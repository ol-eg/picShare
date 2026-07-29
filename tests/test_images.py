import io

import pytest
from PIL import Image


def _tiny_jpeg() -> bytes:
    buf = io.BytesIO()
    im = Image.new("RGB", (1, 1), color="red")
    im.save(buf, format="JPEG")
    return buf.getvalue()


TINY_JPEG = _tiny_jpeg()


@pytest.mark.asyncio
async def test_upload_image(client, auth_headers):
    resp = await client.post(
        "/images",
        files={"file": ("test.jpg", TINY_JPEG, "image/jpeg")},
        data={"caption": "A test image"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["caption"] == "A test image"
    assert "id" in data
    assert "filename" in data
    assert data["original_name"] == "test.jpg"


@pytest.mark.asyncio
async def test_upload_image_without_auth(client):
    resp = await client.post(
        "/images",
        files={"file": ("test.jpg", TINY_JPEG, "image/jpeg")},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_images(client, auth_headers):
    await client.post(
        "/images",
        files={"file": ("img1.jpg", TINY_JPEG, "image/jpeg")},
        data={"caption": "First"},
        headers=auth_headers,
    )
    await client.post(
        "/images",
        files={"file": ("img2.jpg", TINY_JPEG, "image/jpeg")},
        data={"caption": "Second"},
        headers=auth_headers,
    )
    resp = await client.get("/images")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_image_caption(client, auth_headers):
    upload = await client.post(
        "/images",
        files={"file": ("update.jpg", TINY_JPEG, "image/jpeg")},
        data={"caption": "Original"},
        headers=auth_headers,
    )
    image_id = upload.json()["id"]

    resp = await client.patch(
        f"/images/{image_id}",
        json={"caption": "Updated caption"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["caption"] == "Updated caption"


@pytest.mark.asyncio
async def test_delete_image(client, auth_headers):
    upload = await client.post(
        "/images",
        files={"file": ("delete.jpg", TINY_JPEG, "image/jpeg")},
        headers=auth_headers,
    )
    image_id = upload.json()["id"]

    resp = await client.delete(f"/images/{image_id}", headers=auth_headers)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_other_users_image(client, auth_headers):
    upload = await client.post(
        "/images",
        files={"file": ("mine.jpg", TINY_JPEG, "image/jpeg")},
        headers=auth_headers,
    )
    image_id = upload.json()["id"]

    resp = await client.post("/register", json={"username": "other", "password": "secret123"})
    other_token = resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = await client.delete(f"/images/{image_id}", headers=other_headers)
    assert resp.status_code == 403