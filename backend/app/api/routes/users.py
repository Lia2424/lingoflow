import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUserIdDep, DatabaseDep
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.errors import (
    PROTECTED_RESPONSES,
    RESPONSES_400,
    RESPONSES_404,
    RESPONSES_409,
)
from app.schemas.user import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    UpdateUserRequest,
    UserResponse,
)

router = APIRouter()


# ── Shared helper ─────────────────────────────────────────────────────────────


async def _get_user_or_404(user_id: str, db: DatabaseDep) -> User:
    user = await UserRepository(db).get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# ── Profile ───────────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    responses={**PROTECTED_RESPONSES, **RESPONSES_404},
)
async def get_me(user_id: CurrentUserIdDep, db: DatabaseDep) -> UserResponse:
    user = await _get_user_or_404(user_id, db)
    return UserResponse.model_validate(user)


@router.patch(
    "/me",
    response_model=UserResponse,
    responses={**PROTECTED_RESPONSES, **RESPONSES_404, **RESPONSES_409},
)
async def update_me(
    data: UpdateUserRequest,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> UserResponse:
    repo = UserRepository(db)
    user = await _get_user_or_404(user_id, db)
    try:
        updated = await repo.update(user, data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already taken",
        ) from None
    return UserResponse.model_validate(updated)


# ── Security ──────────────────────────────────────────────────────────────────


@router.post(
    "/me/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**PROTECTED_RESPONSES, **RESPONSES_400, **RESPONSES_404},
)
async def change_password(
    data: ChangePasswordRequest,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> None:
    """Verify the current password then replace it with the new one."""
    repo = UserRepository(db)
    user = await _get_user_or_404(user_id, db)

    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from the current password",
        )

    await repo.update_password(user, hash_password(data.new_password))


# ── Account deletion ──────────────────────────────────────────────────────────


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**PROTECTED_RESPONSES, **RESPONSES_400, **RESPONSES_404},
)
async def delete_me(
    data: DeleteAccountRequest,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> None:
    """Permanently delete the authenticated user's account.

    Requires password confirmation. All owned data (vocabulary, interactions)
    is deleted via ON DELETE CASCADE.
    """
    repo = UserRepository(db)
    user = await _get_user_or_404(user_id, db)

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is incorrect",
        )

    await repo.delete(user)


# ── Placeholders ──────────────────────────────────────────────────────────────


@router.get("/me/stats")
async def get_stats(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict[str, Any]:
    # Milestone 5: aggregate streak, words learned, content completed.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.get("/me/interactions")
async def get_interactions(
    user_id: CurrentUserIdDep, db: DatabaseDep
) -> dict[str, Any]:
    # Milestone 2: return paginated user–content interaction history.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover
