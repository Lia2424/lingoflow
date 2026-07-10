"""Curated YouTube ingest queries shared by weekly and bulk seed scripts.

Each entry is (language, query, limit).
"""

from __future__ import annotations

# One query per language — ~80 new/updated YouTube videos per weekly run.
WEEKLY_YOUTUBE_QUERIES: list[tuple[str, str, int]] = [
    ("es", "learn spanish", 10),
    ("fr", "apprendre français", 10),
    ("de", "Deutsch lernen", 10),
    ("it", "imparare italiano", 10),
    ("ja", "日本語 勉強", 10),
    ("ko", "한국어 배우기", 10),
    ("pt", "aprender português", 10),
    ("zh", "学中文", 10),
]

# Bulk one-time fill — multiple queries per language for CEFR spread.
BULK_YOUTUBE_QUERIES: list[tuple[str, str, int]] = [
    ("es", "learn spanish beginners", 20),
    ("es", "español avanzado nativos", 15),
    ("fr", "apprendre le français débutants", 20),
    ("fr", "français avancé niveau C1", 15),
    ("de", "Deutsch lernen Anfänger", 20),
    ("de", "fortgeschrittenes Deutsch C1 C2", 15),
    ("it", "imparare italiano principianti", 15),
    ("it", "italiano avanzato madrelingua", 10),
    ("ja", "日本語 初心者 勉強", 15),
    ("ja", "日本語上級者向け", 10),
    ("ko", "한국어 배우기 초급", 15),
    ("ko", "고급 한국어 회화", 10),
    ("pt", "aprender português iniciantes", 15),
    ("pt", "português avançado nativo", 10),
    ("zh", "学中文 初学者", 15),
    ("zh", "高级汉语 母语", 10),
]
