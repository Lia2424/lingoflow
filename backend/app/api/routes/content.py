from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep

router = APIRouter()

# ── Milestone 2 implementation ─────────────────────────────────────────────


@router.get("")
async def list_content(
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
    language: str | None = None,
    cefr: str | None = None,
    type: str | None = None,
    q: str | None = None,
    cursor: str | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    """
    Discovery feed. Supports CEFR filter, content type, full-text search,
    and cursor-based pagination (stable under concurrent inserts).
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.get("/{content_id}")
async def get_content(
    content_id: str,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> dict[str, Any]:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_content(db: DatabaseDep, user_id: CurrentUserIdDep) -> dict[str, Any]:
    """Admin-only: add a new content item."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.patch("/{content_id}")
async def update_content(
    content_id: str,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> dict[str, Any]:
    """Admin-only: update content metadata."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover


@router.post("/{content_id}/interact", status_code=status.HTTP_204_NO_CONTENT)
async def interact_with_content(
    content_id: str,
    db: DatabaseDep,
    user_id: CurrentUserIdDep,
) -> None:
    """Record a user–content interaction (save, mark read, like, progress)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)  # pragma: no cover
