"""
Unit test configuration.

Uses SQLite in-memory with table-scoped metadata so unit tests stay isolated
from integration models (e.g. JSONB columns) registered on Base.metadata.
"""

from collections.abc import AsyncIterator, Sequence

import pytest
import pytest_asyncio
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base

_SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def sqlite_session(
    request: pytest.FixtureRequest,
) -> AsyncIterator[AsyncSession]:
    """In-memory SQLite session limited to tables declared by the test module."""
    tables: Sequence[Table] = request.param

    engine = create_async_engine(
        _SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.create_all(sync_conn, tables=list(tables))
        )

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(
            lambda sync_conn: Base.metadata.drop_all(sync_conn, tables=list(tables))
        )
    await engine.dispose()
