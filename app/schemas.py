import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

# ── Auth ──


class UserRegister(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=6, max_length=128)]
    invite_code: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Users ──


class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Images ──


class ImageOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_name: str
    caption: str | None
    uploaded_at: datetime
    owner_id: uuid.UUID

    model_config = {"from_attributes": True}


class ImageUpdate(BaseModel):
    caption: str | None = None
