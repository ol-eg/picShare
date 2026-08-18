import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, settings
from app.models import User
from app.repositories import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"])
security = HTTPBearer()
SESSION_COOKIE = "picshare_session"


def create_session_cookie(user_id: str) -> str:
    return create_token(user_id)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: str) -> str:
    return jwt.encode({"sub": user_id}, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials)
    try:
        parsed_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user = await UserRepository().get_by_id(db, parsed_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user


async def get_current_user_from_cookie(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User | None:
    return await read_session_cookie(request, db)


async def read_session_cookie(request: Request, db: AsyncSession) -> User | None:
    cookie = request.cookies.get(SESSION_COOKIE)
    if not cookie:
        return None
    try:
        payload = jwt.decode(cookie, settings.secret_key, algorithms=["HS256"])
        parsed_id = uuid.UUID(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
    user = await UserRepository().get_by_id(db, parsed_id)
    if not user:
        return None
    return user
