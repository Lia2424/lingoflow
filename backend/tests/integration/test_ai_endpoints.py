"""Integration tests for AI-powered endpoints.

All AI calls are mocked — no real API key or internet access required.
Tests cover:
  - POST /api/vocabulary/{id}/suggest
  - GET  /api/content/{id}/questions
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.enums import CEFRLevel, SourceType

_USER = {
    "email": "ai-test@lingoflow.com",
    "username": "aitester",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "es",
}

_OTHER_USER = {
    "email": "ai-other@lingoflow.com",
    "username": "aiother",
    "password": "securepassword123",
    "native_language": "en",
    "target_language": "fr",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _register(client: AsyncClient, payload: dict = _USER) -> str:
    r = await client.post("/api/auth/register", json=payload)
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def _create_entry(
    client: AsyncClient,
    token: str,
    *,
    word: str = "hola",
    language: str = "es",
) -> dict:
    r = await client.post(
        "/api/vocabulary",
        json={"word": word, "language": language},
        headers=_auth(token),
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _create_content(
    db_session: AsyncSession,
    *,
    title: str = "Learn Spanish",
    language: str = "es",
) -> Content:
    content = Content(
        title=title,
        url=f"https://example.com/{uuid.uuid4()}",
        source_type=SourceType.YOUTUBE,
        language=language,
        cefr_level=CEFRLevel.B1,
        description="A sample description for testing.",
        published_at=datetime(2024, 1, 1, tzinfo=UTC),
    )
    db_session.add(content)
    await db_session.commit()
    await db_session.refresh(content)
    return content


_MOCK_DEFINITION = {"definition": "A common Spanish greeting", "translation": "hello"}
_MOCK_QUESTIONS = [
    {
        "question": "What does 'hola' mean?",
        "options": ["Goodbye", "Hello", "Please", "Thank you"],
        "answer_index": 1,
    },
    {
        "question": "Which language is this?",
        "options": ["French", "Italian", "Spanish", "Portuguese"],
        "answer_index": 2,
    },
]


# ── POST /vocabulary/{id}/suggest ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_suggest_definition_returns_suggestion(client: AsyncClient) -> None:
    token = await _register(client)
    entry = await _create_entry(client, token, word="hola")

    with patch(
        "app.api.routes.vocabulary.ai_integration.generate_definition",
        new=AsyncMock(return_value=_MOCK_DEFINITION),
    ):
        r = await client.post(
            f"/api/vocabulary/{entry['id']}/suggest", headers=_auth(token)
        )

    assert r.status_code == 200
    body = r.json()
    assert body["definition"] == "A common Spanish greeting"
    assert body["translation"] == "hello"


@pytest.mark.asyncio
async def test_suggest_definition_does_not_save_to_entry(
    client: AsyncClient,
) -> None:
    """Suggestion is preview-only — the stored entry must not be modified."""
    token = await _register(client)
    entry = await _create_entry(client, token, word="hola")

    with patch(
        "app.api.routes.vocabulary.ai_integration.generate_definition",
        new=AsyncMock(return_value=_MOCK_DEFINITION),
    ):
        await client.post(
            f"/api/vocabulary/{entry['id']}/suggest", headers=_auth(token)
        )

    r = await client.get(
        f"/api/vocabulary/{entry['id']}", headers=_auth(token)
    )
    assert r.json()["definition"] is None


@pytest.mark.asyncio
async def test_suggest_definition_returns_404_for_unknown_entry(
    client: AsyncClient,
) -> None:
    token = await _register(client)
    r = await client.post(
        f"/api/vocabulary/{uuid.uuid4()}/suggest", headers=_auth(token)
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_suggest_definition_returns_404_for_other_users_entry(
    client: AsyncClient,
) -> None:
    owner_token = await _register(client, _USER)
    other_token = await _register(client, _OTHER_USER)
    entry = await _create_entry(client, owner_token, word="hola")

    with patch(
        "app.api.routes.vocabulary.ai_integration.generate_definition",
        new=AsyncMock(return_value=_MOCK_DEFINITION),
    ):
        r = await client.post(
            f"/api/vocabulary/{entry['id']}/suggest", headers=_auth(other_token)
        )

    assert r.status_code == 404


@pytest.mark.asyncio
async def test_suggest_definition_returns_401_without_token(
    client: AsyncClient,
) -> None:
    r = await client.post(f"/api/vocabulary/{uuid.uuid4()}/suggest")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_suggest_definition_returns_503_when_ai_unavailable(
    client: AsyncClient,
) -> None:
    token = await _register(client)
    entry = await _create_entry(client, token, word="hola")

    with patch(
        "app.api.routes.vocabulary.ai_integration.generate_definition",
        new=AsyncMock(side_effect=RuntimeError("OPENAI_API_KEY is not configured")),
    ):
        r = await client.post(
            f"/api/vocabulary/{entry['id']}/suggest", headers=_auth(token)
        )

    assert r.status_code == 503
    assert "OPENAI_API_KEY" in r.json()["detail"]


# ── GET /content/{id}/questions ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_questions_generates_and_returns_on_first_call(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register(client)
    content = await _create_content(db_session)

    with patch(
        "app.api.routes.content.ai_integration.generate_questions",
        new=AsyncMock(return_value=_MOCK_QUESTIONS),
    ) as mock_generate:
        r = await client.get(
            f"/api/content/{content.id}/questions", headers=_auth(token)
        )

    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    assert body[0]["question"] == "What does 'hola' mean?"
    assert body[0]["answer_index"] == 1
    assert len(body[0]["options"]) == 4
    mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_get_questions_returns_cache_on_second_call(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """AI must only be called once — second request hits the cache."""
    token = await _register(client)
    content = await _create_content(db_session)

    with patch(
        "app.api.routes.content.ai_integration.generate_questions",
        new=AsyncMock(return_value=_MOCK_QUESTIONS),
    ) as mock_generate:
        r1 = await client.get(
            f"/api/content/{content.id}/questions", headers=_auth(token)
        )
        r2 = await client.get(
            f"/api/content/{content.id}/questions", headers=_auth(token)
        )

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()
    mock_generate.assert_called_once()


@pytest.mark.asyncio
async def test_get_questions_returns_404_for_unknown_content(
    client: AsyncClient,
) -> None:
    token = await _register(client)
    r = await client.get(
        f"/api/content/{uuid.uuid4()}/questions", headers=_auth(token)
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_questions_returns_401_without_token(
    client: AsyncClient,
) -> None:
    r = await client.get(f"/api/content/{uuid.uuid4()}/questions")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_get_questions_returns_503_when_ai_unavailable(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register(client)
    content = await _create_content(db_session)

    with patch(
        "app.api.routes.content.ai_integration.generate_questions",
        new=AsyncMock(side_effect=RuntimeError("OPENAI_API_KEY is not configured")),
    ):
        r = await client.get(
            f"/api/content/{content.id}/questions", headers=_auth(token)
        )

    assert r.status_code == 503


@pytest.mark.asyncio
async def test_get_questions_returns_503_when_ai_returns_empty(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    token = await _register(client)
    content = await _create_content(db_session)

    with patch(
        "app.api.routes.content.ai_integration.generate_questions",
        new=AsyncMock(return_value=[]),
    ):
        r = await client.get(
            f"/api/content/{content.id}/questions", headers=_auth(token)
        )

    assert r.status_code == 503
