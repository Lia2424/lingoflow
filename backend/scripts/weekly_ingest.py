"""Weekly incremental YouTube ingest.

Fetches a small batch of new videos per language. Safe to re-run — upserts on
``external_id``, no duplicates.

Usage (from backend/):
    .venv/bin/python -m scripts.weekly_ingest

Schedule with cron (Sundays 9am) — see scripts/weekly_ingest.sh header.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from scripts.ingest_queries import WEEKLY_YOUTUBE_QUERIES

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _run() -> int:
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

    total_errors = 0

    logger.info(
        "=== Weekly YouTube ingest (%d queries) ===",
        len(WEEKLY_YOUTUBE_QUERIES),
    )
    for language, query, limit in WEEKLY_YOUTUBE_QUERIES:
        logger.info("── %s | %r | limit=%d", language.upper(), query, limit)
        async with session_factory() as db:
            try:
                result = await ingest_youtube(db, language, query, limit)
                logger.info(
                    "   fetched=%d created=%d updated=%d errors=%d",
                    result.total_fetched,
                    result.created,
                    result.updated,
                    result.errors,
                )
                total_errors += result.errors
            except Exception:
                logger.exception("   Ingest failed — skipping query")
                total_errors += 1

    await engine.dispose()
    logger.info("Weekly ingest finished — total_errors=%d", total_errors)
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(_run()))
