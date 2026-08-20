from pathlib import Path

from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.models import Image, User

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def render_home(
    request: Request,
    user: User | None = None,
    images: list[Image] | None = None,
) -> Response:
    return templates.TemplateResponse(
        request, "home.html", context={"user": user, "images": images or []}
    )


def render_register(request: Request) -> Response:
    return templates.TemplateResponse(request, "register.html")


def render_login(request: Request) -> Response:
    return templates.TemplateResponse(request, "login.html")


def render_login_error(request: Request, error: str) -> Response:
    return templates.TemplateResponse(
        request, "login.html", status_code=400, context={"error": error}
    )


def render_register_error(request: Request, error: str) -> Response:
    return templates.TemplateResponse(
        request, "register.html", status_code=400, context={"error": error}
    )


def redirect_home() -> Response:
    return RedirectResponse("/", status_code=303)
