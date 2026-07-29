import pytest

INVITE_CODE = "test-invite-42"


@pytest.mark.asyncio
async def test_register_requires_invite_code(client):
    resp = await client.post("/register", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post(
        "/register", json={"username": "alice", "password": "password123", "invite_code": INVITE_CODE}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_invalid_invite_code(client):
    resp = await client.post(
        "/register", json={"username": "bob", "password": "password123", "invite_code": "wrong-code"}
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    payload = {"username": "bob", "password": "password123", "invite_code": INVITE_CODE}
    await client.post("/register", json=payload)
    resp = await client.post("/register", json={**payload, "password": "otherpass456"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    payload = {"username": "carol", "password": "mypassword", "invite_code": INVITE_CODE}
    await client.post("/register", json=payload)
    resp = await client.post("/login", json={"username": "carol", "password": "mypassword"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    payload = {"username": "dave", "password": "correctpass", "invite_code": INVITE_CODE}
    await client.post("/register", json=payload)
    resp = await client.post("/login", json={"username": "dave", "password": "wrongpass"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/login", json={"username": "nobody", "password": "anything"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client, auth_headers):
    resp = await client.get("/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert "id" in data


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/me")
    assert resp.status_code == 403