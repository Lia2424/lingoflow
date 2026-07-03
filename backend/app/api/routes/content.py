import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep
from app.models.enums import CEFRLevel, SourceType
from app.repositories.content import ContentRepository
from app.schemas.content import ContentListResponse, ContentResponse, InteractRequest
from app.schemas.errors import RESPONSES_401, RESPONSES_404, RESPONSES_422
from app.services.content import ContentService

router = APIRouter()


def _service(db: DatabaseDep) -> ContentService:
    return ContentService(ContentRepository(db))


@router.get(
    "",
    response_model=ContentListResponse,
    responses={**RESPONSES_401, **RESPONSES_422},
)
async def list_content(
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
    language: str | None = None,
    cefr_level: CEFRLevel | None = None,
    source_type: SourceType | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ContentListResponse:
    return await _service(db).list(
        language=language,
        cefr_level=cefr_level,
        source_type=source_type,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_422},
)
async def get_content(
    content_id: uuid.UUID,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> ContentResponse:
    return await _service(db).get_by_id(content_id)


@router.post(
    "/{content_id}/interact",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**RESPONSES_401, **RESPONSES_404, **RESPONSES_422},
)
async def interact_with_content(
    content_id: uuid.UUID,
    data: InteractRequest,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> None:
    await _service(db).interact(
        user_id=user_id,
        content_id=content_id,
        data=data,
    )
