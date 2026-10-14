"""Shared pytest fixtures.

`pytest-asyncio` is configured with `asyncio_mode = "auto"` (see
pyproject.toml), so plain `async def test_...` functions just work.

TODO (you) -- build the fixtures you'll reuse across tests:

  1. An async engine on in-memory SQLite (so tests need no Postgres):

         engine = create_async_engine("sqlite+aiosqlite:///:memory:")

     Create the schema with `Base.metadata.create_all` (via `run_sync`).

  2. Override the `get_db` dependency so routes use the test session:

         app.dependency_overrides[get_db] = override_get_db

  3. A test client using httpx's ASGI transport:

         transport = ASGITransport(app=app)
         client = AsyncClient(transport=transport, base_url="http://test")

  4. A convenience fixture that registers + logs in a user and returns an
     authenticated client (cookies are kept automatically by httpx).

Remember to clear `app.dependency_overrides` after each test.
"""

# TODO: imports and fixtures...
