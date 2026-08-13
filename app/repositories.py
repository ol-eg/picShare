import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Image, User


class UserRepository:
    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


class ImageRepository:
    async def get_by_id(self, db: AsyncSession, image_id: uuid.UUID) -> Image | None:
        result = await db.execute(select(Image).where(Image.id == image_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        db: AsyncSession,
        owner_id: uuid.UUID,
        filename: str,
        original_name: str,
        caption: str | None = None,
    ) -> Image:
        image = Image(
            filename=filename,
            original_name=original_name,
            caption=caption,
            owner_id=owner_id,
        )
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image

    async def list_all(self, db: AsyncSession) -> list[Image]:
        result = await db.execute(select(Image).order_by(Image.uploaded_at.desc()))
        return list(result.scalars().all())

    async def update_caption(self, db: AsyncSession, image: Image, caption: str) -> Image:
        image.caption = caption
        await db.commit()
        await db.refresh(image)
        return image

    async def delete(self, db: AsyncSession, image: Image) -> None:
        await db.delete(image)
        await db.commit()
