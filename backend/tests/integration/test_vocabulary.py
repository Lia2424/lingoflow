"""
Integration tests for /api/vocabulary/* endpoints.
Requires a running Postgres instance (use: pytest tests/integration/).
"""

import uuid

import pytest
from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "vocab-test@lingoflow.com",
    "username": "vocabtester",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "es",
}

OTHER_USER_PAYLOAD = {
    "email": "other-vocab@lingoflow.com",
    "username": "othervocab",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "fr",
}


async def _register_and_get_token(
    client: AsyncClient, payload: dict = REGISTER_PAYLOAD
) -> str:
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    token: str = response.json()["access_token"]
    return token


async def _create_entry(
    client: AsyncClient,
    token: str,
    *,
    word: str = "hola",
    language: str = "es",
    definition: str | None = "hello",
    translation: str | None = "hello",
) -> dict:
    resp = await client.post(
        "/api/vocabulary",
        json={
            "word": word,
            "language": language,
            "definition": definition,
            "translation": translation,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── POST /vocabulary ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_entry_returns_201_with_correct_shape(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    resp = await client.post(
        "/api/vocabulary",
        json={"word": "gato", "language": "es", "definition": "cat"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["word"] == "gato"
    assert body["language"] == "es"
    assert body["srs_level"] == 0
    assert body["next_review_at"] is None


@pytest.mark.asyncio
async def test_create_entry_deduplicates_same_word_and_language(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="perro", language="es")

    resp = await client.post(
        "/api/vocabulary",
        json={"word": "perro", "language": "es"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_entry_allows_same_word_different_language(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="chat", language="fr")

    resp = await client.post(
        "/api/vocabulary",
        json={"word": "chat", "language": "es"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_entry_strips_whitespace_from_word(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    resp = await client.post(
        "/api/vocabulary",
        json={"word": "  casa  ", "language": "es"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    assert resp.json()["word"] == "casa"


# ── GET /vocabulary ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_returns_only_current_users_entries(
    client: AsyncClient,
) -> None:
    token_a = await _register_and_get_token(client, REGISTER_PAYLOAD)
    token_b = await _register_and_get_token(client, OTHER_USER_PAYLOAD)

    await _create_entry(client, token_a, word="uno", language="es")
    await _create_entry(client, token_b, word="deux", language="fr")

    resp = await client.get(
        "/api/vocabulary",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["word"] == "uno"


@pytest.mark.asyncio
async def test_list_filters_by_language(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="hola", language="es")
    await _create_entry(client, token, word="bonjour", language="fr")

    resp = await client.get(
        "/api/vocabulary",
        params={"language": "es"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["word"] == "hola"


@pytest.mark.asyncio
async def test_list_filters_by_srs_level(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="gato", language="es")  # srs_level=0

    resp = await client.get(
        "/api/vocabulary",
        params={"srs_level": 0},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["total"] == 1


@pytest.mark.asyncio
async def test_list_pagination(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    words = ["uno", "dos", "tres", "cuatro", "cinco"]
    for w in words:
        await _create_entry(client, token, word=w, language="es")

    resp = await client.get(
        "/api/vocabulary",
        params={"page": 1, "page_size": 2},
        headers={"Authorization": f"Bearer {token}"},
    )

    body = resp.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2


# ── GET /vocabulary/{id} ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_entry_by_id_returns_own_entry(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    created = await _create_entry(client, token, word="mesa")

    resp = await client.get(
        f"/api/vocabulary/{created['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["word"] == "mesa"


@pytest.mark.asyncio
async def test_get_entry_returns_404_for_another_users_entry(
    client: AsyncClient,
) -> None:
    token_a = await _register_and_get_token(client, REGISTER_PAYLOAD)
    token_b = await _register_and_get_token(client, OTHER_USER_PAYLOAD)
    entry = await _create_entry(client, token_a, word="silla")

    resp = await client.get(
        f"/api/vocabulary/{entry['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_entry_returns_404_for_nonexistent_id(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    resp = await client.get(
        f"/api/vocabulary/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 404


# ── PATCH /vocabulary/{id} ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_entry_persists_changes(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="libro", definition="book")

    resp = await client.patch(
        f"/api/vocabulary/{entry['id']}",
        json={"definition": "a written work", "notes": "common noun"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["definition"] == "a written work"
    assert body["notes"] == "common noun"


@pytest.mark.asyncio
async def test_update_entry_can_change_word(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="libro", definition="book")

    resp = await client.patch(
        f"/api/vocabulary/{entry['id']}",
        json={"word": "libro nuevo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert resp.json()["word"] == "libro nuevo"


@pytest.mark.asyncio
async def test_update_entry_duplicate_word_returns_409(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="casa")
    entry = await _create_entry(client, token, word="perro")

    resp = await client.patch(
        f"/api/vocabulary/{entry['id']}",
        json={"word": "casa"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_update_entry_returns_404_for_another_users_entry(
    client: AsyncClient,
) -> None:
    token_a = await _register_and_get_token(client, REGISTER_PAYLOAD)
    token_b = await _register_and_get_token(client, OTHER_USER_PAYLOAD)
    entry = await _create_entry(client, token_a, word="puerta")

    resp = await client.patch(
        f"/api/vocabulary/{entry['id']}",
        json={"notes": "door"},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert resp.status_code == 404


# ── DELETE /vocabulary/{id} ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_entry_returns_204_and_removes_entry(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="ventana")

    delete_resp = await client.delete(
        f"/api/vocabulary/{entry['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    get_resp = await client.get(
        f"/api/vocabulary/{entry['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_resp.status_code == 204
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_entry_returns_404_for_another_users_entry(
    client: AsyncClient,
) -> None:
    token_a = await _register_and_get_token(client, REGISTER_PAYLOAD)
    token_b = await _register_and_get_token(client, OTHER_USER_PAYLOAD)
    entry = await _create_entry(client, token_a, word="techo")

    resp = await client.delete(
        f"/api/vocabulary/{entry['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert resp.status_code == 404


# ── GET /vocabulary/review ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_review_queue_includes_entries_with_null_next_review(
    client: AsyncClient,
) -> None:
    """Newly created entries (next_review_at=None) must appear in the queue."""
    token = await _register_and_get_token(client)
    await _create_entry(client, token, word="nuevo")

    resp = await client.get(
        "/api/vocabulary/review",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_review_queue_is_empty_when_no_entries_due(
    client: AsyncClient,
) -> None:
    """After a correct review, the entry should no longer appear in the queue."""
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="aprender")

    await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    resp = await client.get(
        "/api/vocabulary/review",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    assert len(resp.json()) == 0


# ── POST /vocabulary/{id}/review ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_correct_review_advances_srs_level(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="correr")
    assert entry["srs_level"] == 0

    resp = await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["srs_level"] == 1
    assert body["next_review_at"] is not None


@pytest.mark.asyncio
async def test_five_correct_reviews_reaches_max_srs_level(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="saltar")

    for _ in range(5):
        resp = await client.post(
            f"/api/vocabulary/{entry['id']}/review",
            json={"correct": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        entry = resp.json()

    assert entry["srs_level"] == 5


@pytest.mark.asyncio
async def test_correct_at_max_srs_level_stays_capped(client: AsyncClient) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="volar")

    for _ in range(6):  # one extra beyond max
        resp = await client.post(
            f"/api/vocabulary/{entry['id']}/review",
            json={"correct": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        entry = resp.json()

    assert entry["srs_level"] == 5


@pytest.mark.asyncio
async def test_incorrect_review_resets_srs_level_to_zero(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="nadar")

    # Advance to level 3
    for _ in range(3):
        resp = await client.post(
            f"/api/vocabulary/{entry['id']}/review",
            json={"correct": True},
            headers={"Authorization": f"Bearer {token}"},
        )
        entry = resp.json()
    assert entry["srs_level"] == 3

    # Wrong answer — should reset
    resp = await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["srs_level"] == 0


@pytest.mark.asyncio
async def test_incorrect_review_makes_entry_immediately_due_again(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)
    entry = await _create_entry(client, token, word="escribir")

    # Advance past the first review so it's no longer null
    await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Wrong answer
    await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": False},
        headers={"Authorization": f"Bearer {token}"},
    )

    queue_resp = await client.get(
        "/api/vocabulary/review",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert len(queue_resp.json()) == 1


@pytest.mark.asyncio
async def test_review_returns_404_for_another_users_entry(
    client: AsyncClient,
) -> None:
    token_a = await _register_and_get_token(client, REGISTER_PAYLOAD)
    token_b = await _register_and_get_token(client, OTHER_USER_PAYLOAD)
    entry = await _create_entry(client, token_a, word="leer")

    resp = await client.post(
        f"/api/vocabulary/{entry['id']}/review",
        json={"correct": True},
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert resp.status_code == 404


# ── Auth guards ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_all_vocabulary_routes_require_auth(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    routes = [
        ("GET", "/api/vocabulary"),
        ("POST", "/api/vocabulary"),
        ("GET", f"/api/vocabulary/{fake_id}"),
        ("PATCH", f"/api/vocabulary/{fake_id}"),
        ("DELETE", f"/api/vocabulary/{fake_id}"),
        ("GET", "/api/vocabulary/review"),
        ("POST", f"/api/vocabulary/{fake_id}/review"),
    ]

    for method, path in routes:
        resp = await client.request(method, path)
        assert resp.status_code == 401, (
            f"{method} {path} returned {resp.status_code}, expected 401"
        )
