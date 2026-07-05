"""CLI entry-point for content ingestion.

Usage:
    python -m app.cli.ingest --source youtube --language es \\
        --query "learn spanish" --limit 50
    python -m app.cli.ingest --source podcast --language fr \\
        --query "actualites francaises"
    python -m app.cli.ingest --source article --language en \\
        --query "https://example.com/article"

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


async def _run(
    source: str,
    language: str,
    query: str,
    limit: int,
) -> None:
    # Import here so the module can be imported without a database connection
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.core.config import settings
    from app.services import ingest as ingest_service

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        logger.info(
            "Starting %s ingest | language=%s | query=%r | limit=%d",
            source,
            language,
            query,
            limit,
        )

        if source == "youtube":
            result = await ingest_service.ingest_youtube(db, language, query, limit)
        elif source == "podcast":
            result = await ingest_service.ingest_podcasts(db, language, query, limit)
        elif source == "article":
            result = await ingest_service.ingest_article(
                db, url=query, language=language
            )
        else:
            logger.error("Unknown source type: %s", source)
            sys.exit(1)

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
        description="Ingest content from external sources into LingoFlow."
    )
    parser.add_argument(
        "--source",
        required=True,
        choices=["youtube", "podcast", "article"],
        help="Content source to ingest from.",
    )
    parser.add_argument(
        "--language",
        required=True,
        help="BCP-47 language code, e.g. 'es', 'fr'.",
    )
    parser.add_argument(
        "--query",
        required=True,
        help=(
            "Search query for youtube/podcast. "
            "Full URL for article source."
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum items to fetch (default: 20, max: 50).",
    )
    args = parser.parse_args()

    asyncio.run(_run(args.source, args.language, args.query, min(args.limit, 50)))


if __name__ == "__main__":
    main()
