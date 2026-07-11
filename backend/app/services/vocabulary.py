"""
VocabularyService — business logic for vocabulary CRUD and SRS review.

SM-2 scheduling (simplified):
  - Correct answer: srs_level += 1 (capped at 5).
    Interval grows exponentially: [1, 3, 7, 14, 30] days for levels 1-5.
  - Wrong answer: srs_level resets to 0, due immediately (next_review_at = now).
  - Level 0 (unseen / just reset): due immediately.
"""

import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.repositories.vocabulary import VocabularyRepository
from app.schemas.vocabulary import (
    ReviewRequest,
    VocabularyEntryCreate,
    VocabularyEntryResponse,
    VocabularyEntryUpdate,
    VocabularyListResponse,
)

# Days until next review for each SRS level (index = level after answering).
_SRS_INTERVALS: dict[int, int] = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
_SRS_MAX = 5


def _next_review(srs_level: int, now: datetime) -> datetime:
    days = _SRS_INTERVALS.get(srs_level, 0)
    return now + timedelta(days=days)


class VocabularyService:
    def __init__(self, repo: VocabularyRepository) -> None:
        self._repo = repo

    async def create(
        self,
        user_id: str,
        data: VocabularyEntryCreate,
    ) -> VocabularyEntryResponse:
        try:
            entry = await self._repo.create(uuid.UUID(user_id), data)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"'{data.word}' already exists in your "
                    f"{data.language.upper()} vocabulary list."
                ),
            ) from None
        return VocabularyEntryResponse.model_validate(entry)

    async def list_entries(
        self,
        user_id: str,
        language: str | None,
        srs_level: int | None,
        page: int,
        page_size: int,
    ) -> VocabularyListResponse:
        items, total = await self._repo.list_entries(
            user_id=uuid.UUID(user_id),
            language=language,
            srs_level=srs_level,
            page=page,
            page_size=page_size,
        )
        return VocabularyListResponse(
            items=[VocabularyEntryResponse.model_validate(e) for e in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_by_id(
        self,
        user_id: str,
        entry_id: uuid.UUID,
    ) -> VocabularyEntryResponse:
        entry = await self._repo.get_by_id(entry_id, uuid.UUID(user_id))
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary entry not found",
            )
        return VocabularyEntryResponse.model_validate(entry)

    async def update(
        self,
        user_id: str,
        entry_id: uuid.UUID,
        data: VocabularyEntryUpdate,
    ) -> VocabularyEntryResponse:
        entry = await self._repo.get_by_id(entry_id, uuid.UUID(user_id))
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary entry not found",
            )
        current_word = entry.word
        current_language = entry.language
        try:
            updated = await self._repo.update(entry, data)
        except IntegrityError:
            word = data.word or current_word
            language = (data.language or current_language).upper()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(f"'{word}' already exists in your {language} vocabulary list."),
            ) from None
        return VocabularyEntryResponse.model_validate(updated)

    async def delete(self, user_id: str, entry_id: uuid.UUID) -> None:
        entry = await self._repo.get_by_id(entry_id, uuid.UUID(user_id))
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary entry not found",
            )
        await self._repo.delete(entry)

    async def get_review_queue(
        self,
        user_id: str,
    ) -> list[VocabularyEntryResponse]:
        now = datetime.now(UTC)
        entries = await self._repo.get_due_for_review(uuid.UUID(user_id), now)
        return [VocabularyEntryResponse.model_validate(e) for e in entries]

    async def record_review(
        self,
        user_id: str,
        entry_id: uuid.UUID,
        data: ReviewRequest,
    ) -> VocabularyEntryResponse:
        entry = await self._repo.get_by_id(entry_id, uuid.UUID(user_id))
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vocabulary entry not found",
            )

        now = datetime.now(UTC)
        if data.correct:
            new_level = min(entry.srs_level + 1, _SRS_MAX)
            next_at = _next_review(new_level, now)
        else:
            new_level = 0
            next_at = now  # due immediately for a wrong answer

        updated = await self._repo.save_review(entry, new_level, next_at)
        return VocabularyEntryResponse.model_validate(updated)
