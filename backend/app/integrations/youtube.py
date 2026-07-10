"""YouTube Data API v3 integration.

Searches for videos and maps them to the shape expected by ContentRepository.
Requires YOUTUBE_API_KEY in settings.
"""

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.core.config import settings
from app.models.enums import CEFRLevel, SourceType

logger = logging.getLogger(__name__)

_BASE_URL = "https://www.googleapis.com/youtube/v3"


@dataclass
class YouTubeVideoItem:
    external_id: str  # "youtube:<videoId>"
    title: str
    url: str
    source_type: SourceType
    language: str
    cefr_level: CEFRLevel
    thumbnail_url: str | None
    description: str | None
    duration_seconds: int | None
    published_at: datetime | None


async def search_videos(
    language: str,
    query: str,
    max_results: int = 20,
) -> list[YouTubeVideoItem]:
    """Search YouTube for videos and return normalised items.

    Args:
        language: BCP-47 language code used for ``relevanceLanguage`` (e.g. ``"es"``).
        query: Free-text search query.
        max_results: Maximum number of results to return (1–50).

    Returns:
        List of :class:`YouTubeVideoItem` ready to be passed to ``upsert_from_api``.
    """
    if not settings.YOUTUBE_API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY is not configured")

    max_results = max(1, min(max_results, 50))

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: search for video IDs
        search_resp = await client.get(
            f"{_BASE_URL}/search",
            params={
                "part": "snippet",
                "type": "video",
                "relevanceLanguage": language,
                "q": query,
                "maxResults": max_results,
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()

        video_ids = [
            item["id"]["videoId"]
            for item in search_data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]
        if not video_ids:
            return []

        # Step 2: fetch video details (contentDetails for duration)
        details_resp = await client.get(
            f"{_BASE_URL}/videos",
            params={
                "part": "snippet,contentDetails",
                "id": ",".join(video_ids),
                "key": settings.YOUTUBE_API_KEY,
            },
        )
        details_resp.raise_for_status()
        details_data = details_resp.json()

    items: list[YouTubeVideoItem] = []
    for item in details_data.get("items", []):
        video_id: str = item["id"]
        snippet = item.get("snippet", {})
        content_details = item.get("contentDetails", {})

        title: str = snippet.get("title", "")
        description: str | None = snippet.get("description") or None
        thumbnail_url: str | None = snippet.get("thumbnails", {}).get("high", {}).get(
            "url"
        ) or snippet.get("thumbnails", {}).get("default", {}).get("url")
        published_at: datetime | None = None
        raw_published = snippet.get("publishedAt")
        if raw_published:
            with contextlib.suppress(ValueError):
                published_at = datetime.fromisoformat(
                    raw_published.replace("Z", "+00:00")
                )

        duration_seconds: int | None = _parse_iso_duration(
            content_details.get("duration", "")
        )

        # Prefer the declared audio language; fall back to the search language
        detected_lang: str = (
            (
                snippet.get("defaultAudioLanguage")
                or snippet.get("defaultLanguage")
                or language
            )
            .split("-")[0]
            .lower()
        )

        items.append(
            YouTubeVideoItem(
                external_id=f"youtube:{video_id}",
                title=title,
                url=f"https://www.youtube.com/watch?v={video_id}",
                source_type=SourceType.YOUTUBE,
                language=detected_lang,
                cefr_level=CEFRLevel.A1,  # placeholder — AI classifier will update
                thumbnail_url=thumbnail_url,
                description=description,
                duration_seconds=duration_seconds,
                published_at=published_at,
            )
        )

    return items


def _parse_iso_duration(iso: str) -> int | None:
    """Convert an ISO 8601 duration string (PT4M13S) to total seconds."""
    import re

    if not iso:
        return None
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not m:
        return None
    days, hours, minutes, seconds = (int(v or 0) for v in m.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds
