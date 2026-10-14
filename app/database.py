"""Database engine, session factory, and declarative base.

  1. Create the async engine:
       engine = create_async_engine(settings.database_url, echo=settings.debug)

  2. Create a session factory:
       SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

  3. Define the declarative base your models inherit from:
       class Base(DeclarativeBase):
           pass

  4. (Optional) an async `get_session()` generator you can wrap in a FastAPI
     dependency. Many people put that in `app/dependencies.py` instead -- your
     call.

Reference: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
