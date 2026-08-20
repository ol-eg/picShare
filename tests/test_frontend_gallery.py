import pytest
from bs4 import BeautifulSoup
from sqlalchemy import select

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
async def test_home_with_no_images_shows_empty_state(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "No photos yet" in soup.get_text()
