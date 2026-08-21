import pytest
from sqlalchemy import select

from app.models import User
from app.repositories import UserRepository
from app.services import (
    InvalidCredentialsError,
    InvalidInviteError,
    UsernameTakenError,
    login_user,
    register_user,
)
from tests.conftest import INVITE_CODE

repo = UserRepository()


@pytest.mark.asyncio
async def test_register_user_success(session):
    user = await register_user(session, "alice", "password123", INVITE_CODE, users_repo=repo)
    assert user.username == "alice"
    assert user.id is not None


@pytest.mark.asyncio
async def test_register_user_invalid_invite(session):
    with pytest.raises(InvalidInviteError):
        await register_user(session, "alice", "password123", "wrong-code", users_repo=repo)


@pytest.mark.asyncio
async def test_register_user_duplicate_username(session):
    await register_user(session, "bob", "password123", INVITE_CODE, users_repo=repo)
    with pytest.raises(UsernameTakenError):
        await register_user(session, "bob", "otherpass456", INVITE_CODE, users_repo=repo)


@pytest.mark.asyncio
async def test_register_user_hashes_password(session):
    await register_user(session, "carol", "secret123", INVITE_CODE, users_repo=repo)
    result = await session.execute(select(User).where(User.username == "carol"))
    user = result.scalar_one()
    assert user.hashed_password != "secret123"


@pytest.mark.asyncio
async def test_login_success_returns_user(session):
    await register_user(session, "dave", "correctpass", INVITE_CODE, users_repo=repo)
    user = await login_user(session, "dave", "correctpass", users_repo=repo)
    assert user.username == "dave"


@pytest.mark.asyncio
async def test_login_wrong_password_raises(session):
    await register_user(session, "dave", "correctpass", INVITE_CODE, users_repo=repo)
    with pytest.raises(InvalidCredentialsError):
        await login_user(session, "dave", "wrongpass", users_repo=repo)


@pytest.mark.asyncio
async def test_login_nonexistent_user_raises(session):
    with pytest.raises(InvalidCredentialsError):
        await login_user(session, "nobody", "anything", users_repo=repo)
