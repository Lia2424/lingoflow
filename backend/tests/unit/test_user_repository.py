"""
Unit tests for UserRepository.

Uses an in-memory SQLite database so no running Postgres is required.
SQLAlchemy translates the PostgreSQL UUID type to VARCHAR for SQLite automatically.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import (
    user as _user_module,  # noqa: F401 — registers User with Base.metadata
)
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest

_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

_REGISTER_DATA = RegisterRequest(
    email="test@example.com",
    username="testuser",
    password="password123",
    native_language="en",
    target_language="es",
)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine(
        _SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession) -> None:
    repo = UserRepository(db_session)
    user = await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.hashed_password == "hashed_pw"
    assert user.native_language == "en"
    assert user.target_language == "es"
    assert user.is_active is True


@pytest.mark.asyncio
async def test_get_by_email_returns_user(db_session: AsyncSession) -> None:
    repo = UserRepository(db_session)
    await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    found = await repo.get_by_email("test@example.com")

    assert found is not None
    assert found.username == "testuser"


@pytest.mark.asyncio
async def test_get_by_email_is_case_insensitive(db_session: AsyncSession) -> None:
    repo = UserRepository(db_session)
    await repo.create(_REGISTER_DATA, hashed_password="hashed_pw")

    found = await repo.get_by_email("TEST@EXAMPLE.COM")

    assert found is not None
    assert found.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_by_email_returns_none_for_unknown(db_session: AsyncSession) -> None:
    repo = UserRepository(db_session)

    found = await repo.get_by_email("nobody@example.com")

    assert found is None
