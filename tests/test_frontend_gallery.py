import pytest
from bs4 import BeautifulSoup
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.main import app
from app.models import Image, User

INVITE_CODE = "test-invite-42"


@pytest.mark.asyncio
async def test_home_logged_in_shows_image_thumbnails(client, session):
    await client.post(
        "/register/form",
        data={
            "username": "gallery",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )

    user = (await session.execute(select(User).where(User.username == "gallery"))).scalar_one()

    session.add(
        Image(
            filename="abc.jpg",
            original_name="beach.jpg",
            caption="Sunset",
            owner_id=user.id,
        )
    )
    await session.commit()

    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    img = soup.find("img", src="/thumbnails/abc.jpg")
    assert img is not None, "Expected a thumbnail for the uploaded image on the homepage"
    assert "Sunset" in soup.get_text()


@pytest.mark.asyncio
async def test_home_logged_in_with_no_images_shows_empty_state_cta(client):
    await client.post(
        "/register/form",
        data={
            "username": "emptystate",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    resp = await client.get("/")
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
async def test_home_anonymous_hides_gallery_even_with_images(client, session):
    await client.post(
        "/register/form",
        data={
            "username": "seedonly",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    user = (await session.execute(select(User).where(User.username == "seedonly"))).scalar_one()
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
async def test_home_after_logout_shows_only_login_and_register(client):
    await client.post(
        "/register/form",
        data={
            "username": "postlogout",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    await client.post("/logout")

    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "Log in" in soup.get_text()
    assert "Gallery" not in soup.get_text()
