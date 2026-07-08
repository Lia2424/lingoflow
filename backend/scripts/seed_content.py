"""
Seed the content table with sample items for local development.

Usage (from the backend/ directory):
    python -m scripts.seed_content

The script is idempotent — it skips rows whose URL already exists.
Covers every SourceType, all six CEFR levels, and six languages so the
discovery feed's filter bar has something meaningful to filter.
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
    # ── Articles ─────────────────────────────────────────────────────────────
    {
        "title": "Les salutations en français — Greetings for beginners",
        "url": "https://www.frenchtoday.com/blog/french-salutations/",
        "source_type": SourceType.ARTICLE,
        "language": "fr",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": None,
        "description": (
            "A short guide to French greetings, farewells, and polite "
            "expressions for absolute beginners."
        ),
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
        "description": (
            "An in-depth look at French dining etiquette, regional "
            "cuisines, and the role of food in French culture."
        ),
        "duration_seconds": None,
        "published_at": datetime(2024, 1, 20, tzinfo=UTC),
    },
    {
        "title": "Il sistema politico italiano — An overview",
        "url": "https://www.italyheritage.com/traditions/politics.htm",
        "source_type": SourceType.ARTICLE,
        "language": "it",
        "cefr_level": CEFRLevel.B1,
        "thumbnail_url": None,
        "description": (
            "An accessible explanation of the Italian political system, "
            "written in intermediate-level Italian."
        ),
        "duration_seconds": None,
        "published_at": datetime(2024, 4, 3, tzinfo=UTC),
    },
    {
        "title": "日本の四季 — The four seasons of Japan",
        "url": "https://www.tofugu.com/japan/four-seasons/",
        "source_type": SourceType.ARTICLE,
        "language": "ja",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": None,
        "description": (
            "A simple article describing how the four seasons shape "
            "Japanese culture, food, and festivals."
        ),
        "duration_seconds": None,
        "published_at": datetime(2023, 9, 12, tzinfo=UTC),
    },
    # ── Podcasts ─────────────────────────────────────────────────────────────
    {
        "title": "Slow German — Episode 1: Warum lernen Menschen Deutsch?",
        "url": "https://slowgerman.com/2007/10/01/sg001/",
        "source_type": SourceType.PODCAST,
        "language": "de",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": None,
        "description": (
            "Annik Rubens speaks clearly and slowly about why people "
            "learn German. Perfect for early learners."
        ),
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
        "description": (
            "In-depth audio documentaries on German culture, history, "
            "and society. Authentic native-speed speech."
        ),
        "duration_seconds": 2700,
        "published_at": datetime(2024, 5, 18, tzinfo=UTC),
    },
    {
        "title": "Notes in Spanish — Intermediate conversation practice",
        "url": "https://www.notesinspanish.com/intermediate-episode-1/",
        "source_type": SourceType.PODCAST,
        "language": "es",
        "cefr_level": CEFRLevel.B1,
        "thumbnail_url": None,
        "description": (
            "A natural conversation between native Spanish speakers, "
            "aimed at intermediate learners building listening stamina."
        ),
        "duration_seconds": 900,
        "published_at": datetime(2024, 2, 14, tzinfo=UTC),
    },
    {
        "title": "TTMIK Basic Korean — Lesson 1: Greetings",
        "url": "https://talktomeinkorean.com/lessons/l1l1/",
        "source_type": SourceType.PODCAST,
        "language": "ko",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": None,
        "description": (
            "The very first lesson in the Talk To Me In Korean series — "
            "basic greetings with clear, beginner-friendly explanations."
        ),
        "duration_seconds": 360,
        "published_at": datetime(2023, 6, 1, tzinfo=UTC),
    },
    # ── Music ────────────────────────────────────────────────────────────────
    {
        "title": "La Bamba — Ritchie Valens (con letra)",
        "url": "https://www.youtube.com/watch?v=pxvcMGABjVU",
        "source_type": SourceType.MUSIC,
        "language": "es",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": "https://img.youtube.com/vi/pxvcMGABjVU/maxresdefault.jpg",
        "description": (
            "Classic Mexican folk song with lyrics — great for picking "
            "up basic Spanish rhythm and vocabulary."
        ),
        "duration_seconds": 245,
        "published_at": datetime(2023, 8, 12, tzinfo=UTC),
    },
    {
        "title": "La Vie en Rose — Édith Piaf (paroles)",
        "url": "https://www.youtube.com/watch?v=Cw72n2ldz9Q",
        "source_type": SourceType.MUSIC,
        "language": "fr",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": "https://img.youtube.com/vi/Cw72n2ldz9Q/maxresdefault.jpg",
        "description": (
            "A beloved French classic with on-screen lyrics — gentle "
            "introduction to French pronunciation and rhythm."
        ),
        "duration_seconds": 210,
        "published_at": datetime(2023, 5, 20, tzinfo=UTC),
    },
    {
        "title": "Volare — Domenico Modugno (con testo)",
        "url": "https://www.youtube.com/watch?v=vJTRV0X-VpM",
        "source_type": SourceType.MUSIC,
        "language": "it",
        "cefr_level": CEFRLevel.B1,
        "thumbnail_url": "https://img.youtube.com/vi/vJTRV0X-VpM/maxresdefault.jpg",
        "description": (
            "An iconic Italian song with full lyrics displayed — good "
            "listening practice for intermediate learners."
        ),
        "duration_seconds": 195,
        "published_at": datetime(2023, 7, 2, tzinfo=UTC),
    },
    # ── TV Shows ─────────────────────────────────────────────────────────────
    {
        "title": "Extra French — Episode 1 (comprehensible input sitcom)",
        "url": "https://www.youtube.com/watch?v=9ZBULdFO-oI",
        "source_type": SourceType.TV_SHOW,
        "language": "fr",
        "cefr_level": CEFRLevel.A2,
        "thumbnail_url": "https://img.youtube.com/vi/9ZBULdFO-oI/maxresdefault.jpg",
        "description": (
            "A language-learning sitcom designed for beginners. Slow "
            "speech, clear pronunciation, visual context."
        ),
        "duration_seconds": 1500,
        "published_at": datetime(2023, 7, 30, tzinfo=UTC),
    },
    {
        "title": "Extra auf Deutsch — Episode 1",
        "url": "https://www.youtube.com/watch?v=jPDjHRLW-Vc",
        "source_type": SourceType.TV_SHOW,
        "language": "de",
        "cefr_level": CEFRLevel.B1,
        "thumbnail_url": "https://img.youtube.com/vi/jPDjHRLW-Vc/maxresdefault.jpg",
        "description": (
            "The German edition of the Extra sitcom series — natural "
            "pacing for intermediate learners with visual storytelling."
        ),
        "duration_seconds": 1440,
        "published_at": datetime(2024, 3, 22, tzinfo=UTC),
    },
    {
        "title": "テラスハウス — Terrace House (clip with subtitles)",
        "url": "https://www.youtube.com/watch?v=3g8jY9GkX2c",
        "source_type": SourceType.TV_SHOW,
        "language": "ja",
        "cefr_level": CEFRLevel.B2,
        "thumbnail_url": "https://img.youtube.com/vi/3g8jY9GkX2c/maxresdefault.jpg",
        "description": (
            "A clip from a popular Japanese reality show — natural, "
            "fast-paced conversational Japanese for upper-intermediate learners."
        ),
        "duration_seconds": 1200,
        "published_at": datetime(2024, 8, 5, tzinfo=UTC),
    },
    # ── Other ────────────────────────────────────────────────────────────────
    {
        "title": "RAE — Diccionario de la lengua española (reference)",
        "url": "https://dle.rae.es/",
        "source_type": SourceType.OTHER,
        "language": "es",
        "cefr_level": CEFRLevel.C2,
        "thumbnail_url": None,
        "description": (
            "The official Spanish dictionary from the Real Academia "
            "Española — an authoritative reference for advanced learners."
        ),
        "duration_seconds": None,
        "published_at": None,
    },
    {
        "title": "Duden — German dictionary and grammar reference",
        "url": "https://www.duden.de/",
        "source_type": SourceType.OTHER,
        "language": "de",
        "cefr_level": CEFRLevel.A1,
        "thumbnail_url": None,
        "description": (
            "The standard reference for German spelling, grammar, and "
            "vocabulary — useful at every level, listed here for beginners."
        ),
        "duration_seconds": None,
        "published_at": None,
    },
]


# ── Runner ────────────────────────────────────────────────────────────────────


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        inserted = 0
        skipped = 0

        for item in SEED_ITEMS:
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
        print(f"Seed complete — inserted: {inserted}, skipped: {skipped}")


if __name__ == "__main__":
    asyncio.run(seed())
