"""
Integration tests for /api/users/me endpoints.
Requires a running Postgres instance (use: pytest tests/integration/).
"""

import pytest
from httpx import AsyncClient

_USER = {
    "email": "user@lingoflow.com",
    "username": "lingouser",
    "password": "supersecret99",
    "native_language": "en",
    "target_language": "es",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _register(client: AsyncClient, payload: dict = _USER) -> dict:
    r = await client.post("/api/auth/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── GET /users/me ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_me_returns_profile(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.get("/api/users/me", headers=_auth(data["access_token"]))

    assert r.status_code == 200
    body = r.json()
    assert body["email"] == _USER["email"]
    assert body["username"] == _USER["username"]
    assert "hashed_password" not in body


@pytest.mark.asyncio
async def test_get_me_without_token_returns_401(client: AsyncClient) -> None:
    r = await client.get("/api/users/me")
    assert r.status_code == 401


# ── PATCH /users/me ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_me_updates_username(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.patch(
        "/api/users/me",
        json={"username": "newname"},
        headers=_auth(data["access_token"]),
    )

    assert r.status_code == 200
    assert r.json()["username"] == "newname"


@pytest.mark.asyncio
async def test_patch_me_updates_target_language_and_cefr(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.patch(
        "/api/users/me",
        json={"target_language": "fr", "cefr_level": "B2"},
        headers=_auth(data["access_token"]),
    )

    assert r.status_code == 200
    body = r.json()
    assert body["target_language"] == "fr"
    assert body["cefr_level"] == "B2"


@pytest.mark.asyncio
async def test_patch_me_ignores_unset_fields(client: AsyncClient) -> None:
    """Omitting a field leaves it unchanged."""
    data = await _register(client)
    r = await client.patch(
        "/api/users/me",
        json={"target_language": "de"},
        headers=_auth(data["access_token"]),
    )

    assert r.status_code == 200
    body = r.json()
    assert body["username"] == _USER["username"]  # unchanged
    assert body["target_language"] == "de"


@pytest.mark.asyncio
async def test_patch_me_duplicate_username_returns_409(client: AsyncClient) -> None:
    """Changing to an already-taken username must return 409, not 500."""
    other = {**_USER, "email": "other@lingoflow.com", "username": "otheruser"}
    await _register(client, other)

    data = await _register(client)
    r = await client.patch(
        "/api/users/me",
        json={"username": "otheruser"},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 409
    assert "taken" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patch_me_username_too_short_returns_422(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.patch(
        "/api/users/me",
        json={"username": "x"},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_patch_me_without_token_returns_401(client: AsyncClient) -> None:
    r = await client.patch("/api/users/me", json={"username": "x"})
    assert r.status_code == 401


# ── POST /users/me/change-password ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_change_password_success(client: AsyncClient) -> None:
    data = await _register(client)
    token = data["access_token"]

    r = await client.post(
        "/api/users/me/change-password",
        json={"current_password": _USER["password"], "new_password": "newpassword123"},
        headers=_auth(token),
    )
    assert r.status_code == 204

    # Old credentials no longer work
    login_old = await client.post(
        "/api/auth/login",
        json={"email": _USER["email"], "password": _USER["password"]},
    )
    assert login_old.status_code == 401

    # New credentials work
    login_new = await client.post(
        "/api/auth/login",
        json={"email": _USER["email"], "password": "newpassword123"},
    )
    assert login_new.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current_returns_400(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.post(
        "/api/users/me/change-password",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 400
    assert "incorrect" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_same_as_current_returns_400(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.post(
        "/api/users/me/change-password",
        json={"current_password": _USER["password"], "new_password": _USER["password"]},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 400
    assert "differ" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_too_short_returns_422(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.post(
        "/api/users/me/change-password",
        json={"current_password": _USER["password"], "new_password": "short"},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_change_password_without_token_returns_401(client: AsyncClient) -> None:
    r = await client.post(
        "/api/users/me/change-password",
        json={"current_password": "x", "new_password": "newpassword123"},
    )
    assert r.status_code == 401


# ── DELETE /users/me ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_me_success(client: AsyncClient) -> None:
    data = await _register(client)
    token = data["access_token"]

    r = await client.request(
        "DELETE",
        "/api/users/me",
        json={"password": _USER["password"]},
        headers=_auth(token),
    )
    assert r.status_code == 204

    # Account is gone — login should fail
    login = await client.post(
        "/api/auth/login",
        json={"email": _USER["email"], "password": _USER["password"]},
    )
    assert login.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_wrong_password_returns_400(client: AsyncClient) -> None:
    data = await _register(client)
    r = await client.request(
        "DELETE",
        "/api/users/me",
        json={"password": "notmypassword"},
        headers=_auth(data["access_token"]),
    )
    assert r.status_code == 400
    assert "incorrect" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_me_without_token_returns_401(client: AsyncClient) -> None:
    r = await client.request("DELETE", "/api/users/me", json={"password": "x"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_delete_me_token_invalid_after_deletion(client: AsyncClient) -> None:
    """Using a stale token after account deletion should return 404."""
    data = await _register(client)
    token = data["access_token"]

    await client.request(
        "DELETE",
        "/api/users/me",
        json={"password": _USER["password"]},
        headers=_auth(token),
    )

    # The user no longer exists; the route's _get_user_or_404 returns 404.
    r = await client.get("/api/users/me", headers=_auth(token))
    assert r.status_code == 404
