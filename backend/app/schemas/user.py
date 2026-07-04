import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

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


# Alias used by the settings endpoints so the public name matches the milestone spec.
UserProfileResponse = UserResponse


class UpdateUserRequest(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=50)
    native_language: str | None = Field(default=None, min_length=2, max_length=10)
    target_language: str | None = Field(default=None, min_length=2, max_length=10)
    cefr_level: CEFRLevel | None = None


# Alias so routes can import by the spec name.
UpdateProfileRequest = UpdateUserRequest


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountRequest(BaseModel):
    """Password confirmation required before irreversible account deletion."""

    password: str = Field(min_length=1)
