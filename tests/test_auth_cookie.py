import pytest

from app.auth import create_session_cookie, read_session_cookie
from app.repositories import UserRepository
from app.services import register_user
from tests.conftest import INVITE_CODE, make_session_request


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
    request = make_session_request(cookie=cookie)
    result = await read_session_cookie(request, db=session)
    assert result is not None
    assert result.id == user.id


@pytest.mark.asyncio
async def test_read_session_cookie_missing_returns_none(session):
    request = make_session_request(cookie=None)
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_invalid_token_returns_none(session):
    request = make_session_request(cookie="not-a-valid-jwt")
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_wrong_signature_returns_none(session):
    cookie = create_session_cookie("some-user-id")
    request = make_session_request(cookie=cookie + "tampered")
    result = await read_session_cookie(request, db=session)
    assert result is None


@pytest.mark.asyncio
async def test_read_session_cookie_unknown_user_returns_none(session):
    cookie = create_session_cookie("00000000-0000-0000-0000-000000000000")
    request = make_session_request(cookie=cookie)
    result = await read_session_cookie(request, db=session)
    assert result is None
