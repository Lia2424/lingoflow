"""
Integration tests for /api/auth/* endpoints.
Requires a running Postgres instance (use: pytest tests/integration/).
"""

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "test@lingoflow.com",
    "username": "testuser",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "es",
}


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == REGISTER_PAYLOAD["email"]
    assert body["user"]["username"] == REGISTER_PAYLOAD["username"]
    assert "hashed_password" not in body["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@lingoflow.com", "password": "whatever"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_token(client: AsyncClient) -> None:
    register_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    original_refresh = register_response.json()["refresh_token"]

    refresh_response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": original_refresh},
    )

    assert refresh_response.status_code == 200
    body = refresh_response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    # A new refresh token is issued — the old one is not reused
    assert body["refresh_token"] != original_refresh


@pytest.mark.asyncio
async def test_refresh_with_invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_without_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/api/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_route_with_valid_token(client: AsyncClient) -> None:
    register_response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    token = register_response.json()["access_token"]

    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]
