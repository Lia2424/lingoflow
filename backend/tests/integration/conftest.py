import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.limiter import limiter
from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Rate limiting fires in tests because all requests share the same loopback IP.
# Disable it for the whole integration test session.
limiter._enabled = False  # type: ignore[attr-defined]

# Replace only the database name (last path segment), not the username.
_base, _db = settings.DATABASE_URL.rsplit("/", 1)
TEST_DATABASE_URL = (
    f"{_base}/lingoflow_test" if _db != "lingoflow_test" else settings.DATABASE_URL
)

# NullPool ensures each session gets its own connection — prevents the
# "another operation is in progress" asyncpg error when tests run concurrently.
_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
_TestSession = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> None:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def truncate_tables() -> None:
    """Wipe all rows between tests so each test starts with a clean database."""
    yield
    async with _test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            stmt = f"TRUNCATE TABLE {table.name} RESTART IDENTITY CASCADE"
            await conn.execute(text(stmt))


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with _TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
