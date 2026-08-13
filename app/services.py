import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, verify_password
from app.database import settings
from app.image_utils import save_upload
from app.models import Image, User
from app.repositories import ImageRepository, UserRepository


class InvalidInviteError(Exception):
    pass


class UsernameTakenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class ImageNotFoundError(Exception):
    pass


class NotImageOwnerError(Exception):
    pass


async def register_user(
    db: AsyncSession,
    username: str,
    password: str,
    invite_code: str,
    users_repo: UserRepository | None = None,
) -> User:
    repo = users_repo or UserRepository()
    if settings.invite_code and invite_code != settings.invite_code:
        raise InvalidInviteError()
    if await repo.get_by_username(db, username):
        raise UsernameTakenError()
    return await repo.create(db, username, hash_password(password))


async def login_user(
    db: AsyncSession,
    username: str,
    password: str,
    users_repo: UserRepository | None = None,
) -> User:
    repo = users_repo or UserRepository()
    user = await repo.get_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsError()
    return user


async def create_image(
    db: AsyncSession,
    owner_id: uuid.UUID,
    file_bytes: bytes,
    original_name: str,
    caption: str | None = None,
    images_repo: ImageRepository | None = None,
) -> Image:
    repo = images_repo or ImageRepository()
    filename = save_upload(file_bytes, original_name)
    return await repo.create(
        db, owner_id=owner_id, filename=filename, original_name=original_name, caption=caption
    )


async def list_images(
    db: AsyncSession,
    images_repo: ImageRepository | None = None,
) -> list[Image]:
    repo = images_repo or ImageRepository()
    return await repo.list_all(db)


async def update_image_caption(
    db: AsyncSession,
    image_id: uuid.UUID,
    caption: str | None,
    user_id: uuid.UUID,
    images_repo: ImageRepository | None = None,
) -> Image:
    repo = images_repo or ImageRepository()
    image = await repo.get_by_id(db, image_id)
    if image is None:
        raise ImageNotFoundError()
    if image.owner_id != user_id:
        raise NotImageOwnerError()
    if caption is None:
        return image
    return await repo.update_caption(db, image, caption)


async def delete_image(
    db: AsyncSession,
    image_id: uuid.UUID,
    user_id: uuid.UUID,
    images_repo: ImageRepository | None = None,
) -> None:
    repo = images_repo or ImageRepository()
    image = await repo.get_by_id(db, image_id)
    if image is None:
        raise ImageNotFoundError()
    if image.owner_id != user_id:
        raise NotImageOwnerError()
    await repo.delete(db, image)
