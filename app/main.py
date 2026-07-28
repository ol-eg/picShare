from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import hash_password, verify_password, create_token, get_current_user
from app.database import settings, get_db
from app.dependencies import get_db, get_current_user
from app.image_utils import save_upload
from app.models import User, Image
from app.schemas import UserRegister, TokenResponse, UserOut, ImageOut, ImageUpdate

app = FastAPI(title="picShare")


# ── Static files (serving images) ──

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=settings.thumb_dir), name="thumbnails")


# ── Auth ──

@app.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
    user = User(username=body.username, hashed_password=hash_password(body.password))
    db.add(user)
    await db.commit()
    return TokenResponse(access_token=create_token(str(user.id)))


@app.post("/login", response_model=TokenResponse)
async def login(body: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    return TokenResponse(access_token=create_token(str(user.id)))


# ── Users ──

@app.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


# ── Images ──

@app.post("/images", response_model=ImageOut, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    caption: str = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contents = await file.read()
    filename = save_upload(contents, file.filename or "image.jpg")
    image = Image(filename=filename, original_name=file.filename or "", caption=caption, owner_id=user.id)
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return image


@app.get("/images", response_model=list[ImageOut])
async def list_images(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Image).order_by(Image.uploaded_at.desc()))
    return result.scalars().all()


@app.patch("/images/{image_id}", response_model=ImageOut)
async def update_image(
    image_id: str,
    body: ImageUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if image.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if body.caption is not None:
        image.caption = body.caption
    await db.commit()
    await db.refresh(image)
    return image


@app.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if image.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await db.delete(image)
    await db.commit()