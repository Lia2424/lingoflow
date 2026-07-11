"""
Unit tests for ContentRepository.

Uses an in-memory SQLite database — no running Postgres required.

Note: `upsert_interaction` uses a PostgreSQL-specific `ON CONFLICT` clause and
is therefore covered by the integration tests (tests/integration/test_content.py)
against a real Postgres instance instead of here.
"""

import uuid
from datetime import UTC, datetime

import pytest

from app.models.content import Content
from app.models.enums import CEFRLevel, SourceType
from app.repositories.content import ContentRepository


def _make_content(
    *,
    title: str,
    url: str,
    language: str = "es",
    cefr_level: CEFRLevel = CEFRLevel.A1,
    source_type: SourceType = SourceType.ARTICLE,
) -> Content:
    return Content(
        title=title,
        url=url,
        source_type=source_type,
        language=language,
        cefr_level=cefr_level,
        thumbnail_url=None,
        description=None,
        duration_seconds=None,
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )


async def _seed(db_session, *items: Content) -> None:
    for item in items:
        db_session.add(item)
    await db_session.commit()


# ── list() ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_returns_all_items_when_no_filters(sqlite_session) -> None:
    await _seed(
        sqlite_session,
        _make_content(title="A", url="https://example.com/a"),
        _make_content(title="B", url="https://example.com/b"),
    )
    repo = ContentRepository(sqlite_session)

    items, total = await repo.list(
        language=None, cefr_level=None, source_type=None, page=1, page_size=20
    )

    assert total == 2
    assert len(items) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_filters_by_language(sqlite_session) -> None:
    await _seed(
        sqlite_session,
        _make_content(title="Spanish", url="https://example.com/es", language="es"),
        _make_content(title="French", url="https://example.com/fr", language="fr"),
    )
    repo = ContentRepository(sqlite_session)

    items, total = await repo.list(
        language="es", cefr_level=None, source_type=None, page=1, page_size=20
    )

    assert total == 1
    assert items[0].title == "Spanish"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_filters_by_cefr_level(sqlite_session) -> None:
    await _seed(
        sqlite_session,
        _make_content(
            title="Easy", url="https://example.com/1", cefr_level=CEFRLevel.A1
        ),
        _make_content(
            title="Hard", url="https://example.com/2", cefr_level=CEFRLevel.C2
        ),
    )
    repo = ContentRepository(sqlite_session)

    items, total = await repo.list(
        language=None, cefr_level=CEFRLevel.C2, source_type=None, page=1, page_size=20
    )

    assert total == 1
    assert items[0].title == "Hard"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_filters_by_source_type(sqlite_session) -> None:
    await _seed(
        sqlite_session,
        _make_content(
            title="Video", url="https://example.com/v", source_type=SourceType.YOUTUBE
        ),
        _make_content(
            title="Article", url="https://example.com/a", source_type=SourceType.ARTICLE
        ),
    )
    repo = ContentRepository(sqlite_session)

    items, total = await repo.list(
        language=None,
        cefr_level=None,
        source_type=SourceType.YOUTUBE,
        page=1,
        page_size=20,
    )

    assert total == 1
    assert items[0].title == "Video"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_combines_multiple_filters(sqlite_session) -> None:
    await _seed(
        sqlite_session,
        _make_content(
            title="Match",
            url="https://example.com/match",
            language="es",
            cefr_level=CEFRLevel.B1,
            source_type=SourceType.PODCAST,
        ),
        _make_content(
            title="WrongLanguage",
            url="https://example.com/wrong-lang",
            language="fr",
            cefr_level=CEFRLevel.B1,
            source_type=SourceType.PODCAST,
        ),
        _make_content(
            title="WrongLevel",
            url="https://example.com/wrong-level",
            language="es",
            cefr_level=CEFRLevel.C1,
            source_type=SourceType.PODCAST,
        ),
    )
    repo = ContentRepository(sqlite_session)

    items, total = await repo.list(
        language="es",
        cefr_level=CEFRLevel.B1,
        source_type=SourceType.PODCAST,
        page=1,
        page_size=20,
    )

    assert total == 1
    assert items[0].title == "Match"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_list_pagination_returns_correct_page_and_total(
    sqlite_session,
) -> None:
    await _seed(
        sqlite_session,
        *[
            _make_content(title=f"Item {i}", url=f"https://example.com/{i}")
            for i in range(5)
        ],
    )
    repo = ContentRepository(sqlite_session)

    page_1, total = await repo.list(
        language=None, cefr_level=None, source_type=None, page=1, page_size=2
    )
    page_2, _ = await repo.list(
        language=None, cefr_level=None, source_type=None, page=2, page_size=2
    )
    page_3, _ = await repo.list(
        language=None, cefr_level=None, source_type=None, page=3, page_size=2
    )

    assert total == 5
    assert len(page_1) == 2
    assert len(page_2) == 2
    assert len(page_3) == 1
    ids = {item.id for item in [*page_1, *page_2, *page_3]}
    assert len(ids) == 5


# ── get_by_id() ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_get_by_id_returns_item_when_exists(sqlite_session) -> None:
    content = _make_content(title="Findable", url="https://example.com/findable")
    await _seed(sqlite_session, content)
    repo = ContentRepository(sqlite_session)

    found = await repo.get_by_id(content.id)

    assert found is not None
    assert found.title == "Findable"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[Content.__table__]],
    indirect=True,
)
async def test_get_by_id_returns_none_when_missing(sqlite_session) -> None:
    repo = ContentRepository(sqlite_session)

    found = await repo.get_by_id(uuid.uuid4())

    assert found is None
