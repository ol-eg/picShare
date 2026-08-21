import pytest
from bs4 import BeautifulSoup
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models import Image, User
from tests.conftest import SESSION_USERNAME


@pytest.mark.asyncio
async def test_home_logged_in_shows_image_thumbnails(session_client, session):
    user = (
        await session.execute(select(User).where(User.username == SESSION_USERNAME))
    ).scalar_one()

    session.add(
        Image(
            filename="abc.jpg",
            original_name="beach.jpg",
            caption="Sunset",
            owner_id=user.id,
        )
    )
    await session.commit()

    resp = await session_client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    img = soup.find("img", src="/thumbnails/abc.jpg")
    assert img is not None, "Expected a thumbnail for the uploaded image on the homepage"
    assert "Sunset" in soup.get_text()


@pytest.mark.asyncio
async def test_home_logged_in_with_no_images_shows_empty_state_cta(session_client):
    resp = await session_client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "be the first to share one" in soup.get_text()


@pytest.mark.asyncio
async def test_home_anonymous_shows_only_login_and_register(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Log in" in soup.get_text()
    assert "Register" in soup.get_text()
    assert "Gallery" not in soup.get_text()
    assert "No photos" not in soup.get_text()


@pytest.mark.asyncio
async def test_home_anonymous_hides_gallery_even_with_images(session_client, session):
    user = (
        await session.execute(select(User).where(User.username == SESSION_USERNAME))
    ).scalar_one()
    session.add(
        Image(
            filename="seed.jpg",
            original_name="seed.jpg",
            caption="Hidden",
            owner_id=user.id,
        )
    )
    await session.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as anon:
        resp = await anon.get("/")
        assert resp.status_code == 200
        soup = BeautifulSoup(resp.text, "html.parser")
        assert soup.find("img") is None
        assert "Gallery" not in soup.get_text()


@pytest.mark.asyncio
async def test_home_after_logout_shows_only_login_and_register(session_client):
    await session_client.post("/logout")

    resp = await session_client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Log in" in soup.get_text()
    assert "Gallery" not in soup.get_text()
