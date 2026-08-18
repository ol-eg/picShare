import pytest
from starlette.requests import Request
from starlette.types import Scope

from app.auth import (
    SESSION_COOKIE,
    create_session_cookie,
    read_session_cookie,
)
from app.repositories import UserRepository
from app.services import register_user

INVITE_CODE = "test-invite-42"


def _make_request(cookie: str | None = None) -> Request:
    scope: Scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    if cookie is not None:
        scope["headers"].append(
            (
                b"cookie",
                f"{SESSION_COOKIE}={cookie}".encode(),
            )
        )

    async def receive() -> dict:
        return {}

    return Request(scope, receive=receive)


@pytest.mark.asyncio
async def test_create_session_cookie_is_signed_jwt(session):
    cookie = create_session_cookie("some-user-id")
    assert isinstance(cookie, str)
    assert cookie.count(".") == 2  # JWT shape: header.payload.signature


@pytest.mark.asyncio
async def test_read_session_cookie_returns_user(session):
    user = await register_user(
        session, "cookieuser", "password123", INVITE_CODE, users_repo=UserRepository()
    )
    cookie = create_session_cookie(str(user.id))
    request = _make_request(cookie=cookie)
    result = await read_session_cookie(request, db=session)
    assert result is not None
    assert result.id == user.id


@pytest.mark.asyncio
async def test_read_session_cookie_missing_returns_none(session):
    request = _make_request(cookie=None)
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_invalid_token_returns_none(session):
    request = _make_request(cookie="not-a-valid-jwt")
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_wrong_signature_returns_none(session):
    cookie = create_session_cookie("some-user-id")
    request = _make_request(cookie=cookie + "tampered")
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_unknown_user_returns_none(session):
    cookie = create_session_cookie("00000000-0000-0000-0000-000000000000")
    request = _make_request(cookie=cookie)
    result = await read_session_cookie(request, db=session)
    assert result is None
