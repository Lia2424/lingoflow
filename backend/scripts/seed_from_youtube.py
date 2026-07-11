"""Bulk-seed the content table from YouTube for all supported languages.

Usage (from the backend/ directory):
    /path/to/.venv/bin/python -m scripts.seed_from_youtube

Runs a curated set of queries per language, deduplicates via external_id,
and auto-classifies CEFR levels via Groq.  Safe to re-run — already-seen
videos are updated, not duplicated.
"""

import asyncio
import logging

from scripts.ingest_queries import BULK_YOUTUBE_QUERIES

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

QUERIES = BULK_YOUTUBE_QUERIES


async def _run() -> None:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.core.config import settings
    from app.services.ingest import ingest_youtube

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    total_created = 0
    total_updated = 0
    total_errors = 0

    for language, query, limit in QUERIES:
        logger.info("── %s | %r", language.upper(), query)
        async with session_factory() as db:
            try:
                result = await ingest_youtube(db, language, query, limit)
                total_created += result.created
                total_updated += result.updated
                total_errors += result.errors
                logger.info(
                    "   fetched=%d created=%d updated=%d errors=%d",
                    result.total_fetched,
                    result.created,
                    result.updated,
                    result.errors,
                )
            except Exception:
                logger.exception("   Failed — skipping query")

    await engine.dispose()
    logger.info(
        "\nDone — total created=%d updated=%d errors=%d",
        total_created,
        total_updated,
        total_errors,
    )


if __name__ == "__main__":
    asyncio.run(_run())
