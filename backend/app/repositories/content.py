import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.enums import CEFRLevel, SourceType
from app.models.user_content_interaction import UserContentInteraction
from app.schemas.content import InteractRequest


class ContentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list(
        self,
        language: str | None,
        cefr_level: CEFRLevel | None,
        source_type: SourceType | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Content], int]:
        """Return (items, total) for the given filters and page."""
        base = select(Content)

        if language:
            base = base.where(Content.language == language.lower())
        if cefr_level:
            base = base.where(Content.cefr_level == cefr_level)
        if source_type:
            base = base.where(Content.source_type == source_type)

        total_result = await self._db.execute(
            select(func.count()).select_from(base.subquery())
        )
        total: int = total_result.scalar_one()

        items_result = await self._db.execute(
            base.order_by(Content.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(items_result.scalars().all())
        return items, total

    async def get_by_id(self, content_id: uuid.UUID) -> Content | None:
        result = await self._db.execute(select(Content).where(Content.id == content_id))
        return result.scalar_one_or_none()

    async def upsert_interaction(
        self,
        user_id: uuid.UUID,
        content_id: uuid.UUID,
        data: InteractRequest,
    ) -> None:
        """
        Insert or update the interaction row for (user_id, content_id).

        Omitting `rating` (leaving it None) preserves whatever rating was
        previously stored, via COALESCE against the existing row — it does
        NOT null out an existing rating. This matches InteractRequest's
        documented contract. There is currently no way to explicitly clear
        a rating once set; that would need a separate sentinel value.

        Raises sqlalchemy.exc.IntegrityError if content_id no longer exists
        (FK violation) — callers should catch this to return a 404 rather
        than letting it bubble up as a 500.
        """
        insert_stmt = pg_insert(UserContentInteraction).values(
            user_id=user_id,
            content_id=content_id,
            status=data.status,
            rating=data.rating,
        )
        stmt = insert_stmt.on_conflict_do_update(
            constraint="uq_user_content",
            set_={
                "status": insert_stmt.excluded.status,
                "rating": func.coalesce(
                    insert_stmt.excluded.rating, UserContentInteraction.rating
                ),
                "updated_at": func.now(),
            },
        )
        try:
            await self._db.execute(stmt)
            await self._db.commit()
        except IntegrityError:
            await self._db.rollback()
            raise
