import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from openai import OpenAIError
from pydantic import BaseModel

from app.core.dependencies import CurrentUserIdDep, DatabaseDep
from app.integrations import ai as ai_integration
from app.repositories.vocabulary import VocabularyRepository
from app.schemas.errors import (
    RESPONSES_401,
    RESPONSES_404,
    RESPONSES_409,
    RESPONSES_422,
)
from app.schemas.vocabulary import (
    ReviewRequest,
    VocabularyEntryCreate,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
    VocabularyListResponse,
)
from app.services.vocabulary import VocabularyService

router = APIRouter()


def _service(db: DatabaseDep) -> VocabularyService:
    return VocabularyService(VocabularyRepository(db))


# ── Review queue — must come before /{entry_id} to avoid route shadowing ─────


@router.get(
    "/review",
    response_model=list[VocabularyEntryResponse],
    responses={**RESPONSES_401},
)
async def get_review_queue(
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> list[VocabularyEntryResponse]:
    """Return up to 20 entries that are due for review, most overdue first."""
    return await _service(db).get_review_queue(user_id)


# ── Collection ────────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=VocabularyEntryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={**RESPONSES_401, **RESPONSES_409, **RESPONSES_422},
)
async def create_vocabulary_entry(
    data: VocabularyEntryCreate,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> VocabularyEntryResponse:
    """Save a new word to the authenticated user's vocabulary list."""
    return await _service(db).create(user_id, data)


@router.get(
    "",
    response_model=VocabularyListResponse,
    responses={**RESPONSES_401, **RESPONSES_422},
)
async def list_vocabulary(
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
    language: Annotated[str | None, Query(max_length=10)] = None,
    srs_level: Annotated[int | None, Query(ge=0, le=5)] = None,
    page: Annotated[int, Query(ge=1, le=100_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> VocabularyListResponse:
    """Return the authenticated user's vocabulary list with optional filters."""
    return await _service(db).list_entries(
        user_id=user_id,
        language=language,
        srs_level=srs_level,
        page=page,
        page_size=page_size,
    )


# ── Single entry ──────────────────────────────────────────────────────────────


@router.get(
    "/{entry_id}",
    response_model=VocabularyEntryResponse,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_422},
)
async def get_vocabulary_entry(
    entry_id: uuid.UUID,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> VocabularyEntryResponse:
    return await _service(db).get_by_id(user_id, entry_id)


@router.patch(
    "/{entry_id}",
    response_model=VocabularyEntryResponse,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_409, **RESPONSES_422},
)
async def update_vocabulary_entry(
    entry_id: uuid.UUID,
    data: VocabularyEntryUpdate,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> VocabularyEntryResponse:
    """Update word, language, definition, translation, or notes for an owned entry."""
    return await _service(db).update(user_id, entry_id, data)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_422},
)
async def delete_vocabulary_entry(
    entry_id: uuid.UUID,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> None:
    await _service(db).delete(user_id, entry_id)


@router.post(
    "/{entry_id}/review",
    response_model=VocabularyEntryResponse,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_422},
)
async def record_review(
    entry_id: uuid.UUID,
    data: ReviewRequest,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> VocabularyEntryResponse:
    """
    Record a flashcard review result.
    Correct advances the SRS level; incorrect resets it to 0 (due immediately).
    Returns the updated entry with the new srs_level and next_review_at.
    """
    return await _service(db).record_review(user_id, entry_id, data)


class DefinitionSuggestion(BaseModel):
    definition: str
    translation: str


@router.post(
    "/{entry_id}/suggest",
    response_model=DefinitionSuggestion,
    responses={
        **RESPONSES_401,
        **RESPONSES_404,
        503: {"description": "AI service unavailable"},
    },
)
async def suggest_definition(
    entry_id: uuid.UUID,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> DefinitionSuggestion:
    """Ask the AI to suggest a definition and translation for a saved word.

    The suggestion is returned for the user to preview — it is **not** saved
    automatically.  The frontend should let the user accept or discard it.
    """
    entry = await _service(db).get_by_id(user_id, entry_id)
    try:
        result = await ai_integration.generate_definition(
            word=entry.word,
            language=entry.language,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except OpenAIError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ai_integration.ai_unavailable_detail(exc),
        ) from exc

    return DefinitionSuggestion(
        definition=result["definition"],
        translation=result["translation"],
    )
