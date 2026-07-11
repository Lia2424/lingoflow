"""Remove placeholder content rows seeded by seed_content.py.

Deletes rows with no ``external_id`` (fake demo catalog). Real ingested content
from YouTube, podcasts, and articles always has an ``external_id``.

Usage (from backend/):
    .venv/bin/python -m scripts.remove_placeholder_content --dry-run
    .venv/bin/python -m scripts.remove_placeholder_content --confirm
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from sqlalchemy import delete, func, select

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def _run(*, confirm: bool) -> None:
    from sqlalchemy.ext.asyncio import (
        AsyncSession,
        async_sessionmaker,
        create_async_engine,
    )

    from app.core.config import settings
    from app.models.content import Content

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as db:
        count_stmt = (
            select(func.count())
            .select_from(Content)
            .where(Content.external_id.is_(None))
        )
        count = (await db.execute(count_stmt)).scalar_one()
        logger.info("Found %d placeholder rows (external_id IS NULL)", count)

        if count == 0:
            await engine.dispose()
            return

        preview = await db.execute(
            select(Content.source_type, Content.title)
            .where(Content.external_id.is_(None))
            .limit(10)
        )
        for source_type, title in preview.all():
            logger.info("  - [%s] %s", source_type.value, title)

        if not confirm:
            logger.info("Dry run only — pass --confirm to delete these rows.")
            await engine.dispose()
            return

        await db.execute(delete(Content).where(Content.external_id.is_(None)))
        await db.commit()
        logger.info("Deleted %d placeholder rows.", count)

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove fake seed_content.py rows from the catalog."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted (default if --confirm not passed).",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete placeholder rows.",
    )
    args = parser.parse_args()
    asyncio.run(_run(confirm=args.confirm))


if __name__ == "__main__":
    main()
