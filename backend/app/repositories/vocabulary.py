import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import VocabularyEntry
from app.schemas.vocabulary import VocabularyEntryCreate, VocabularyEntryUpdate

_REVIEW_BATCH = 20  # max entries returned by get_due_for_review


class VocabularyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ── CRUD ─────────────────────────────────────────────────────────────────

    async def create(
        self,
        user_id: uuid.UUID,
        data: VocabularyEntryCreate,
    ) -> VocabularyEntry:
        """
        Insert a new entry.

        Raises sqlalchemy.exc.IntegrityError when (user_id, word, language)
        already exists — callers should translate this to a 409.
        """
        entry = VocabularyEntry(
            user_id=user_id,
            content_id=data.content_id,
            word=data.word.strip(),
            language=data.language.lower(),
            definition=data.definition,
            translation=data.translation,
            notes=data.notes,
        )
        self._db.add(entry)
        try:
            await self._db.commit()
            await self._db.refresh(entry)
        except IntegrityError:
            await self._db.rollback()
            raise
        return entry

    async def list_entries(
        self,
        user_id: uuid.UUID,
        language: str | None,
        srs_level: int | None,
        page: int,
        page_size: int,
    ) -> tuple[list[VocabularyEntry], int]:
        """Return (items, total) for the given filters and page."""
        base = select(VocabularyEntry).where(VocabularyEntry.user_id == user_id)

        if language:
            base = base.where(VocabularyEntry.language == language.lower())
        if srs_level is not None:
            base = base.where(VocabularyEntry.srs_level == srs_level)

        total_result = await self._db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = total_result.scalar_one()

        items_result = await self._db.execute(
            base.order_by(VocabularyEntry.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(items_result.scalars().all()), total

    async def get_by_id(
        self,
        entry_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> VocabularyEntry | None:
        """Return the entry only if it belongs to user_id."""
        result = await self._db.execute(
            select(VocabularyEntry).where(
                VocabularyEntry.id == entry_id,
                VocabularyEntry.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        entry: VocabularyEntry,
        data: VocabularyEntryUpdate,
    ) -> VocabularyEntry:
        """Apply non-None fields from data to entry and persist."""
        if data.definition is not None:
            entry.definition = data.definition
        if data.translation is not None:
            entry.translation = data.translation
        if data.notes is not None:
            entry.notes = data.notes
        await self._db.commit()
        await self._db.refresh(entry)
        return entry

    async def delete(self, entry: VocabularyEntry) -> None:
        await self._db.delete(entry)
        await self._db.commit()

    # ── SRS / review ─────────────────────────────────────────────────────────

    async def get_due_for_review(
        self,
        user_id: uuid.UUID,
        now: datetime,
    ) -> list[VocabularyEntry]:
        """
        Return up to _REVIEW_BATCH entries due for review, ordered by urgency
        (most overdue first, then newly added entries with null next_review_at).
        """
        result = await self._db.execute(
            select(VocabularyEntry)
            .where(
                VocabularyEntry.user_id == user_id,
                (VocabularyEntry.next_review_at <= now)
                | (VocabularyEntry.next_review_at.is_(None)),
            )
            .order_by(
                VocabularyEntry.next_review_at.asc().nullsfirst(),
            )
            .limit(_REVIEW_BATCH)
        )
        return list(result.scalars().all())

    async def save_review(
        self,
        entry: VocabularyEntry,
        new_srs_level: int,
        next_review_at: datetime,
    ) -> VocabularyEntry:
        entry.srs_level = new_srs_level
        entry.next_review_at = next_review_at
        await self._db.commit()
        await self._db.refresh(entry)
        return entry
