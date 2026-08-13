import pytest
from sqlalchemy import select

from app.auth import hash_password
from app.models import User
from app.repositories import UserRepository

repo = UserRepository()


@pytest.mark.asyncio
async def test_create_and_get_by_username(session):
    user = await repo.create(session, username="alice", hashed_password=hash_password("pw"))
    assert user.id is not None

    found = await repo.get_by_username(session, "alice")
    assert found is not None
    assert found.id == user.id
    assert found.username == "alice"


@pytest.mark.asyncio
async def test_get_by_username_missing_returns_none(session):
    found = await repo.get_by_username(session, "nobody")
    assert found is None


@pytest.mark.asyncio
async def test_get_by_username_matches_other_columns(session):
    await repo.create(session, username="alice", hashed_password=hash_password("pw"))

    found = await repo.get_by_username(session, "alicia")
    assert found is None


@pytest.mark.asyncio
async def test_create_persists_hashed_password(session):
    hashed = hash_password("secret123")
    user = await repo.create(session, username="bob", hashed_password=hashed)
    assert user.hashed_password == hashed


@pytest.mark.asyncio
async def test_create_persists_row_in_db(session):
    await repo.create(session, username="carol", hashed_password=hash_password("pw"))
    result = await session.execute(select(User).where(User.username == "carol"))
    assert result.scalar_one_or_none() is not None
