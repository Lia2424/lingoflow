import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VocabularyEntryCreate(BaseModel):
    word: str = Field(min_length=1, max_length=200)
    language: str = Field(min_length=2, max_length=10)
    definition: str | None = Field(default=None, max_length=2000)
    translation: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)
    content_id: uuid.UUID | None = None


class VocabularyEntryUpdate(BaseModel):
    word: str | None = Field(default=None, min_length=1, max_length=200)
    language: str | None = Field(default=None, min_length=2, max_length=10)
    definition: str | None = Field(default=None, max_length=2000)
    translation: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)


class VocabularyEntryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    content_id: uuid.UUID | None
    word: str
    language: str
    definition: str | None
    translation: str | None
    notes: str | None
    srs_level: int
    next_review_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VocabularyListResponse(BaseModel):
    items: list[VocabularyEntryResponse]
    total: int
    page: int
    page_size: int


class ReviewRequest(BaseModel):
    correct: bool
