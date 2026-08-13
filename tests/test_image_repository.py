import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Image, User
from app.repositories import ImageRepository


async def _make_user(session: AsyncSession) -> User:
    user = User(username="owner", hashed_password="x")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


repo = ImageRepository()


@pytest.mark.asyncio
async def test_create_image(session):
    user = await _make_user(session)
    image = await repo.create(
        session,
        owner_id=user.id,
        filename="abc.jpg",
        original_name="photo.jpg",
        caption="Hello",
    )
    assert image.id is not None
    assert image.owner_id == user.id
    assert image.caption == "Hello"


@pytest.mark.asyncio
async def test_get_by_id(session):
    user = await _make_user(session)
    image = await repo.create(session, owner_id=user.id, filename="a.jpg", original_name="a.jpg")
    found = await repo.get_by_id(session, image.id)
    assert found is not None
    assert found.id == image.id


@pytest.mark.asyncio
async def test_get_by_id_missing_returns_none(session):
    found = await repo.get_by_id(session, uuid.uuid4())
    assert found is None


@pytest.mark.asyncio
async def test_list_all_orders_desc(session):
    user = await _make_user(session)
    await repo.create(session, owner_id=user.id, filename="a.jpg", original_name="a.jpg")
    await repo.create(session, owner_id=user.id, filename="b.jpg", original_name="b.jpg")
    images = await repo.list_all(session)
    assert len(images) == 2


@pytest.mark.asyncio
async def test_update_caption(session):
    user = await _make_user(session)
    image = await repo.create(session, owner_id=user.id, filename="a.jpg", original_name="a.jpg")
    updated = await repo.update_caption(session, image, "New caption")
    assert updated.caption == "New caption"

    fresh = await repo.get_by_id(session, image.id)
    assert fresh.caption == "New caption"


@pytest.mark.asyncio
async def test_delete_image(session):
    user = await _make_user(session)
    image = await repo.create(session, owner_id=user.id, filename="a.jpg", original_name="a.jpg")
    await repo.delete(session, image)
    result = await session.execute(select(Image).where(Image.id == image.id))
    assert result.scalar_one_or_none() is None
