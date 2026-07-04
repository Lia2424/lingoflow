"""
Integration tests for /api/content/* endpoints.
Requires a running Postgres instance (use: pytest tests/integration/).
"""

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.enums import CEFRLevel, InteractionStatus, SourceType
from app.models.user_content_interaction import UserContentInteraction
from app.repositories.content import ContentRepository
from app.schemas.content import InteractRequest

REGISTER_PAYLOAD = {
    "email": "content-test@lingoflow.com",
    "username": "contenttester",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "es",
}


async def _register_and_get_token(client: AsyncClient) -> str:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    token: str = response.json()["access_token"]
    return token


async def _create_content(
    db_session: AsyncSession,
    *,
    title: str = "Sample content",
    url: str | None = None,
    language: str = "es",
    cefr_level: CEFRLevel = CEFRLevel.A1,
    source_type: SourceType = SourceType.ARTICLE,
) -> Content:
    content = Content(
        title=title,
        url=url or f"https://example.com/{uuid.uuid4()}",
        source_type=source_type,
        language=language,
        cefr_level=cefr_level,
        thumbnail_url=None,
        description="A sample description",
        duration_seconds=120,
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)
    return content


# ── GET /content ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_content_returns_200_with_paginated_shape(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register_and_get_token(client)
    await _create_content(db_session, title="Item A")
    await _create_content(db_session, title="Item B")

    response = await client.get(
        "/api/content", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_list_content_rejects_page_above_upper_bound(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    response = await client.get(
        "/api/content",
        params={"page": 100_001},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_content_filters_narrow_results(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register_and_get_token(client)
    await _create_content(db_session, title="Spanish", language="es")
    await _create_content(db_session, title="French", language="fr")

    response = await client.get(
        "/api/content",
        params={"language": "es"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Spanish"


# ── GET /content/{id} ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_content_by_id_success(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register_and_get_token(client)
    content = await _create_content(db_session, title="Findable")

    response = await client.get(
        f"/api/content/{content.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(content.id)
    assert body["title"] == "Findable"


@pytest.mark.asyncio
async def test_get_content_by_id_returns_404_for_unknown_id(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    response = await client.get(
        f"/api/content/{uuid.uuid4()}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


# ── POST /content/{id}/interact ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_interact_creates_interaction_returns_204(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register_and_get_token(client)
    content = await _create_content(db_session)

    response = await client.post(
        f"/api/content/{content.id}/interact",
        json={"status": "saved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    result = await db_session.execute(
        select(UserContentInteraction).where(
            UserContentInteraction.content_id == content.id
        )
    )
    interaction = result.scalar_one()
    assert interaction.status == "saved"


@pytest.mark.asyncio
async def test_interact_upserts_on_repeated_call(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register_and_get_token(client)
    content = await _create_content(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    first = await client.post(
        f"/api/content/{content.id}/interact",
        json={"status": "saved"},
        headers=headers,
    )
    second = await client.post(
        f"/api/content/{content.id}/interact",
        json={"status": "completed", "rating": 5},
        headers=headers,
    )

    assert first.status_code == 204
    assert second.status_code == 204

    result = await db_session.execute(
        select(UserContentInteraction).where(
            UserContentInteraction.content_id == content.id
        )
    )
    interactions = result.scalars().all()
    # Only one row exists — the second call updated it in place
    assert len(interactions) == 1
    assert interactions[0].status == "completed"
    assert interactions[0].rating == 5


@pytest.mark.asyncio
async def test_interact_omitting_rating_preserves_existing_rating(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Regression test: rating must not be wiped when a later call omits it."""
    token = await _register_and_get_token(client)
    content = await _create_content(db_session)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        f"/api/content/{content.id}/interact",
        json={"status": "completed", "rating": 4},
        headers=headers,
    )
    second = await client.post(
        f"/api/content/{content.id}/interact",
        json={"status": "in_progress"},
        headers=headers,
    )

    assert second.status_code == 204
    result = await db_session.execute(
        select(UserContentInteraction).where(
            UserContentInteraction.content_id == content.id
        )
    )
    interaction = result.scalar_one()
    assert interaction.status == "in_progress"
    assert interaction.rating == 4


@pytest.mark.asyncio
async def test_upsert_interaction_raises_integrity_error_for_missing_content(
    db_session: AsyncSession,
) -> None:
    """
    Regression test for the TOCTOU race between the existence check in
    ContentService.interact() and the upsert: if content_id doesn't exist
    (e.g. deleted between the check and the write), the FK violation must
    surface as IntegrityError so the service layer can translate it to a
    404 instead of letting it bubble up as an unhandled 500.
    """
    repo = ContentRepository(db_session)

    with pytest.raises(IntegrityError):
        await repo.upsert_interaction(
            user_id=uuid.uuid4(),
            content_id=uuid.uuid4(),
            data=InteractRequest(status=InteractionStatus.SAVED),
        )


@pytest.mark.asyncio
async def test_interact_with_unknown_content_returns_404(
    client: AsyncClient,
) -> None:
    token = await _register_and_get_token(client)

    response = await client.post(
        f"/api/content/{uuid.uuid4()}/interact",
        json={"status": "saved"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


# ── Auth guard ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_content_routes_return_401_without_token(client: AsyncClient) -> None:
    list_response = await client.get("/api/content")
    detail_response = await client.get(f"/api/content/{uuid.uuid4()}")
    interact_response = await client.post(
        f"/api/content/{uuid.uuid4()}/interact", json={"status": "saved"}
    )

    assert list_response.status_code == 401
    assert detail_response.status_code == 401
    assert interact_response.status_code == 401
