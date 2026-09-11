"""Content ingestion service.

YouTube (M5) and podcast via iTunes/RSS (M6 Option B).
Article ingestion deferred to a later M6 task.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations import ai as ai_integration
from app.integrations import podcast_itunes as podcast_integration
from app.integrations import youtube as youtube_integration
from app.models.enums import CEFRLevel
from app.repositories.content import ContentRepository

logger = logging.getLogger(__name__)

IngestItem: TypeAlias = (
    youtube_integration.YouTubeVideoItem | podcast_integration.PodcastEpisodeItem
)


@dataclass
class IngestResult:
    source_type: str
    language: str
    query: str
    total_fetched: int
    created: int
    updated: int
    errors: int


async def ingest_youtube(
    db: AsyncSession,
    language: str,
    query: str,
    limit: int = 20,
) -> IngestResult:
    """Fetch YouTube videos and upsert into the content table."""
    items = await youtube_integration.search_videos(language, query, limit)
    return await _upsert_items(db, items, "youtube", language, query)


async def ingest_podcasts(
    db: AsyncSession,
    language: str,
    query: str,
    limit: int = 20,
) -> IngestResult:
    """Fetch podcast episodes via iTunes + RSS and upsert into the content table."""
    items = await podcast_integration.search_episodes(language, query, limit)
    return await _upsert_items(db, items, "podcast", language, query)


async def _upsert_items(
    db: AsyncSession,
    items: Sequence[IngestItem],
    source_type_label: str,
    language: str,
    query: str,
) -> IngestResult:
    repo = ContentRepository(db)
    created_count = 0
    updated_count = 0
    errors = 0

    for item in items:
        try:
            existing = await repo.get_by_external_id(item.external_id)
            if existing is not None:
                cefr = existing.cefr_level
            else:
                cefr = await _classify_or_default(
                    item.title, item.description or "", item.language
                )
            _, created = await repo.upsert_from_external(
                external_id=item.external_id,
                title=item.title,
                url=item.url,
                source_type=item.source_type,
                language=item.language,
                cefr_level=cefr,
                thumbnail_url=item.thumbnail_url,
                description=item.description,
                duration_seconds=item.duration_seconds,
                published_at=item.published_at,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        except Exception:
            logger.exception("Failed to upsert %s item %s", source_type_label, item.url)
            errors += 1

    return IngestResult(
        source_type=source_type_label,
        language=language,
        query=query,
        total_fetched=len(items),
        created=created_count,
        updated=updated_count,
        errors=errors,
    )


async def _classify_or_default(
    title: str,
    description: str,
    language: str,
) -> CEFRLevel:
    """Call AI CEFR classifier; silently fall back to A1 if unavailable."""
    try:
        return await ai_integration.classify_cefr(title, description, language)
    except Exception:
        logger.debug("CEFR classification unavailable for %r — defaulting to A1", title)
        return CEFRLevel.A1
