"""
Seed the content table with sample items for local development.

Usage (from the backend/ directory):
    python -m scripts.seed_content

The script is idempotent — it skips rows whose URL already exists.
"""

import asyncio
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db.session import AsyncSessionLocal
from app.models.content import Content
from app.models.enums import CEFRLevel, SourceType

# ── Sample data ───────────────────────────────────────────────────────────────

SEED_ITEMS = [
    # ── Spanish / YouTube ────────────────────────────────────────────────────
    {
        "title": "Spanish for Beginners — Learn 100 Common Words",
        "url": "https://www.youtube.com/watch?v=hnpB6E5RQIM",
        "source_type": SourceType.YOUTUBE,
        "language": "es",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": "https://img.youtube.com/vi/hnpB6E5RQIM/maxresdefault.jpg",
        "description": "A beginner-friendly video covering the 100 most common Spanish words with pronunciation and example sentences.",
        "duration_seconds": 1320,
        "published_at": datetime(2024, 3, 15, tzinfo=UTC),
    },
    {
        "title": "El español en conversación — Intermediate dialogue practice",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "source_type": SourceType.YOUTUBE,
        "language": "es",
        "cefr_level": CEFRLevel.B1,
        "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "description": "Natural conversation between two native speakers discussing everyday topics. Subtitles included.",
        "duration_seconds": 2280,
        "published_at": datetime(2024, 6, 2, tzinfo=UTC),
    },
    {
        "title": "Política y sociedad en América Latina — Advanced discussion",
        "url": "https://www.youtube.com/watch?v=l1dnqKGuezo",
        "source_type": SourceType.YOUTUBE,
        "language": "es",
        "cefr_level": CEFRLevel.C1,
        "thumbnail_url": None,
        "description": "A panel debate on contemporary political and social issues in Latin America. Suitable for advanced learners.",
        "duration_seconds": 3600,
        "published_at": datetime(2024, 9, 10, tzinfo=UTC),
    },
    # ── French / Article ─────────────────────────────────────────────────────
    {
        "title": "Les salutations en français — Greetings for beginners",
        "url": "https://www.frenchtoday.com/blog/french-salutations/",
        "source_type": SourceType.ARTICLE,
        "language": "fr",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": None,
        "description": "A short guide to French greetings, farewells, and polite expressions for absolute beginners.",
        "duration_seconds": None,
        "published_at": datetime(2023, 11, 5, tzinfo=UTC),
    },
    {
        "title": "La culture française à table — Food and dining customs",
        "url": "https://www.bonjourlafrance.net/culture/gastronomie.htm",
        "source_type": SourceType.ARTICLE,
        "language": "fr",
        "cefr_level": CEFRLevel.B2,
        "thumbnail_url": None,
        "description": "An in-depth look at French dining etiquette, regional cuisines, and the role of food in French culture.",
        "duration_seconds": None,
        "published_at": datetime(2024, 1, 20, tzinfo=UTC),
    },
    # ── German / Podcast ─────────────────────────────────────────────────────
    {
        "title": "Slow German — Episode 1: Warum lernen Menschen Deutsch?",
        "url": "https://slowgerman.com/2007/10/01/sg001/",
        "source_type": SourceType.PODCAST,
        "language": "de",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": None,
        "description": "Annik Rubens speaks clearly and slowly about why people learn German. Perfect for early learners.",
        "duration_seconds": 480,
        "published_at": datetime(2023, 10, 1, tzinfo=UTC),
    },
    {
        "title": "Deutschlandfunk Kultur — Das Feature",
        "url": "https://www.deutschlandfunkkultur.de/das-feature-100.html",
        "source_type": SourceType.PODCAST,
        "language": "de",
        "cefr_level": CEFRLevel.C2,
        "thumbnail_url": None,
        "description": "In-depth audio documentaries on German culture, history, and society. Authentic native-speed speech.",
        "duration_seconds": 2700,
        "published_at": datetime(2024, 5, 18, tzinfo=UTC),
    },
    # ── Japanese / YouTube ───────────────────────────────────────────────────
    {
        "title": "Japanese for Beginners — Hiragana in 1 Hour",
        "url": "https://www.youtube.com/watch?v=6p9Il_j0zjc",
        "source_type": SourceType.YOUTUBE,
        "language": "ja",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": "https://img.youtube.com/vi/6p9Il_j0zjc/maxresdefault.jpg",
        "description": "Learn all 46 hiragana characters with stroke order, pronunciation, and memory aids.",
        "duration_seconds": 3720,
        "published_at": datetime(2024, 2, 8, tzinfo=UTC),
    },
    # ── Spanish / Music ──────────────────────────────────────────────────────
    {
        "title": "La Bamba — Ritchie Valens (con letra)",
        "url": "https://www.youtube.com/watch?v=pxvcMGABjVU",
        "source_type": SourceType.MUSIC,
        "language": "es",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": "https://img.youtube.com/vi/pxvcMGABjVU/maxresdefault.jpg",
        "description": "Classic Mexican folk song with lyrics — great for picking up basic Spanish rhythm and vocabulary.",
        "duration_seconds": 245,
        "published_at": datetime(2023, 8, 12, tzinfo=UTC),
    },
    # ── French / TV Show ─────────────────────────────────────────────────────
    {
        "title": "Extra French — Episode 1 (comprehensible input sitcom)",
        "url": "https://www.youtube.com/watch?v=9ZBULdFO-oI",
        "source_type": SourceType.TV_SHOW,
        "language": "fr",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": "https://img.youtube.com/vi/9ZBULdFO-oI/maxresdefault.jpg",
        "description": "A language-learning sitcom designed for beginners. Slow speech, clear pronunciation, visual context.",
        "duration_seconds": 1500,
        "published_at": datetime(2023, 7, 30, tzinfo=UTC),
    },
]


# ── Runner ────────────────────────────────────────────────────────────────────

async def seed() -> None:
    async with AsyncSessionLocal() as session:
        inserted = 0
        skipped = 0

        for item in SEED_ITEMS:
            # Check for existing URL to keep idempotent
            existing = await session.scalar(
                select(Content).where(Content.url == item["url"])
            )
            if existing:
                skipped += 1
                continue

            session.add(Content(**item))  # type: ignore[arg-type]
            try:
                await session.flush()
                inserted += 1
            except IntegrityError:
                await session.rollback()
                skipped += 1
                continue

        await session.commit()
        print(f"Seed complete — inserted: {inserted}, skipped (already exist): {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
