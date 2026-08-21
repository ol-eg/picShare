import pytest

from app.auth import SESSION_COOKIE


@pytest.mark.asyncio
async def test_logout_clears_session_cookie(session_client):
    assert session_client.cookies.get(SESSION_COOKIE) is not None

    resp = await session_client.post("/logout")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"
    assert session_client.cookies.get(SESSION_COOKIE) is None


@pytest.mark.asyncio
async def test_logout_without_session_still_redirects(client):
    resp = await client.post("/logout")
    assert resp.status_code == 303
    assert resp.headers["location"] == "/"
