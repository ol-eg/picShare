import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/register", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/register", json={"username": "bob", "password": "password123"})
    resp = await client.post("/register", json={"username": "bob", "password": "otherpass456"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/register", json={"username": "carol", "password": "mypassword"})
    resp = await client.post("/login", json={"username": "carol", "password": "mypassword"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/register", json={"username": "dave", "password": "correctpass"})
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