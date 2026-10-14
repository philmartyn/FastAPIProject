"""Application settings.

Loaded from environment variables / the `.env` file and validated by
pydantic-settings. This file is deliberately finished so you can focus on the
interesting parts of the project.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # pydantic-settings reads env vars (case-insensitively) and, if present, the
    # `.env` file. `extra="ignore"` means unknown vars don't raise.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "FastAPI Notes"
    debug: bool = False

    # Signs the session cookie -- must be secret in production.
    secret_key: str = "dev-secret-change-me"

    # Async SQLAlchemy URL, e.g. postgresql+asyncpg://user:pass@host:5432/db
    database_url: str = "postgresql+asyncpg://notes:notes@localhost:5432/notes"

    # Name of the cookie that holds the signed session.
    session_cookie: str = "notes_session"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (built once per process)."""
    return Settings()


settings = get_settings()
