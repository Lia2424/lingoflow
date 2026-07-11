"""CLI entry-point for YouTube content ingestion.

Usage:
    python -m app.cli.ingest --language es --query "learn spanish" --limit 50

The script creates its own database session and tears it down cleanly, so it
can be run as a cron job or management command without a running server.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _run(language: str, query: str, limit: int) -> None:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.core.config import settings
    from app.services import ingest as ingest_service

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        logger.info(
            "Starting youtube ingest | language=%s | query=%r | limit=%d",
            language,
            query,
            limit,
        )
        result = await ingest_service.ingest_youtube(db, language, query, limit)

    await engine.dispose()

    logger.info(
        "Done — fetched=%d created=%d updated=%d errors=%d",
        result.total_fetched,
        result.created,
        result.updated,
        result.errors,
    )
    if result.errors:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest YouTube videos into LingoFlow."
    )
    parser.add_argument(
        "--language",
        required=True,
        help="BCP-47 language code, e.g. 'es', 'fr'.",
    )
    parser.add_argument(
        "--query",
        required=True,
        help="YouTube search query.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum videos to fetch (default: 20, max: 50).",
    )
    args = parser.parse_args()

    asyncio.run(_run(args.language, args.query, min(args.limit, 50)))


if __name__ == "__main__":
    main()
