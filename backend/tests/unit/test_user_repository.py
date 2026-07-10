"""
Unit tests for UserRepository.

Uses an in-memory SQLite database so no running Postgres is required.
SQLAlchemy translates the PostgreSQL UUID type to VARCHAR for SQLite automatically.
"""

import pytest

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest

_REGISTER_DATA = RegisterRequest(
    email="test@example.com",
    username="testuser",
    password="password123",
    native_language="en",
    target_language="es",
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[User.__table__]],
    indirect=True,
)
async def test_create_user(sqlite_session) -> None:
    repo = UserRepository(sqlite_session)
    user = await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashed_pw"
    assert user.native_language == "en"
    assert user.target_language == "es"
    assert user.is_active is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[User.__table__]],
    indirect=True,
)
async def test_get_by_email_returns_user(sqlite_session) -> None:
    repo = UserRepository(sqlite_session)
    await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    found = await repo.get_by_email("test@example.com")

    assert found is not None
    assert found.username == "testuser"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[User.__table__]],
    indirect=True,
)
async def test_get_by_email_is_case_insensitive(sqlite_session) -> None:
    repo = UserRepository(sqlite_session)
    await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    found = await repo.get_by_email("TEST@EXAMPLE.COM")

    assert found is not None
    assert found.email == "test@example.com"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sqlite_session",
    [[User.__table__]],
    indirect=True,
)
async def test_get_by_email_returns_none_for_unknown(sqlite_session) -> None:
    repo = UserRepository(sqlite_session)

    found = await repo.get_by_email("nobody@example.com")

    assert found is None
