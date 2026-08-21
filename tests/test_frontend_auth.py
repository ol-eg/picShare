import pytest
from bs4 import BeautifulSoup

from app.auth import SESSION_COOKIE, read_session_cookie
from tests.conftest import INVITE_CODE, make_session_request, session_cookie_value


@pytest.mark.asyncio
async def test_register_form_sets_session_cookie(client):
    resp = await client.post(
        "/register/form",
        data={
            "username": "alice",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    assert resp.status_code == 303
    set_cookie = resp.headers.get("set-cookie")
    assert set_cookie is not None
    assert SESSION_COOKIE in set_cookie


@pytest.mark.asyncio
async def test_register_form_cookie_logs_in_user(client, session):
    resp = await client.post(
        "/register/form",
        data={
            "username": "bob",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    assert resp.status_code == 303
    token = session_cookie_value(resp.headers["set-cookie"])
    request = make_session_request(token)
    user = await read_session_cookie(request, db=session)
    assert user is not None
    assert user.username == "bob"


@pytest.mark.asyncio
async def test_home_anonymous_shows_log_in_and_register(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    hrefs = [a.get("href") for a in soup.find_all("a")]
    assert "/login" in hrefs
    assert "/register" in hrefs
    assert "/logout" not in hrefs


@pytest.mark.asyncio
async def test_home_logged_in_shows_username_and_logout(client):
    await client.post(
        "/register/form",
        data={
            "username": "homeuser",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "homeuser" in soup.get_text()
    assert "Log out" in soup.get_text()
    logout_form = soup.find("form", {"action": "/logout"})
    assert logout_form is not None
    assert logout_form.get("method", "").lower() == "post"
    hrefs = [a.get("href") for a in soup.find_all("a")]
    assert "/login" not in hrefs
