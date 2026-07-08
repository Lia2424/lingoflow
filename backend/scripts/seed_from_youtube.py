"""Bulk-seed the content table from YouTube for all supported languages.

Usage (from the backend/ directory):
    /path/to/.venv/bin/python -m scripts.seed_from_youtube

Runs a curated set of queries per language, deduplicates via external_id,
and auto-classifies CEFR levels via Groq.  Safe to re-run — already-seen
videos are updated, not duplicated.
"""

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Curated queries ────────────────────────────────────────────────────────────
# (language, query, limit)
# Multiple queries per language give better CEFR spread (beginner + advanced).

QUERIES = [
    # Spanish
    ("es", "learn spanish beginners", 20),
    ("es", "español avanzado nativos", 15),
    # French
    ("fr", "apprendre le français débutants", 20),
    ("fr", "français avancé niveau C1", 15),
    # German
    ("de", "Deutsch lernen Anfänger", 20),
    ("de", "fortgeschrittenes Deutsch C1 C2", 15),
    # Italian
    ("it", "imparare italiano principianti", 15),
    ("it", "italiano avanzato madrelingua", 10),
    # Japanese
    ("ja", "日本語 初心者 勉強", 15),
    ("ja", "日本語上級者向け", 10),
    # Korean
    ("ko", "한국어 배우기 초급", 15),
    ("ko", "고급 한국어 회화", 10),
    # Portuguese
    ("pt", "aprender português iniciantes", 15),
    ("pt", "português avançado nativo", 10),
    # Mandarin
    ("zh", "学中文 初学者", 15),
    ("zh", "高级汉语 母语", 10),
]


async def _run() -> None:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
