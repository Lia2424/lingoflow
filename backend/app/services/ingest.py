"""Content ingestion service.

Orchestrates fetching from external sources (YouTube, Podcast Index,
articles) and persisting results via ContentRepository.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations import ai as ai_integration
from app.integrations import article as article_integration
from app.integrations import podcast_index as podcast_integration
from app.integrations import youtube as youtube_integration
from app.models.enums import CEFRLevel, SourceType
from app.repositories.content import ContentRepository

logger = logging.getLogger(__name__)


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
    """Fetch podcast episodes and upsert into the content table."""
    items = await podcast_integration.search_episodes(language, query, limit)
    return await _upsert_items(db, items, "podcast", language, query)


async def ingest_article(
    db: AsyncSession,
    url: str,
    language: str | None = None,
) -> IngestResult:
    """Extract an article from *url* and upsert into the content table."""
    metadata = await article_integration.extract_metadata(url)
    effective_language = language or metadata.language or "en"

    repo = ContentRepository(db)
    created_count = 0
    updated_count = 0
    errors = 0

    try:
        cefr = await _classify_or_default(
            metadata.title, metadata.description or "", effective_language
        )
        _, created = await repo.upsert_from_external(
            external_id=metadata.external_id,
            title=metadata.title,
            url=metadata.url,
            source_type=SourceType.ARTICLE,
            language=effective_language,
            cefr_level=cefr,
            description=metadata.description,
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
    except Exception:
        logger.exception("Failed to upsert article %s", url)
        errors += 1

    return IngestResult(
        source_type="article",
        language=effective_language,
        query=url,
        total_fetched=1,
        created=created_count,
        updated=updated_count,
        errors=errors,
    )


async def _upsert_items(
    db: AsyncSession,
    items: Sequence[
        youtube_integration.YouTubeVideoItem
        | podcast_integration.PodcastEpisodeItem
    ],
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
        logger.debug(
            "CEFR classification unavailable for %r — defaulting to A1", title
        )
        return CEFRLevel.A1
