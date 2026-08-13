import io
import uuid

import pytest
from PIL import Image as PILImage
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import ImageRepository
from app.services import (
    ImageNotFoundError,
    NotImageOwnerError,
    create_image,
    delete_image,
    list_images,
    update_image_caption,
)

images_repo = ImageRepository()


def _tiny_jpeg() -> bytes:
    buf = io.BytesIO()
    im = PILImage.new("RGB", (1, 1), color="red")
    im.save(buf, format="JPEG")
    return buf.getvalue()


async def _make_user(session: AsyncSession) -> User:
    user = User(username=f"owner-{uuid.uuid4().hex[:8]}", hashed_password="x")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def _make_image(session: AsyncSession, user: User):
    return await create_image(
        session,
        owner_id=user.id,
        file_bytes=_tiny_jpeg(),
        original_name="a.jpg",
        images_repo=images_repo,
    )


@pytest.mark.asyncio
async def test_create_image_returns_image(session):
    user = await _make_user(session)
    image = await create_image(
        session,
        owner_id=user.id,
        file_bytes=_tiny_jpeg(),
        original_name="photo.jpg",
        caption="Hello",
        images_repo=images_repo,
    )
    assert image.id is not None
    assert image.owner_id == user.id
    assert image.caption == "Hello"


@pytest.mark.asyncio
async def test_list_images(session):
    user = await _make_user(session)
    await _make_image(session, user)
    await _make_image(session, user)
    images = await list_images(session, images_repo=images_repo)
    assert len(images) == 2


@pytest.mark.asyncio
async def test_update_caption_success(session):
    user = await _make_user(session)
    image = await _make_image(session, user)
    updated = await update_image_caption(
        session, image.id, "New", user_id=user.id, images_repo=images_repo
    )
    assert updated.caption == "New"


@pytest.mark.asyncio
async def test_update_caption_not_owner_raises(session):
    user = await _make_user(session)
    other = await _make_user(session)
    image = await _make_image(session, user)
    with pytest.raises(NotImageOwnerError):
        await update_image_caption(
            session, image.id, "x", user_id=other.id, images_repo=images_repo
        )


@pytest.mark.asyncio
async def test_update_caption_missing_raises(session):
    user = await _make_user(session)
    with pytest.raises(ImageNotFoundError):
        await update_image_caption(
            session, uuid.uuid4(), "x", user_id=user.id, images_repo=images_repo
        )


@pytest.mark.asyncio
async def test_delete_own_image_success(session):
    user = await _make_user(session)
    image = await _make_image(session, user)
    await delete_image(session, image.id, user_id=user.id, images_repo=images_repo)
    found = await images_repo.get_by_id(session, image.id)
    assert found is None


@pytest.mark.asyncio
async def test_delete_other_users_image_raises(session):
    user = await _make_user(session)
    other = await _make_user(session)
    image = await _make_image(session, user)
    with pytest.raises(NotImageOwnerError):
        await delete_image(session, image.id, user_id=other.id, images_repo=images_repo)
