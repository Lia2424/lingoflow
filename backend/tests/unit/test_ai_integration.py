"""Unit tests for app/integrations/ai.py.

All OpenAI network calls are mocked — no real API key or internet access required.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.integrations.ai import classify_cefr, generate_definition, generate_questions
from app.models.enums import CEFRLevel


# ── Helpers ───────────────────────────────────────────────────────────────────


def _mock_completion(content: str) -> MagicMock:
    """Build a minimal mock that looks like an openai ChatCompletion response."""
    message = MagicMock()
    message.content = content
    choice = MagicMock()
    choice.message = message
    completion = MagicMock()
    completion.choices = [choice]
    return completion


def _patch_client(content: str) -> Any:
    """Patch _client() so chat.completions.create returns *content* as a string."""
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_mock_completion(content)
    )
    return patch("app.integrations.ai._client", return_value=mock_client)


# ── classify_cefr ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_classify_cefr_parses_valid_level() -> None:
    with _patch_client('{"level": "B2"}'):
        result = await classify_cefr("La Bamba", "A classic Spanish song", "es")

    assert result == CEFRLevel.B2


@pytest.mark.asyncio
async def test_classify_cefr_handles_lowercase_level() -> None:
    with _patch_client('{"level": "a1"}'):
        result = await classify_cefr("Lesson 1", "Absolute beginner content", "es")

    assert result == CEFRLevel.A1


@pytest.mark.asyncio
async def test_classify_cefr_falls_back_to_b1_on_unknown_level() -> None:
    with _patch_client('{"level": "EXTREME"}'):
        result = await classify_cefr("Something weird", "...", "en")

    assert result == CEFRLevel.B1


@pytest.mark.asyncio
async def test_classify_cefr_falls_back_to_b1_on_malformed_json() -> None:
    with _patch_client("not json at all"):
        result = await classify_cefr("Bad response", "...", "en")

    assert result == CEFRLevel.B1


@pytest.mark.asyncio
async def test_classify_cefr_falls_back_to_b1_on_empty_response() -> None:
    with _patch_client("{}"):
        result = await classify_cefr("Empty", "", "fr")

    assert result == CEFRLevel.B1


@pytest.mark.asyncio
async def test_classify_cefr_raises_runtime_error_when_no_api_key() -> None:
    with patch("app.integrations.ai.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            await classify_cefr("Test", "Test", "en")


# ── generate_definition ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_definition_returns_definition_and_translation() -> None:
    payload = json.dumps(
        {"definition": "A friendly greeting", "translation": "hello"}
    )
    with _patch_client(payload):
        result = await generate_definition("hola", "es")

    assert result["definition"] == "A friendly greeting"
    assert result["translation"] == "hello"


@pytest.mark.asyncio
async def test_generate_definition_handles_missing_keys() -> None:
    with _patch_client("{}"):
        result = await generate_definition("hola", "es")

    assert result["definition"] == ""
    assert result["translation"] == ""


@pytest.mark.asyncio
async def test_generate_definition_handles_malformed_json() -> None:
    with _patch_client("this is not json"):
        result = await generate_definition("hola", "es")

    assert result["definition"] == ""
    assert result["translation"] == ""


@pytest.mark.asyncio
async def test_generate_definition_raises_runtime_error_when_no_api_key() -> None:
    with patch("app.integrations.ai.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            await generate_definition("word", "es")


@pytest.mark.asyncio
async def test_generate_definition_includes_context_sentence_in_prompt() -> None:
    """Verify the context sentence is passed through to the API call."""
    payload = json.dumps(
        {"definition": "To run fast", "translation": "correr"}
    )
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_mock_completion(payload)
    )
    with patch("app.integrations.ai._client", return_value=mock_client):
        await generate_definition("correr", "es", context_sentence="Él corre rápido")

    call_kwargs = mock_client.chat.completions.create.call_args
    messages = call_kwargs.kwargs["messages"]
    user_message = next(m for m in messages if m["role"] == "user")
    assert "Él corre rápido" in user_message["content"]


# ── generate_questions ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_generate_questions_returns_validated_questions() -> None:
    payload = json.dumps(
        {
            "questions": [
                {
                    "question": "What is the topic?",
                    "options": ["Music", "Sports", "Food", "Travel"],
                    "answer_index": 0,
                },
                {
                    "question": "Who is the artist?",
                    "options": ["Piaf", "Aznavour", "Brel", "Hardy"],
                    "answer_index": 2,
                },
            ]
        }
    )
    with _patch_client(payload):
        result = await generate_questions("La Vie en Rose", "A French song", "fr", n=2)

    assert len(result) == 2
    assert result[0]["question"] == "What is the topic?"
    assert result[0]["options"] == ["Music", "Sports", "Food", "Travel"]
    assert result[0]["answer_index"] == 0
    assert result[1]["answer_index"] == 2


@pytest.mark.asyncio
async def test_generate_questions_filters_malformed_items() -> None:
    """Questions missing required fields or with wrong option count are dropped."""
    payload = json.dumps(
        {
            "questions": [
                # valid
                {
                    "question": "Good question?",
                    "options": ["A", "B", "C", "D"],
                    "answer_index": 1,
                },
                # invalid — only 3 options
                {
                    "question": "Bad question?",
                    "options": ["A", "B", "C"],
                    "answer_index": 0,
                },
                # invalid — answer_index out of range
                {
                    "question": "Out of range?",
                    "options": ["A", "B", "C", "D"],
                    "answer_index": 5,
                },
            ]
        }
    )
    with _patch_client(payload):
        result = await generate_questions("Test content", "desc", "en", n=5)

    assert len(result) == 1
    assert result[0]["question"] == "Good question?"


@pytest.mark.asyncio
async def test_generate_questions_returns_empty_on_malformed_json() -> None:
    with _patch_client("garbage"):
        result = await generate_questions("Content", "desc", "en")

    assert result == []


@pytest.mark.asyncio
async def test_generate_questions_caps_at_n() -> None:
    questions = [
        {
            "question": f"Q{i}?",
            "options": ["A", "B", "C", "D"],
            "answer_index": 0,
        }
        for i in range(10)
    ]
    payload = json.dumps({"questions": questions})
    with _patch_client(payload):
        result = await generate_questions("Content", "desc", "en", n=3)

    assert len(result) == 3


@pytest.mark.asyncio
async def test_generate_questions_raises_runtime_error_when_no_api_key() -> None:
    with patch("app.integrations.ai.settings") as mock_settings:
        mock_settings.OPENAI_API_KEY = ""
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            await generate_questions("Content", "desc", "en")
