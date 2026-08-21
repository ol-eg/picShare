import pytest
from bs4 import BeautifulSoup
from starlette.requests import Request
from starlette.types import Scope

from app.auth import SESSION_COOKIE, read_session_cookie
from tests.conftest import INVITE_CODE


async def _login_soup(client) -> BeautifulSoup:
    resp = await client.get("/login")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    return BeautifulSoup(resp.text, "html.parser")


def _cookie_value(set_cookie_header: str) -> str:
    payload = set_cookie_header.split(";")[0]
    name, value = payload.split("=", 1)
    assert name == SESSION_COOKIE
    return value


def _make_request(cookie: str) -> Request:
    scope: Scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    scope["headers"].append((b"cookie", f"{SESSION_COOKIE}={cookie}".encode()))

    async def receive() -> dict:
        return {}

    return Request(scope, receive=receive)


@pytest.mark.asyncio
async def test_login_page_has_form(client):
    soup = await _login_soup(client)
    form = soup.find("form")
    assert form is not None, "Expected a <form> on the login page"
    assert form.get("method", "").lower() == "post"
    assert form.get("action") == "/login/form"


@pytest.mark.asyncio
async def test_login_form_has_username_field(client):
    soup = await _login_soup(client)
    username = soup.find("input", {"id": "username"})
    assert username is not None, "Expected a username input on the login form"
    assert username.get("name") == "username"


@pytest.mark.asyncio
async def test_login_form_has_password_field(client):
    soup = await _login_soup(client)
    password = soup.find("input", {"id": "password"})
    assert password is not None, "Expected a password input on the login form"
    assert password.get("name") == "password"


@pytest.mark.asyncio
async def test_login_form_has_submit_button(client):
    soup = await _login_soup(client)
    button = soup.find("button", {"type": "submit"})
    assert button is not None, "Expected a submit button on the login form"


@pytest.mark.asyncio
async def test_login_form_success_sets_cookie(client, session):
    await client.post(
        "/register/form",
        data={
            "username": "loguser",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    resp = await client.post(
        "/login/form",
        data={"username": "loguser", "password": "password123"},
    )
    assert resp.status_code == 303
    set_cookie = resp.headers.get("set-cookie")
    assert set_cookie is not None
    assert SESSION_COOKIE in set_cookie


@pytest.mark.asyncio
async def test_login_form_cookie_logs_in_user(client, session):
    await client.post(
        "/register/form",
        data={
            "username": "loguser",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    resp = await client.post(
        "/login/form",
        data={"username": "loguser", "password": "password123"},
    )
    assert resp.status_code == 303
    token = _cookie_value(resp.headers["set-cookie"])
    request = _make_request(token)
    user = await read_session_cookie(request, db=session)
    assert user is not None
    assert user.username == "loguser"


@pytest.mark.asyncio
async def test_login_form_bad_password_renders_error(client):
    await client.post(
        "/register/form",
        data={
            "username": "loguser",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    resp = await client.post(
        "/login/form",
        data={"username": "loguser", "password": "wrongpass"},
    )
    assert resp.status_code == 400
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Invalid credentials" in soup.get_text()
    assert "set-cookie" not in resp.headers
