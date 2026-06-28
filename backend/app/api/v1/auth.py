from fastapi import APIRouter, HTTPException, status

router = APIRouter()

# ── Milestone 1 implementation ─────────────────────────────────────────────
# Each stub will be replaced with full handler + schema validation.


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register() -> dict:
    """Register a new user and return tokens."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/login")
async def login() -> dict:
    """Authenticate and return access + refresh tokens."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/refresh")
async def refresh_token() -> dict:
    """Exchange a valid refresh token for a new token pair (rotation)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout() -> None:
    """Invalidate the current refresh token."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
