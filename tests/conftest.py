import io
import os

import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.requests import Request
from starlette.types import Scope

from app.auth import SESSION_COOKIE
from app.database import get_db
from app.main import app
from app.models import Base

TEST_DB_HOST = os.environ.get("PICSHARE_TEST_DB_HOST", "localhost")
TEST_DB_URL = f"postgresql+asyncpg://picshare:picshare@{TEST_DB_HOST}:5432/picshare_test"

INVITE_CODE = "test-invite-42"
SESSION_USERNAME = "session_user"
SESSION_PASSWORD = "password123"


def make_session_request(cookie: str | None = None) -> Request:
    scope: Scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    if cookie is not None:
        scope["headers"].append((b"cookie", f"{SESSION_COOKIE}={cookie}".encode()))

    async def receive() -> dict:
        return {}

    return Request(scope, receive=receive)


def session_cookie_value(set_cookie_header: str) -> str:
    payload = set_cookie_header.split(";")[0]
    name, value = payload.split("=", 1)
    assert name == SESSION_COOKIE
    return value


def tiny_jpeg() -> bytes:
    buf = io.BytesIO()
    im = Image.new("RGB", (1, 1), color="red")
    im.save(buf, format="JPEG")
    return buf.getvalue()


TINY_JPEG = tiny_jpeg()


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def session(engine):
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
        await session.rollback()
    async with SessionLocal() as cleanup:
        for table in reversed(Base.metadata.sorted_tables):
            await cleanup.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
        await cleanup.commit()


@pytest.fixture
async def client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def session_client(client: AsyncClient) -> AsyncClient:
    resp = await client.post(
        "/register/form",
        data={
            "username": SESSION_USERNAME,
            "password": SESSION_PASSWORD,
            "invite_code": INVITE_CODE,
        },
    )
    assert resp.status_code == 303
    return client


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict:
    resp = await client.post(
        "/register",
        json={"username": "testuser", "password": "secret123", "invite_code": INVITE_CODE},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
