import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep
from app.repositories.user import UserRepository
from app.schemas.user import UpdateUserRequest, UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(user_id: CurrentUserIdDep, db: DatabaseDep) -> UserResponse:
    user = await UserRepository(db).get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UpdateUserRequest,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> UserResponse:
    repo = UserRepository(db)
    user = await repo.get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = await repo.update(user, data)
    return UserResponse.model_validate(updated)


@router.get("/me/stats")
async def get_stats(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    # Milestone 5: aggregate streak, words learned, content completed.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/me/interactions")
async def get_interactions(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    # Milestone 2: return paginated user–content interaction history.
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
