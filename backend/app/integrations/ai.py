"""AI integration — thin async wrapper around OpenAI chat completions.

All functions are best-effort: if the API key is missing or the service is
unavailable they raise ``RuntimeError`` so callers can return 503 instead of
crashing with a 500.

Responses use ``response_format={"type": "json_object"}`` for deterministic
output; each function includes a defensive fallback in case the model
returns unexpected JSON.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, TypedDict

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    InternalServerError,
    OpenAIError,
    RateLimitError,
)

from app.core.config import settings
from app.models.enums import CEFRLevel


class QuestionDict(TypedDict):
    question: str
    options: list[str]
    answer_index: int

logger = logging.getLogger(__name__)

_CEFR_VALUES = {level.value for level in CEFRLevel}
_RETRYABLE_ERRORS = (
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)


def _client() -> AsyncOpenAI:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured — AI features are unavailable."
        )
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        timeout=60.0,
        max_retries=0,
    )


async def _chat_completion(**kwargs: Any):
    """Call chat completions with retries for transient provider errors."""
    client = _client()
    delays = (1.0, 2.0, 4.0, 8.0)
    for attempt, delay in enumerate(delays):
        try:
            return await client.chat.completions.create(**kwargs)
        except _RETRYABLE_ERRORS as exc:
            if attempt == len(delays) - 1:
                logger.warning(
                    "OpenAI %s after %d attempts: %s",
                    type(exc).__name__,
                    len(delays),
                    exc,
                )
                raise
            logger.warning(
                "OpenAI %s (attempt %d/%d), retrying in %.0fs: %s",
                type(exc).__name__,
                attempt + 1,
                len(delays),
                delay,
                exc,
            )
            await asyncio.sleep(delay)
        except OpenAIError:
            raise


def _coerce_answer_index(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and 0 <= value <= 3:
        return value
    if isinstance(value, str) and value.isdigit():
        index = int(value)
        return index if 0 <= index <= 3 else None
    return None


def _validate_questions(raw_questions: list[Any], n: int) -> list[QuestionDict]:
    validated: list[QuestionDict] = []
    for q in raw_questions[:n]:
        if not isinstance(q, dict):
            continue
        options = q.get("options", [])
        answer_index = _coerce_answer_index(q.get("answer_index"))
        if (
            isinstance(q.get("question"), str)
            and isinstance(options, list)
            and len(options) == 4
            and answer_index is not None
        ):
            validated.append(
                {
                    "question": q["question"],
                    "options": [str(o) for o in options],
                    "answer_index": answer_index,
                }
            )
    return validated


def _parse_questions_payload(raw: str, n: int) -> list[QuestionDict]:
    try:
        data = json.loads(raw)
        questions_raw = data.get("questions", [])
        questions = questions_raw if isinstance(questions_raw, list) else []
    except json.JSONDecodeError:
        questions = []
    return _validate_questions(questions, n)


async def classify_cefr(
    title: str,
    description: str,
    language: str,
) -> CEFRLevel:
    """Classify the CEFR difficulty level of a piece of content.

    Args:
        title: Content title.
        description: Short description or subtitle.
        language: BCP-47 language code of the content (e.g. ``"es"``).

    Returns:
        A :class:`~app.models.enums.CEFRLevel`.  Falls back to ``B1`` if the
        model returns an unrecognised value.

    Raises:
        RuntimeError: If ``OPENAI_API_KEY`` is not set.
        OpenAIError: On network / quota errors.
    """
    prompt = (
        f"Language: {language}\n"
        f"Title: {title}\n"
        f"Description: {description or '(none)'}"
    )
    try:
        response = await _chat_completion(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a language-learning expert. "
                        "Given a content title and description, classify its "
                        "CEFR level for a language learner. "
                        "Valid levels: A1, A2, B1, B2, C1, C2. "
                        'Respond in JSON format with exactly: {"level": "<LEVEL>"}'
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=20,
            temperature=0,
        )
    except OpenAIError as exc:
        logger.warning("classify_cefr OpenAI error: %s", exc)
        raise

    raw = response.choices[0].message.content or "{}"
    try:
        level_str = json.loads(raw).get("level", "").upper()
    except json.JSONDecodeError:
        level_str = ""

    if level_str in _CEFR_VALUES:
        return CEFRLevel(level_str)

    logger.warning("classify_cefr: unexpected level %r — defaulting to B1", level_str)
    return CEFRLevel.B1


async def generate_definition(
    word: str,
    language: str,
    context_sentence: str | None = None,
) -> dict[str, str]:
    """Generate a definition and translation for a vocabulary word.

    Args:
        word: The word or phrase to define.
        language: BCP-47 code of the word's language (e.g. ``"es"``).
        context_sentence: Optional sentence the word appeared in for better
            contextual accuracy.

    Returns:
        ``{"definition": "...", "translation": "..."}`` — both in English.

    Raises:
        RuntimeError: If ``OPENAI_API_KEY`` is not set.
        OpenAIError: On network / quota errors.
    """
    context_part = (
        f"\nContext sentence: {context_sentence}" if context_sentence else ""
    )
    prompt = f"Word: {word}\nLanguage: {language}{context_part}"

    try:
        response = await _chat_completion(
            model=settings.OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a language tutor. Given a word and its language, "
                        "provide a concise English definition and an English "
                        "translation. If a context sentence is provided, use it "
                        "to give the contextually correct meaning. "
                        "Respond in JSON format: "
                        '{"definition": "<English definition>", '
                        '"translation": "<English translation>"}'
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.3,
        )
    except OpenAIError as exc:
        logger.warning("generate_definition OpenAI error: %s", exc)
        raise

    raw = response.choices[0].message.content or "{}"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    return {
        "definition": str(data.get("definition") or ""),
        "translation": str(data.get("translation") or ""),
    }


async def generate_questions(
    content_title: str,
    content_description: str,
    language: str,
    n: int = 5,
) -> list[QuestionDict]:
    """Generate multiple-choice comprehension questions for a piece of content.

    Args:
        content_title: Title of the content item.
        content_description: Description or summary.
        language: BCP-47 code for the content's language (e.g. ``"es"``).
        n: Number of questions to generate (1–10).

    Returns:
        A list of dicts, each with keys:
        ``{"question": str, "options": list[str], "answer_index": int}``

    Raises:
        RuntimeError: If ``OPENAI_API_KEY`` is not set.
        OpenAIError: On network / quota errors.
    """
    n = max(1, min(n, 10))
    prompt = (
        f"Content language: {language}\n"
        f"Title: {content_title}\n"
        f"Description: {content_description or '(none)'}\n"
        f"Number of questions: {n}"
    )
    system_prompt = (
        "You are a language-learning quiz designer. "
        "Create multiple-choice comprehension questions about "
        "the given content to help learners test their "
        "understanding. Each question must have exactly 4 "
        "options and one correct answer. "
        "Respond in JSON format: "
        '{"questions": [{"question": "...", '
        '"options": ["A", "B", "C", "D"], '
        '"answer_index": 0}]}'
    )

    validated: list[QuestionDict] = []
    for attempt in range(2):
        try:
            response = await _chat_completion(
                model=settings.OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1200,
                temperature=0.5,
            )
        except OpenAIError as exc:
            logger.warning("generate_questions OpenAI error: %s", exc)
            raise

        raw = response.choices[0].message.content or "{}"
        validated = _parse_questions_payload(raw, n)
        if validated:
            return validated

        logger.warning(
            "generate_questions: attempt %d/%d returned no valid questions",
            attempt + 1,
            2,
        )

    return validated
