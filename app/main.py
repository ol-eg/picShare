from pathlib import Path

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import create_token, get_current_user
from app.database import get_db, settings
from app.image_utils import save_upload
from app.models import Image, User
from app.schemas import ImageOut, ImageUpdate, TokenResponse, UserOut, UserRegister
from app.services import (
    InvalidCredentialsError,
    InvalidInviteError,
    UsernameTakenError,
    login_user,
    register_user,
)

app = FastAPI(title="picShare", redoc_url=None)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# ── Frontend ──


@app.get("/", include_in_schema=False)
async def homepage(request: Request):
    return templates.TemplateResponse(request, "home.html")


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


# ── Static files (serving images + local redoc bundle) ──

app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=settings.thumb_dir), name="thumbnails")
app.mount(
    "/static/redoc",
    StaticFiles(directory=Path(__file__).parent / "static" / "redoc_assets"),
    name="redoc_static",
)


# ── Local ReDoc (avoid CDN dependency) ──

REDOC_HTML = (
    "<!DOCTYPE html>\n"
    "<html>\n"
    "<head>\n"
    "<title>picShare - ReDoc</title>\n"
    '<meta charset="utf-8"/>\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<style>body {{ margin: 0; padding: 0; }}</style>\n"
    "</head>\n"
    "<body>\n"
    "<noscript>ReDoc requires Javascript to function. "
    "Please enable it to browse the documentation.</noscript>\n"
    '<redoc spec-url="/openapi.json"></redoc>\n'
    '<script src="/static/redoc/redoc.standalone.js"></script>\n'
    "</body>\n"
    "</html>"
)


@app.get("/redoc", include_in_schema=False)
async def redoc():
    return Response(content=REDOC_HTML, media_type="text/html")


# ── Auth ──


@app.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, body.username, body.password, body.invite_code or "")
    except InvalidInviteError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid invite code")
    except UsernameTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username taken")
    return TokenResponse(access_token=create_token(str(user.id)))


@app.post("/register/form", include_in_schema=False)
async def register_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    invite_code: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    try:
        await register_user(db, username, password, invite_code)
    except InvalidInviteError:
        return templates.TemplateResponse(
            request, "register.html", status_code=400, context={"error": "Invalid invite code"}
        )
    except UsernameTakenError:
        return templates.TemplateResponse(
            request, "register.html", status_code=400, context={"error": "Username taken"}
        )
    return RedirectResponse("/", status_code=303)


@app.post("/login", response_model=TokenResponse)
async def login(body: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await login_user(db, body.username, body.password)
    except InvalidCredentialsError:
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
    image = Image(
        filename=filename,
        original_name=file.filename or "",
        caption=caption,
        owner_id=user.id,
    )
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
