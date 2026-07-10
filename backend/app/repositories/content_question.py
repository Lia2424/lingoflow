from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.ai import QuestionDict
from app.models.content_question import ContentQuestion


class ContentQuestionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def acquire_generation_lock(self, content_id: uuid.UUID) -> None:
        """Serialize first-time question generation for one content item."""
        bind = self._db.get_bind()
        if bind.dialect.name != "postgresql":
            return
        lock_key = content_id.int % (2**31 - 1)
        await self._db.execute(select(func.pg_advisory_xact_lock(lock_key)))

    async def get_by_content_id(self, content_id: uuid.UUID) -> list[ContentQuestion]:
        """Return all cached questions for a content item, oldest first."""
        result = await self._db.execute(
            select(ContentQuestion)
            .where(ContentQuestion.content_id == content_id)
            .order_by(ContentQuestion.created_at.asc())
        )
        return list(result.scalars().all())

    async def create_bulk(
        self,
        content_id: uuid.UUID,
        questions: list[QuestionDict],
    ) -> list[ContentQuestion]:
        """Persist a batch of generated questions and return them.

        Each dict in *questions* must have keys:
        ``question`` (str), ``options`` (list[str]), ``answer_index`` (int).
        """
        rows = [
            ContentQuestion(
                content_id=content_id,
                question=str(q["question"]),
                options=q["options"],
                answer_index=q["answer_index"],
            )
            for q in questions
        ]
        self._db.add_all(rows)
        await self._db.commit()
        for row in rows:
            await self._db.refresh(row)
        return rows

    async def delete_by_content_id(self, content_id: uuid.UUID) -> None:
        """Remove all cached questions for a content item (force regeneration)."""
        rows = await self.get_by_content_id(content_id)
        for row in rows:
            await self._db.delete(row)
        await self._db.commit()
