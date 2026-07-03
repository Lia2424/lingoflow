import jwt
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse

# Pre-computed hash used when the requested email doesn't exist.
# Running verify_password against this normalises response time and prevents
# timing-based email enumeration (bcrypt takes ~100ms; skipping it leaks ~99ms).
_DUMMY_HASH = hash_password("dummy-password-for-timing-safety")


class AuthService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def register(self, data: RegisterRequest) -> TokenResponse:
        existing = await self._repo.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        hashed = hash_password(data.password)
        try:
            user = await self._repo.create(data, hashed_password=hashed)
        except IntegrityError:
            # Two concurrent registrations with the same email — the DB
            # unique constraint caught the race the application check missed.
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            ) from None

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)

        # Always call verify_password to keep response time constant.
        # Short-circuiting on a missing user would leak ~100ms and allow
        # attackers to enumerate valid emails via timing.
        candidate_hash = user.hashed_password if user else _DUMMY_HASH
        password_ok = verify_password(data.password, candidate_hash)

        if not user or not password_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            # Use 401 rather than 403 to avoid confirming the email exists
            # (a 403 with correct credentials reveals a valid account).
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            user=UserResponse.model_validate(user),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
            user_id: str = payload["sub"]
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from None

        user = await self._repo.get_by_id_str(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
            )

        # Rotate: issue a brand new pair, old refresh token is implicitly abandoned.
        # A token blocklist (Redis) will be added in Milestone 6 for full revocation.
        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            user=UserResponse.model_validate(user),
        )

    async def logout(self, refresh_token: str) -> None:
        # Validate the token so logout can't be called with garbage input.
        # Milestone 6: add payload["jti"] to a Redis blocklist for true revocation.
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise ValueError("Not a refresh token")
        except (jwt.PyJWTError, ValueError, KeyError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from None
