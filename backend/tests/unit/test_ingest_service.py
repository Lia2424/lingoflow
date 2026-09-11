"""Unit tests for app/services/ingest.py."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.podcast_itunes import PodcastEpisodeItem
from app.integrations.youtube import YouTubeVideoItem
from app.models.enums import CEFRLevel, SourceType
from app.services.ingest import (
    _classify_or_default,
    ingest_podcasts,
    ingest_youtube,
)


def _youtube_item() -> YouTubeVideoItem:
    return YouTubeVideoItem(
        external_id="youtube:abc123",
        title="Learn Spanish",
        url="https://www.youtube.com/watch?v=abc123",
        source_type=SourceType.YOUTUBE,
        language="es",
        cefr_level=CEFRLevel.A1,
        thumbnail_url="https://img.example/thumb.jpg",
        description="A lesson",
        duration_seconds=300,
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


def _podcast_item() -> PodcastEpisodeItem:
    return PodcastEpisodeItem(
        external_id="podcast:ep-1",
        title="News in Slow Spanish",
        url="https://example.com/ep1.mp3",
        source_type=SourceType.PODCAST,
        language="es",
        cefr_level=CEFRLevel.A1,
        thumbnail_url=None,
        description="Episode 1",
        duration_seconds=600,
        published_at=datetime(2024, 2, 1, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_ingest_youtube_counts_created_and_updated() -> None:
    db = MagicMock()
    items = [_youtube_item(), _youtube_item()]

    with (
        patch(
            "app.services.ingest.youtube_integration.search_videos",
            new=AsyncMock(return_value=items),
        ),
        patch(
            "app.services.ingest.ai_integration.classify_cefr",
            new=AsyncMock(return_value=CEFRLevel.B2),
        ),
        patch("app.services.ingest.ContentRepository") as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_by_external_id = AsyncMock(return_value=None)
        repo.upsert_from_external = AsyncMock(
            side_effect=[(MagicMock(), True), (MagicMock(), False)]
        )

        result = await ingest_youtube(db, "es", "learn spanish", limit=2)

    assert result.source_type == "youtube"
    assert result.total_fetched == 2
    assert result.created == 1
    assert result.updated == 1
    assert result.errors == 0


@pytest.mark.asyncio
async def test_ingest_youtube_skips_cefr_classify_on_update() -> None:
    db = MagicMock()
    existing = MagicMock()
    existing.cefr_level = CEFRLevel.C1

    with (
        patch(
            "app.services.ingest.youtube_integration.search_videos",
            new=AsyncMock(return_value=[_youtube_item()]),
        ),
        patch(
            "app.services.ingest.ai_integration.classify_cefr",
            new=AsyncMock(return_value=CEFRLevel.A1),
        ) as mock_classify,
        patch("app.services.ingest.ContentRepository") as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_by_external_id = AsyncMock(return_value=existing)
        repo.upsert_from_external = AsyncMock(return_value=(MagicMock(), False))

        result = await ingest_youtube(db, "es", "learn spanish", limit=1)

    assert result.updated == 1
    mock_classify.assert_not_called()
    repo.upsert_from_external.assert_awaited_once()
    assert repo.upsert_from_external.await_args.kwargs["cefr_level"] == CEFRLevel.C1


@pytest.mark.asyncio
async def test_ingest_youtube_counts_errors() -> None:
    db = MagicMock()

    with (
        patch(
            "app.services.ingest.youtube_integration.search_videos",
            new=AsyncMock(return_value=[_youtube_item()]),
        ),
        patch(
            "app.services.ingest.ai_integration.classify_cefr",
            new=AsyncMock(return_value=CEFRLevel.A1),
        ),
        patch("app.services.ingest.ContentRepository") as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_by_external_id = AsyncMock(return_value=None)
        repo.upsert_from_external = AsyncMock(side_effect=RuntimeError("db down"))

        result = await ingest_youtube(db, "es", "learn spanish", limit=1)

    assert result.errors == 1


@pytest.mark.asyncio
async def test_ingest_podcasts_counts_errors() -> None:
    db = MagicMock()

    with (
        patch(
            "app.services.ingest.podcast_integration.search_episodes",
            new=AsyncMock(return_value=[_podcast_item()]),
        ),
        patch(
            "app.services.ingest.ai_integration.classify_cefr",
            new=AsyncMock(return_value=CEFRLevel.A1),
        ),
        patch("app.services.ingest.ContentRepository") as repo_cls,
    ):
        repo = repo_cls.return_value
        repo.get_by_external_id = AsyncMock(return_value=None)
        repo.upsert_from_external = AsyncMock(side_effect=RuntimeError("db down"))

        result = await ingest_podcasts(db, "es", "News in Slow Spanish", limit=1)

    assert result.source_type == "podcast"
    assert result.total_fetched == 1
    assert result.errors == 1


@pytest.mark.asyncio
async def test_classify_or_default_returns_a1_when_ai_unavailable() -> None:
    with patch(
        "app.services.ingest.ai_integration.classify_cefr",
        new=AsyncMock(side_effect=RuntimeError("no key")),
    ):
        level = await _classify_or_default("Title", "Desc", "es")

    assert level == CEFRLevel.A1
