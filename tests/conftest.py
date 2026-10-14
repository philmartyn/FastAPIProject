"""Shared pytest fixtures.

Tests run against an in-memory SQLite database (via aiosqlite) so they need no
Postgres or Docker. The app's `get_session` dependency is overridden so routes
use the test session.

`pytest-asyncio` is configured with `asyncio_mode = "auto"` (see pyproject.toml),
so async test functions and fixtures just work.
"""

from collections.abc import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 - registers User/Note on Base.metadata
from app.database import Base, get_session
from app.main import app

# Credentials reused across tests; each test gets a fresh database, so no clash.
TEST_USER = {"email": "user@example.com", "password": "password123"}


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """A fresh in-memory database per test.

    `StaticPool` keeps a single connection, so the `:memory:` database is shared
    across all sessions/connections made during the test (otherwise each new
    connection would see its own empty database).
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # SQLite ignores foreign keys unless explicitly enabled per connection.
    @event.listens_for(engine.sync_engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """A session factory bound to the test database, for direct DB assertions."""
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    """An httpx client wired to the app, backed by the test database.

    httpx keeps cookies automatically, which is what makes the session-based
    auth flow testable.
    """

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncClient:
    """A client that has already registered (and therefore logged in)."""
    response = await client.post("/register", data=TEST_USER)
    assert response.status_code == 303
    return client
