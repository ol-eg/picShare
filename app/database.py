from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://picshare:picshare@localhost:5432/picshare"
    secret_key: str = "change-me-in-production"
    upload_dir: str = "app/static/uploads"
    thumb_dir: str = "app/static/thumbnails"
    thumbnail_size: tuple[int, int] = (300, 300)
    invite_code: str | None = None
    cookie_secure: bool = True

    model_config = {"env_prefix": "PICSHARE_"}


settings = Settings()

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
