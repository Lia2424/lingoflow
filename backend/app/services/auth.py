from fastapi import HTTPException, status
from jose import JWTError

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
        user = await self._repo.create(data, hashed_password=hashed)

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self._repo.get_by_email(data.email)

        if not user or not verify_password(data.password, user.hashed_password):
            # Intentionally vague — don't reveal whether the email exists
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
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
        except (JWTError, ValueError, KeyError):
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
        # Milestone 6: decode the token and add its jti to a Redis blocklist.
        # For now, logout is handled client-side by discarding the token.
        pass
