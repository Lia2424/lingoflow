import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CEFRLevel, InteractionStatus, SourceType


class ContentResponse(BaseModel):
    id: uuid.UUID
    title: str
    url: str
    source_type: SourceType
    language: str
    cefr_level: CEFRLevel
    thumbnail_url: str | None
    description: str | None
    duration_seconds: int | None
    published_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    items: list[ContentResponse]
    total: int
    page: int
    page_size: int


class InteractRequest(BaseModel):
    status: InteractionStatus
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        description=(
            "1-5 star rating. Omit (or send null) to leave any previously "
            "recorded rating unchanged — this field is never used to clear "
            "an existing rating, only to set one."
        ),
    )
