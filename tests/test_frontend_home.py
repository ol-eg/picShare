import pytest
from bs4 import BeautifulSoup


@pytest.mark.asyncio
async def test_homepage_returns_html(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]

    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.title is not None
    assert soup.title.string == "picShare"


@pytest.mark.asyncio
async def test_homepage_has_login_link(client):
    resp = await client.get("/")
    soup = BeautifulSoup(resp.text, "html.parser")
    login = soup.find("a", string="Log in")
    assert login is not None, "Expected a 'Log in' link on the homepage"
    assert login.get("href") is not None


@pytest.mark.asyncio
async def test_homepage_has_register_link(client):
    resp = await client.get("/")
    soup = BeautifulSoup(resp.text, "html.parser")
    register = soup.find("a", string="Register")
    assert register is not None, "Expected a 'Register' link on the homepage"
    assert register.get("href") is not None


@pytest.mark.asyncio
async def test_register_link_loads_page(client):
    resp = await client.get("/register")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


@pytest.mark.asyncio
async def test_login_link_loads_page(client):
    resp = await client.get("/login")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]