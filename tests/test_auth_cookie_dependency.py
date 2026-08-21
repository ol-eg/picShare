import pytest
from starlette.requests import Request
from starlette.types import Scope

from app.auth import SESSION_COOKIE, create_session_cookie, get_current_user_from_cookie
from app.repositories import UserRepository
from app.services import register_user
from tests.conftest import INVITE_CODE


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
async def test_cookie_dependency_returns_user(session):
    user = await register_user(
        session, "cookieuser", "password123", INVITE_CODE, users_repo=UserRepository()
    )
    request = _make_request(cookie=create_session_cookie(str(user.id)))
    result = await get_current_user_from_cookie(request, db=session)
    assert result is not None
    assert result.id == user.id


@pytest.mark.asyncio
async def test_cookie_dependency_missing_returns_none(session):
    request = _make_request(cookie=None)
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_cookie_dependency_invalid_cookie_returns_none(session):
    request = _make_request(cookie="garbage")
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_cookie_dependency_unknown_user_returns_none(session):
    request = _make_request(cookie=create_session_cookie("00000000-0000-0000-0000-000000000000"))
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None
