"""Podcast Index API integration (https://podcastindex.org).

Podcast Index is a free, open-source alternative to the Apple Podcasts
directory. Authentication uses an HMAC-SHA1 signature of the form:
    Authorization: SHA-1(api_key + api_secret + unix_timestamp)

Requires PODCAST_INDEX_KEY and PODCAST_INDEX_SECRET in settings.
"""

from __future__ import annotations

import contextlib
import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.core.config import settings
from app.models.enums import CEFRLevel, SourceType

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.podcastindex.org/api/1.0"


@dataclass
class PodcastEpisodeItem:
    external_id: str  # "podcast:<episode_guid_or_id>"
    title: str
    url: str
    source_type: SourceType
    language: str
    cefr_level: CEFRLevel
    thumbnail_url: str | None
    description: str | None
    duration_seconds: int | None
    published_at: datetime | None


def _auth_headers() -> dict[str, str]:
    """Build the Podcast Index authentication headers."""
    api_key = settings.PODCAST_INDEX_KEY
    api_secret = settings.PODCAST_INDEX_SECRET
    epoch = str(int(time.time()))
    hash_input = (api_key + api_secret + epoch).encode("utf-8")
    auth_hash = hashlib.sha1(hash_input).hexdigest()
    return {
        "X-Auth-Key": api_key,
        "X-Auth-Date": epoch,
        "Authorization": auth_hash,
        "User-Agent": "LingoFlow/0.1",
    }


async def search_episodes(
    language: str,
    query: str,
    max_results: int = 20,
) -> list[PodcastEpisodeItem]:
    """Search Podcast Index for episodes matching *query* in *language*.

    The Podcast Index ``/search/byterm`` endpoint searches feed titles and
    descriptions. We fetch episode lists from the top matching feeds and
    filter by language where the feed declares one.

    Args:
        language: BCP-47 language code (e.g. ``"es"``).
        query: Free-text search query.
        max_results: Maximum episodes to return.

    Returns:
        List of :class:`PodcastEpisodeItem` ready to be passed to
        ``upsert_from_api``.
    """
    if not settings.PODCAST_INDEX_KEY or not settings.PODCAST_INDEX_SECRET:
        raise RuntimeError(
            "PODCAST_INDEX_KEY and PODCAST_INDEX_SECRET are not configured"
        )

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Step 1: find feeds matching the query
        feed_resp = await client.get(
            f"{_BASE_URL}/search/byterm",
            params={"q": query, "max": 5, "language": language},
            headers=_auth_headers(),
        )
        feed_resp.raise_for_status()
        feeds = feed_resp.json().get("feeds", [])

        items: list[PodcastEpisodeItem] = []
        per_feed = max(1, max_results // max(len(feeds), 1))

        # Step 2: pull recent episodes from each matching feed
        for feed in feeds[:5]:
            feed_id = feed.get("id")
            feed_language = (feed.get("language") or language).split("-")[0].lower()
            feed_image = feed.get("image") or feed.get("artwork")

            if not feed_id:
                continue

            ep_resp = await client.get(
                f"{_BASE_URL}/episodes/byfeedid",
                params={"id": feed_id, "max": per_feed},
                headers=_auth_headers(),
            )
            ep_resp.raise_for_status()
            episodes = ep_resp.json().get("items", [])

            for ep in episodes:
                ep_id = ep.get("id") or ep.get("guid")
                if not ep_id:
                    continue

                title: str = ep.get("title", "")
                description: str | None = ep.get("description") or None
                audio_url: str | None = ep.get("enclosureUrl") or ep.get("link")
                if not audio_url:
                    continue

                thumbnail_url: str | None = ep.get("image") or feed_image or None
                duration_seconds: int | None = ep.get("duration")
                published_at: datetime | None = None
                raw_ts = ep.get("datePublished")
                if raw_ts:
                    with contextlib.suppress(ValueError, OSError):
                        published_at = datetime.fromtimestamp(int(raw_ts), tz=UTC)

                items.append(
                    PodcastEpisodeItem(
                        external_id=f"podcast:{ep_id}",
                        title=title,
                        url=audio_url,
                        source_type=SourceType.PODCAST,
                        language=feed_language,
                        cefr_level=CEFRLevel.A1,  # placeholder
                        thumbnail_url=thumbnail_url,
                        description=description,
                        duration_seconds=duration_seconds,
                        published_at=published_at,
                    )
                )
                if len(items) >= max_results:
                    return items

    return items
