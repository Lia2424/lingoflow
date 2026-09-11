"""Integration tests for POST /api/admin/ingest.

Covers the auth guard (X-Admin-Key), 503 when unconfigured, and the happy
path with mocked ingest service so no real external API calls are made.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.services.ingest import IngestResult

_VALID_BODY = {
    "source_type": "youtube",
    "language": "es",
    "query": "spanish for beginners",
    "limit": 5,
}

_MOCK_RESULT = IngestResult(
    source_type="youtube",
    language="es",
    query="spanish for beginners",
    total_fetched=5,
    created=4,
    updated=1,
    errors=0,
)


# ── Auth guard ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_returns_401_with_no_key(client: AsyncClient) -> None:
    with patch("app.api.routes.admin.settings") as s:
        s.ADMIN_API_KEY = "secret-admin-key"
        r = await client.post("/api/admin/ingest", json=_VALID_BODY)

    assert r.status_code == 401
    assert "X-Admin-Key" in r.json()["detail"]


@pytest.mark.asyncio
async def test_ingest_returns_401_with_wrong_key(client: AsyncClient) -> None:
    with patch("app.api.routes.admin.settings") as s:
        s.ADMIN_API_KEY = "secret-admin-key"
        r = await client.post(
            "/api/admin/ingest",
            json=_VALID_BODY,
            headers={"X-Admin-Key": "wrong-key"},
        )

    assert r.status_code == 401


@pytest.mark.asyncio
async def test_ingest_returns_503_when_admin_key_not_configured(
    client: AsyncClient,
) -> None:
    with patch("app.api.routes.admin.settings") as s:
        s.ADMIN_API_KEY = ""
        r = await client.post(
            "/api/admin/ingest",
            json=_VALID_BODY,
            headers={"X-Admin-Key": "anything"},
        )

    assert r.status_code == 503
    assert "not configured" in r.json()["detail"]


# ── Happy path ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_youtube_returns_result_with_valid_key(
    client: AsyncClient,
) -> None:
    with (
        patch("app.api.routes.admin.settings") as s,
        patch(
            "app.api.routes.admin.ingest_service.ingest_youtube",
            new=AsyncMock(return_value=_MOCK_RESULT),
        ),
    ):
        s.ADMIN_API_KEY = "secret-admin-key"
        r = await client.post(
            "/api/admin/ingest",
            json=_VALID_BODY,
            headers={"X-Admin-Key": "secret-admin-key"},
        )

    assert r.status_code == 200
    body = r.json()
    assert body["source_type"] == "youtube"
    assert body["total_fetched"] == 5
    assert body["created"] == 4
    assert body["updated"] == 1
    assert body["errors"] == 0


@pytest.mark.asyncio
async def test_ingest_podcast_returns_result_with_valid_key(
    client: AsyncClient,
) -> None:
    mock_result = IngestResult(
        source_type="podcast",
        language="es",
        query="News in Slow Spanish",
        total_fetched=10,
        created=8,
        updated=2,
        errors=0,
    )
    with (
        patch("app.api.routes.admin.settings") as s,
        patch(
            "app.api.routes.admin.ingest_service.ingest_podcasts",
            new=AsyncMock(return_value=mock_result),
        ),
    ):
        s.ADMIN_API_KEY = "secret-admin-key"
        r = await client.post(
            "/api/admin/ingest",
            json={
                "source_type": "podcast",
                "language": "es",
                "query": "News in Slow Spanish",
                "limit": 10,
            },
            headers={"X-Admin-Key": "secret-admin-key"},
        )

    assert r.status_code == 200
    body = r.json()
    assert body["source_type"] == "podcast"
    assert body["total_fetched"] == 10
    assert body["created"] == 8


@pytest.mark.asyncio
async def test_ingest_returns_503_when_service_raises_runtime_error(
    client: AsyncClient,
) -> None:
    with (
        patch("app.api.routes.admin.settings") as s,
        patch(
            "app.api.routes.admin.ingest_service.ingest_youtube",
            new=AsyncMock(
                side_effect=RuntimeError("YOUTUBE_API_KEY is not configured")
            ),
        ),
    ):
        s.ADMIN_API_KEY = "test-key"
        r = await client.post(
            "/api/admin/ingest",
            json=_VALID_BODY,
            headers={"X-Admin-Key": "test-key"},
        )

    assert r.status_code == 503
    assert "YOUTUBE_API_KEY" not in r.json()["detail"]
    assert "unavailable" in r.json()["detail"].lower()


# ── Input validation ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_returns_422_for_invalid_source_type(
    client: AsyncClient,
) -> None:
    with patch("app.api.routes.admin.settings") as s:
        s.ADMIN_API_KEY = "test-key"
        r = await client.post(
            "/api/admin/ingest",
            json={**_VALID_BODY, "source_type": "tiktok"},
            headers={"X-Admin-Key": "test-key"},
        )

    assert r.status_code == 422


@pytest.mark.asyncio
async def test_ingest_returns_422_for_limit_out_of_range(
    client: AsyncClient,
) -> None:
    with patch("app.api.routes.admin.settings") as s:
        s.ADMIN_API_KEY = "test-key"
        r = await client.post(
            "/api/admin/ingest",
            json={**_VALID_BODY, "limit": 999},
            headers={"X-Admin-Key": "test-key"},
        )

    assert r.status_code == 422
