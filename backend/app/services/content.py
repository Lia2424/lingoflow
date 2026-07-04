import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.models.enums import CEFRLevel, SourceType
from app.repositories.content import ContentRepository
from app.schemas.content import ContentListResponse, ContentResponse, InteractRequest


class ContentService:
    def __init__(self, repo: ContentRepository) -> None:
        self._repo = repo

    async def list(
        self,
        language: str | None,
        cefr_level: CEFRLevel | None,
        source_type: SourceType | None,
        page: int,
        page_size: int,
    ) -> ContentListResponse:
        items, total = await self._repo.list(
            language=language,
            cefr_level=cefr_level,
            source_type=source_type,
            page=page,
            page_size=page_size,
        )
        return ContentListResponse(
            items=[ContentResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_by_id(self, content_id: uuid.UUID) -> ContentResponse:
        content = await self._repo.get_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )
        return ContentResponse.model_validate(content)

    async def interact(
        self,
        user_id: str,
        content_id: uuid.UUID,
        data: InteractRequest,
    ) -> None:
        # Verify content exists before recording an interaction. This is a
        # best-effort check — see the IntegrityError handling below for the
        # race where content is deleted between this check and the upsert.
        content = await self._repo.get_by_id(content_id)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            )
        try:
            await self._repo.upsert_interaction(
                user_id=uuid.UUID(user_id),
                content_id=content_id,
                data=data,
            )
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found",
            ) from None
