import uuid
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
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import SESSION_COOKIE, create_token, get_current_user, get_current_user_from_cookie
from app.database import get_db, settings
from app.models import User
from app.schemas import ImageOut, ImageUpdate, TokenResponse, UserOut, UserRegister
from app.services import (
    ImageNotFoundError,
    InvalidCredentialsError,
    InvalidInviteError,
    NotImageOwnerError,
    UsernameTakenError,
    create_image,
    login_user,
    register_user,
    update_image_caption,
)
from app.services import (
    delete_image as delete_image_service,
)
from app.services import (
    list_images as list_images_service,
)
from app.views import (
    redirect_home,
    render_home,
    render_login,
    render_login_error,
    render_register,
    render_register_error,
)

app = FastAPI(title="picShare", redoc_url=None)


# ── Frontend ──


@app.get("/", include_in_schema=False)
async def homepage(
    request: Request,
    user: User | None = Depends(get_current_user_from_cookie),
):
    return render_home(request, user=user)


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return render_register(request)


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return render_login(request)


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
        user = await register_user(db, username, password, invite_code)
    except InvalidInviteError:
        return render_register_error(request, "Invalid invite code")
    except UsernameTakenError:
        return render_register_error(request, "Username taken")
    response = redirect_home()
    response.set_cookie(
        SESSION_COOKIE,
        create_token(str(user.id)),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return response


@app.post("/login", response_model=TokenResponse)
async def login(body: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await login_user(db, body.username, body.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")
    return TokenResponse(access_token=create_token(str(user.id)))


@app.post("/login/form", include_in_schema=False)
async def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await login_user(db, username, password)
    except InvalidCredentialsError:
        return render_login_error(request, "Invalid credentials")
    response = redirect_home()
    response.set_cookie(
        SESSION_COOKIE,
        create_token(str(user.id)),
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
    )
    return response


@app.post("/logout", include_in_schema=False)
async def logout():
    response = redirect_home()
    response.delete_cookie(
        SESSION_COOKIE, httponly=True, samesite="lax", secure=settings.cookie_secure
    )
    return response


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
    image = await create_image(
        db,
        owner_id=user.id,
        file_bytes=contents,
        original_name=file.filename or "",
        caption=caption,
    )
    return image


@app.get("/images", response_model=list[ImageOut])
async def list_images(db: AsyncSession = Depends(get_db)):
    return await list_images_service(db)


@app.patch("/images/{image_id}", response_model=ImageOut)
async def update_image(
    image_id: uuid.UUID,
    body: ImageUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        image = await update_image_caption(db, image_id, body.caption, user_id=user.id)
    except ImageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except NotImageOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return image


@app.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await delete_image_service(db, image_id, user_id=user.id)
    except ImageNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except NotImageOwnerError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
