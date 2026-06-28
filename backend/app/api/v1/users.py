from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep

router = APIRouter()

# ── Milestone 1 implementation ─────────────────────────────────────────────


@router.get("/me")
async def get_me(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Return the authenticated user's profile."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.patch("/me")
async def update_me(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Update profile fields (username, CEFR level, target language, etc.)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/me/stats")
async def get_stats(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Return aggregated progress stats for the dashboard."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/me/interactions")
async def get_interactions(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Return paginated history of user–content interactions."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
