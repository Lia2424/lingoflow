"""Unit tests for iTunes + RSS podcast integration."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.integrations.podcast_itunes import (
    PodcastEpisodeItem,
    _audio_url,
    _entry_guid,
    _parse_duration,
    search_episodes,
)
from app.models.enums import CEFRLevel, SourceType


def test_parse_duration_seconds_and_hms() -> None:
    assert _parse_duration(120) == 120
    assert _parse_duration("3600") == 3600
    assert _parse_duration("4:13") == 253
    assert _parse_duration("1:02:03") == 3723
    assert _parse_duration(None) is None
    assert _parse_duration("bad") is None


def test_entry_guid_prefers_id() -> None:
    entry = {"id": "guid-1", "link": "https://example.com/ep"}
    assert _entry_guid(entry) == "guid-1"


def test_audio_url_uses_enclosure() -> None:
    entry = {
        "enclosures": [{"href": "https://example.com/ep.mp3"}],
        "link": "https://example.com/page",
    }
    assert _audio_url(entry) == "https://example.com/ep.mp3"


@pytest.mark.asyncio
async def test_search_episodes_returns_empty_when_no_feeds() -> None:
    with patch(
        "app.integrations.podcast_itunes._search_podcast_feeds",
        new=AsyncMock(return_value=[]),
    ):
        result = await search_episodes("es", "missing show", max_results=5)

    assert result == []


@pytest.mark.asyncio
async def test_search_episodes_maps_feed_entries() -> None:
    feeds = [
        {
            "feedUrl": "https://example.com/feed.xml",
            "artworkUrl600": "https://img.example/art.jpg",
        }
    ]
    episode = PodcastEpisodeItem(
        external_id="podcast:ep-1",
        title="Episode 1",
        url="https://example.com/ep1.mp3",
        source_type=SourceType.PODCAST,
        language="es",
        cefr_level=CEFRLevel.A1,
        thumbnail_url="https://img.example/art.jpg",
        description="Summary",
        duration_seconds=600,
        published_at=None,
    )

    with (
        patch(
            "app.integrations.podcast_itunes._search_podcast_feeds",
            new=AsyncMock(return_value=feeds),
        ),
        patch(
            "app.integrations.podcast_itunes._fetch_episodes_from_feed",
            new=AsyncMock(return_value=[episode]),
        ),
    ):
        result = await search_episodes("es", "News in Slow Spanish", max_results=1)

    assert len(result) == 1
    assert result[0].external_id == "podcast:ep-1"
    assert result[0].title == "Episode 1"


@pytest.mark.asyncio
async def test_search_episodes_propagates_http_errors() -> None:
    request = httpx.Request("GET", "https://itunes.apple.com/search")
    response = httpx.Response(500, request=request)

    with patch("app.integrations.podcast_itunes.httpx.AsyncClient") as client_cls:
        client = client_cls.return_value.__aenter__.return_value
        client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "error", request=request, response=response
            )
        )
        with pytest.raises(httpx.HTTPStatusError):
            await search_episodes("es", "show", max_results=1)
