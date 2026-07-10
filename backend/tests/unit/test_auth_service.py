"""Unit tests for AuthService with a mocked repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.security import create_refresh_token, hash_password
from app.models.enums import CEFRLevel
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth import AuthService

_REGISTER = RegisterRequest(
    email="user@example.com",
    username="user",
    password="securepassword123",
    native_language="en",
    target_language="es",
)


def _user(
    *,
    email: str = "user@example.com",
    password: str = "securepassword123",
    is_active: bool = True,
) -> MagicMock:
    user = MagicMock()
    user.id = uuid.uuid4()
    user.email = email
    user.username = "user"
    user.hashed_password = hash_password(password)
    user.native_language = "en"
    user.target_language = "es"
    user.cefr_level = CEFRLevel.B1
    user.is_active = is_active
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)
    return user


@pytest.mark.asyncio
async def test_register_returns_tokens_for_new_user() -> None:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(return_value=_user())
    service = AuthService(repo)

    result = await service.register(_REGISTER)

    assert result.access_token
    assert result.refresh_token
    assert result.user.email == "user@example.com"


@pytest.mark.asyncio
async def test_register_raises_409_when_email_exists() -> None:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=_user())
    service = AuthService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.register(_REGISTER)

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_register_raises_409_on_integrity_error() -> None:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock(side_effect=IntegrityError("", {}, Exception()))
    service = AuthService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.register(_REGISTER)

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_login_raises_401_for_unknown_email() -> None:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    service = AuthService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.login(
            LoginRequest(email="missing@example.com", password="securepassword123")
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_login_raises_401_for_inactive_user() -> None:
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=_user(is_active=False))
    service = AuthService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.login(
            LoginRequest(email="user@example.com", password="securepassword123")
        )

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_returns_new_tokens_for_valid_refresh_token() -> None:
    user = _user()
    repo = MagicMock()
    repo.get_by_id_str = AsyncMock(return_value=user)
    service = AuthService(repo)
    refresh_token = create_refresh_token(str(user.id))

    result = await service.refresh(refresh_token)

    assert result.access_token
    assert result.user.email == user.email


@pytest.mark.asyncio
async def test_refresh_raises_401_for_access_token() -> None:
    user = _user()
    repo = MagicMock()
    service = AuthService(repo)
    from app.core.security import create_access_token

    with pytest.raises(HTTPException) as exc:
        await service.refresh(create_access_token(str(user.id)))

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_refresh_raises_401_for_missing_user() -> None:
    user = _user()
    repo = MagicMock()
    repo.get_by_id_str = AsyncMock(return_value=None)
    service = AuthService(repo)

    with pytest.raises(HTTPException) as exc:
        await service.refresh(create_refresh_token(str(user.id)))

    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_logout_accepts_valid_refresh_token() -> None:
    user = _user()
    service = AuthService(MagicMock())

    await service.logout(create_refresh_token(str(user.id)))


@pytest.mark.asyncio
async def test_logout_raises_401_for_invalid_token() -> None:
    service = AuthService(MagicMock())

    with pytest.raises(HTTPException) as exc:
        await service.logout("not-a-token")

    assert exc.value.status_code == 401
