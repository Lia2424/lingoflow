from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUserIdDep, DatabaseDep

router = APIRouter()

# ── Milestone 4 implementation ─────────────────────────────────────────────


@router.get("")
async def list_vocabulary(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Return the authenticated user's saved vocabulary list."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("", status_code=status.HTTP_201_CREATED)
async def save_word(user_id: CurrentUserIdDep, db: DatabaseDep) -> dict:
    """Add a word to the user's vocabulary tracker."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.delete("/{vocab_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_word(
    vocab_id: str,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/content/{content_id}")
async def vocabulary_for_content(
    content_id: str,
    user_id: CurrentUserIdDep,
    db: DatabaseDep,
) -> dict:
    """
    Return vocabulary entries extracted from a specific content item.
    Results are cached after first extraction (Milestone 3).
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
