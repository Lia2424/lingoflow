"""Unit tests for YouTube integration helpers and search."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.integrations.youtube import _parse_iso_duration, search_videos


@pytest.mark.parametrize(
    ("iso", "expected"),
    [
        ("PT4M13S", 253),
        ("PT1H2M3S", 3723),
        ("P1DT2H", 93600),
        ("", None),
        ("invalid", None),
    ],
)
def test_parse_iso_duration(iso: str, expected: int | None) -> None:
    assert _parse_iso_duration(iso) == expected


@pytest.mark.asyncio
async def test_search_videos_raises_when_api_key_missing() -> None:
    with patch("app.integrations.youtube.settings") as mock_settings:
        mock_settings.YOUTUBE_API_KEY = ""
        with pytest.raises(RuntimeError, match="YOUTUBE_API_KEY"):
            await search_videos("es", "learn spanish", max_results=5)


@pytest.mark.asyncio
async def test_search_videos_returns_empty_when_no_results() -> None:
    search_response = MagicMock()
    search_response.raise_for_status = MagicMock()
    search_response.json.return_value = {"items": []}

    with (
        patch("app.integrations.youtube.settings") as mock_settings,
        patch("app.integrations.youtube.httpx.AsyncClient") as client_cls,
    ):
        mock_settings.YOUTUBE_API_KEY = "test-key"
        client = client_cls.return_value.__aenter__.return_value
        client.get = AsyncMock(return_value=search_response)

        result = await search_videos("es", "empty query", max_results=5)

    assert result == []


@pytest.mark.asyncio
async def test_search_videos_maps_api_response() -> None:
    search_response = MagicMock()
    search_response.raise_for_status = MagicMock()
    search_response.json.return_value = {
        "items": [{"id": {"videoId": "abc123"}}],
    }

    details_response = MagicMock()
    details_response.raise_for_status = MagicMock()
    details_response.json.return_value = {
        "items": [
            {
                "id": "abc123",
                "snippet": {
                    "title": "Learn Spanish Fast",
                    "description": "Intro lesson",
                    "publishedAt": "2024-01-15T10:00:00Z",
                    "defaultAudioLanguage": "es-ES",
                    "thumbnails": {"high": {"url": "https://img.example/thumb.jpg"}},
                },
                "contentDetails": {"duration": "PT5M30S"},
            }
        ]
    }

    with (
        patch("app.integrations.youtube.settings") as mock_settings,
        patch("app.integrations.youtube.httpx.AsyncClient") as client_cls,
    ):
        mock_settings.YOUTUBE_API_KEY = "test-key"
        client = client_cls.return_value.__aenter__.return_value
        client.get = AsyncMock(side_effect=[search_response, details_response])

        result = await search_videos("es", "learn spanish", max_results=1)

    assert len(result) == 1
    assert result[0].external_id == "youtube:abc123"
    assert result[0].title == "Learn Spanish Fast"
    assert result[0].language == "es"
    assert result[0].duration_seconds == 330


@pytest.mark.asyncio
async def test_search_videos_propagates_http_errors() -> None:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(403, request=request)

    with (
        patch("app.integrations.youtube.settings") as mock_settings,
        patch("app.integrations.youtube.httpx.AsyncClient") as client_cls,
    ):
        mock_settings.YOUTUBE_API_KEY = "test-key"
        client = client_cls.return_value.__aenter__.return_value
        client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "forbidden", request=request, response=response
            )
        )

        with pytest.raises(httpx.HTTPStatusError):
            await search_videos("es", "learn spanish", max_results=1)
