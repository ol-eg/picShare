import pytest

from app.auth import create_session_cookie, get_current_user_from_cookie
from app.repositories import UserRepository
from app.services import register_user
from tests.conftest import INVITE_CODE, make_session_request


@pytest.mark.asyncio
async def test_cookie_dependency_returns_user(session):
    user = await register_user(
        session, "cookieuser", "password123", INVITE_CODE, users_repo=UserRepository()
    )
    request = make_session_request(cookie=create_session_cookie(str(user.id)))
    result = await get_current_user_from_cookie(request, db=session)
    assert result is not None
    assert result.id == user.id


@pytest.mark.asyncio
async def test_cookie_dependency_missing_returns_none(session):
    request = make_session_request(cookie=None)
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_cookie_dependency_invalid_cookie_returns_none(session):
    request = make_session_request(cookie="garbage")
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_cookie_dependency_unknown_user_returns_none(session):
    request = make_session_request(
        cookie=create_session_cookie("00000000-0000-0000-0000-000000000000")
    )
    result = await get_current_user_from_cookie(request, db=session)
    assert result is None
