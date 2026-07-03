import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.enums import CEFRLevel


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    native_language: str
    target_language: str
    cefr_level: CEFRLevel
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateUserRequest(BaseModel):
    username: str | None = None
    native_language: str | None = None
    target_language: str | None = None
    cefr_level: CEFRLevel | None = None
