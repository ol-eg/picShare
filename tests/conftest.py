import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import settings, get_db
from app.main import app
from app.models import Base

TEST_DB_HOST = os.environ.get("PICSHARE_TEST_DB_HOST", "localhost")
TEST_DB_URL = f"postgresql+asyncpg://picshare:picshare@{TEST_DB_HOST}:5432/picshare_test"


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
async def auth_headers(client: AsyncClient) -> dict:
    resp = await client.post("/register", json={"username": "testuser", "password": "secret123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}