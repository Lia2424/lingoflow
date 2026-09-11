"""Podcast ingestion via Apple iTunes Search API + RSS feeds.

No API key required. Searches iTunes for podcast shows, then fetches recent
episodes from each show's ``feedUrl`` using ``feedparser``.
"""

from __future__ import annotations

import asyncio
import calendar
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import feedparser
import httpx

from app.models.enums import CEFRLevel, SourceType

logger = logging.getLogger(__name__)

_ITUNES_SEARCH = "https://itunes.apple.com/search"
_USER_AGENT = "LingoFlow/0.1"


@dataclass
class PodcastEpisodeItem:
    external_id: str  # "podcast:<episode_guid>"
    title: str
    url: str
    source_type: SourceType
    language: str
    cefr_level: CEFRLevel
    thumbnail_url: str | None
    description: str | None
    duration_seconds: int | None
    published_at: datetime | None


async def search_episodes(
    language: str,
    query: str,
    max_results: int = 20,
) -> list[PodcastEpisodeItem]:
    """Search iTunes for podcast shows matching *query*, then pull RSS episodes.

    Args:
        language: BCP-47 language code stored on ingested rows (e.g. ``"es"``).
        query: iTunes search term — typically a show name.
        max_results: Maximum episodes to return across all matching feeds.

    Returns:
        List of :class:`PodcastEpisodeItem` ready for ``upsert_from_external``.
    """
    max_results = max(1, min(max_results, 50))
    feeds = await _search_podcast_feeds(query, limit=3)
    if not feeds:
        return []

    items: list[PodcastEpisodeItem] = []
    per_feed = max(1, max_results // len(feeds))

    headers = {"User-Agent": _USER_AGENT}
    async with httpx.AsyncClient(timeout=20.0, headers=headers) as client:
        for feed in feeds:
            feed_url = feed.get("feedUrl")
            if not feed_url:
                continue
            feed_image = feed.get("artworkUrl600") or feed.get("artworkUrl100")
            episodes = await _fetch_episodes_from_feed(
                client,
                feed_url=feed_url,
                language=language,
                max_episodes=per_feed,
                thumbnail_url=feed_image,
            )
            items.extend(episodes)
            if len(items) >= max_results:
                return items[:max_results]

    return items


async def _search_podcast_feeds(query: str, limit: int = 5) -> list[dict[str, Any]]:
    headers = {"User-Agent": _USER_AGENT}
    async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
        resp = await client.get(
            _ITUNES_SEARCH,
            params={
                "term": query,
                "media": "podcast",
                "entity": "podcast",
                "limit": limit,
            },
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        results = data.get("results", [])
        if not isinstance(results, list):
            return []
        return results


async def _fetch_episodes_from_feed(
    client: httpx.AsyncClient,
    *,
    feed_url: str,
    language: str,
    max_episodes: int,
    thumbnail_url: str | None,
) -> list[PodcastEpisodeItem]:
    resp = await client.get(feed_url)
    resp.raise_for_status()
    parsed = await asyncio.to_thread(feedparser.parse, resp.content)

    items: list[PodcastEpisodeItem] = []
    for entry in parsed.entries[:max_episodes]:
        item = _entry_to_item(entry, language=language, thumbnail_url=thumbnail_url)
        if item is not None:
            items.append(item)
    return items


def _entry_to_item(
    entry: Any,
    *,
    language: str,
    thumbnail_url: str | None,
) -> PodcastEpisodeItem | None:
    guid = _entry_guid(entry)
    audio_url = _audio_url(entry)
    if not guid or not audio_url:
        return None

    title: str = entry.get("title") or "Untitled episode"
    description: str | None = entry.get("summary") or entry.get("description") or None
    if description:
        description = description.strip() or None

    return PodcastEpisodeItem(
        external_id=f"podcast:{guid}",
        title=title,
        url=audio_url,
        source_type=SourceType.PODCAST,
        language=language,
        cefr_level=CEFRLevel.A1,
        thumbnail_url=thumbnail_url,
        description=description,
        duration_seconds=_parse_duration(entry.get("itunes_duration")),
        published_at=_parse_published(entry.get("published_parsed")),
    )


def _entry_guid(entry: Any) -> str | None:
    raw = entry.get("id") or entry.get("guid") or entry.get("link")
    if raw is None:
        return None
    return str(raw).strip() or None


def _audio_url(entry: Any) -> str | None:
    for enclosure in entry.get("enclosures") or []:
        href = enclosure.get("href")
        if href:
            return str(href)
    link = entry.get("link")
    return str(link).strip() if link else None


def _parse_duration(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    parts = text.split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return None
    if len(nums) == 3:
        hours, minutes, seconds = nums
        return hours * 3600 + minutes * 60 + seconds
    if len(nums) == 2:
        minutes, seconds = nums
        return minutes * 60 + seconds
    return None


def _parse_published(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        timestamp = calendar.timegm(value)
        return datetime.fromtimestamp(timestamp, tz=UTC)
    except (ValueError, TypeError, OverflowError):
        return None
