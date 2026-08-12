import pytest
from bs4 import BeautifulSoup


async def _register_soup(client) -> BeautifulSoup:
    resp = await client.get("/register")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    return BeautifulSoup(resp.text, "html.parser")


@pytest.mark.asyncio
async def test_register_page_has_correct_title(client):
    soup = await _register_soup(client)
    assert soup.title is not None
    assert soup.title.string == "picShare"


@pytest.mark.asyncio
async def test_register_page_returns_html_form(client):
    soup = await _register_soup(client)
    form = soup.find("form")
    assert form is not None, "Expected a <form> on the register page"


@pytest.mark.asyncio
async def test_register_form_has_username_field(client):
    soup = await _register_soup(client)
    username = soup.find("input", {"id": "username"})
    assert username is not None, "Expected a username input field on the register form"
    assert username.get("name") == "username"


@pytest.mark.asyncio
async def test_register_form_has_password_field(client):
    soup = await _register_soup(client)
    password = soup.find("input", {"id": "password"})
    assert password is not None, "Expected a password input field on the register form"
    assert password.get("name") == "password"


@pytest.mark.asyncio
async def test_register_form_has_invite_code_field(client):
    soup = await _register_soup(client)
    invite = soup.find("input", {"id": "invite_code"})
    assert invite is not None, "Expected an invite code input field on the register form"
    assert invite.get("name") == "invite_code"


@pytest.mark.asyncio
async def test_register_form_has_submit_button(client):
    soup = await _register_soup(client)
    button = soup.find("button", {"type": "submit"})
    assert button is not None, "Expected a submit button on the register form"


@pytest.mark.asyncio
async def test_register_form_submits_to_register(client):
    soup = await _register_soup(client)
    form = soup.find("form")
    assert form.get("method", "").lower() == "post"
    assert form.get("action") == "/register/form"


@pytest.mark.asyncio
async def test_register_form_submission_creates_user(client):
    resp = await client.post(
        "/register/form",
        data={"username": "carol", "password": "password123", "invite_code": "test-invite-42"},
    )
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"


@pytest.mark.asyncio
async def test_register_form_bad_invite_renders_error(client):
    resp = await client.post(
        "/register/form",
        data={"username": "carol", "password": "password123", "invite_code": "wrong-code"},
    )
    assert resp.status_code == 400
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Invalid invite code" in soup.get_text()


@pytest.mark.asyncio
async def test_register_form_duplicate_username_renders_error(client):
    await client.post(
        "/register/form",
        data={"username": "carol", "password": "password123", "invite_code": "test-invite-42"},
    )
    resp = await client.post(
        "/register/form",
        data={"username": "carol", "password": "password123", "invite_code": "test-invite-42"},
    )
    assert resp.status_code == 400
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Username taken" in soup.get_text()
