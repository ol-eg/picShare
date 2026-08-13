from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, verify_password
from app.database import settings
from app.models import User
from app.repositories import UserRepository


class InvalidInviteError(Exception):
    pass


class UsernameTakenError(Exception):
    pass


class InvalidCredentialsError(Exception):
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
