import uuid
from datetime import datetime

from pydantic import BaseModel, constr


# ── Auth ──

class UserRegister(BaseModel):
    username: constr(min_length=3, max_length=64)
    password: constr(min_length=6, max_length=128)
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