"""Bulk-seed the content table from curated podcasts (iTunes + RSS).

Usage (from the backend/ directory):
    /path/to/.venv/bin/python -m scripts.seed_from_podcasts

No API keys required — uses Apple iTunes Search + public RSS feeds.
Safe to re-run — deduplicates on ``external_id``.
"""

import asyncio
import logging

from scripts.ingest_queries import BULK_PODCAST_SHOWS

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

SHOWS = BULK_PODCAST_SHOWS


async def _run() -> None:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.core.config import settings
    from app.services.ingest import ingest_podcasts

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    total_created = 0
    total_updated = 0
    total_errors = 0

    for language, show_name, limit in SHOWS:
        logger.info("── %s | %r", language.upper(), show_name)
        async with session_factory() as db:
            try:
                result = await ingest_podcasts(db, language, show_name, limit)
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
                logger.exception("   Failed — skipping show")

    await engine.dispose()
    logger.info(
        "\nDone — total created=%d updated=%d errors=%d",
        total_created,
        total_updated,
        total_errors,
    )


if __name__ == "__main__":
    asyncio.run(_run())
