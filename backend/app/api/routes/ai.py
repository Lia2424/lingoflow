from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep

router = APIRouter()

# ── Milestone 3 implementation ─────────────────────────────────────────────
# All AI endpoints cache responses in Redis to avoid redundant LLM calls.
# Uses OpenAI structured outputs for deterministic JSON responses.


@router.post("/explain")
async def explain_sentence(
    user_id: CurrentUserIdDep, db: DatabaseDep
) -> dict[str, Any]:
    """
    Explain a sentence in the context of its source content item.
    Returns a plain-language breakdown + grammar notes in the user's
    native language.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.post("/difficulty")
async def estimate_difficulty(user_id: CurrentUserIdDep) -> dict[str, Any]:
    """
    Estimate the CEFR level of a provided text snippet.
    Result is returned as a structured JSON object with level + confidence.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.get("/quiz/{content_id}")
async def get_or_generate_quiz(
    content_id: str,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> dict[str, Any]:
    """
    Fetch a previously generated quiz, or generate and persist a new one.
    Quiz questions are stored in the quizzes table as JSONB.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.get("/immersion/plan")
async def get_immersion_plan(
    user_id: CurrentUserIdDep, db: DatabaseDep
) -> dict[str, Any]:
    """Return the user's current AI-generated immersion plan."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.post("/immersion/plan/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_immersion_plan(
    user_id: CurrentUserIdDep, db: DatabaseDep
) -> dict[str, Any]:
    """Trigger a new immersion plan generation based on current profile."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover
