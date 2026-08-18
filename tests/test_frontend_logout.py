import pytest

from app.auth import SESSION_COOKIE

INVITE_CODE = "test-invite-42"


@pytest.mark.asyncio
async def test_logout_clears_session_cookie(client):
    resp = await client.post(
        "/register/form",
        data={
            "username": "logoutuser",
            "password": "password123",
            "invite_code": INVITE_CODE,
        },
    )
    assert resp.status_code == 303
    assert client.cookies.get(SESSION_COOKIE) is not None

    resp = await client.post("/logout")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"
    assert client.cookies.get(SESSION_COOKIE) is None


@pytest.mark.asyncio
async def test_logout_without_session_still_redirects(client):
    resp = await client.post("/logout")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"
