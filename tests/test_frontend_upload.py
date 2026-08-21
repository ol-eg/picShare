import io

import pytest
from bs4 import BeautifulSoup
from PIL import Image


def _tiny_jpeg() -> bytes:
    buf = io.BytesIO()
    im = Image.new("RGB", (1, 1), color="red")
    im.save(buf, format="JPEG")
    return buf.getvalue()


TINY_JPEG = _tiny_jpeg()


@pytest.mark.asyncio
async def test_upload_entry_point_hidden_for_anonymous(client):
    resp = await client.get("/")
    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.find("a", href="/upload") is None


@pytest.mark.asyncio
async def test_upload_entry_point_visible_for_logged_in(session_client):
    resp = await session_client.get("/")
    soup = BeautifulSoup(resp.text, "html.parser")
    assert soup.find("a", href="/upload") is not None


@pytest.mark.asyncio
async def test_upload_page_redirects_anonymous_to_login(client):
    resp = await client.get("/upload")
    assert resp.status_code in (302, 303)
    assert resp.headers["location"].startswith("/login")


@pytest.mark.asyncio
async def test_upload_page_for_logged_in_renders_form(session_client):
    resp = await session_client.get("/upload")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    form = soup.find("form", attrs={"enctype": "multipart/form-data"})
    assert form is not None
    assert form.find("input", attrs={"type": "file"}) is not None
    assert "Upload" in soup.get_text()


@pytest.mark.asyncio
async def test_upload_submit_logged_in_redirects_and_shows_in_gallery(session_client):
    resp = await session_client.post(
        "/upload",
        files={"file": ("beach.jpg", TINY_JPEG, "image/jpeg")},
        data={"caption": "A beach"},
    )
    assert resp.status_code in (302, 303)
    assert resp.headers["location"] == "/"

    resp = await session_client.get("/")
    assert resp.status_code == 200
    soup = BeautifulSoup(resp.text, "html.parser")
    assert "A beach" in soup.get_text()


@pytest.mark.asyncio
async def test_upload_submit_anonymous_redirects_to_login(client):
    resp = await client.post(
        "/upload",
        files={"file": ("secret.jpg", TINY_JPEG, "image/jpeg")},
    )
    assert resp.status_code in (302, 303)
    assert resp.headers["location"].startswith("/login")
