"""Tests for the ORM models and their relationships."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from app.models import Note, User


def test_user_columns():
    assert {column.name for column in User.__table__.columns} == {
        "id",
        "email",
        "hashed_password",
        "created_at",
    }


def test_note_columns():
    assert {column.name for column in Note.__table__.columns} == {
        "id",
        "owner_id",
        "title",
        "body",
        "is_pinned",
        "created_at",
        "updated_at",
    }


async def test_create_user_with_note(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        user = User(email="a@b.com", hashed_password="x")
        user.notes.append(Note(title="First", body="hello"))
        session.add(user)
        await session.commit()

        assert user.id is not None
        assert user.notes[0].id is not None
        assert user.notes[0].owner_id == user.id


async def test_relationship_loads_eagerly(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        user = User(email="a@b.com", hashed_password="x")
        user.notes.append(Note(title="First", body="hello"))
        session.add(user)
        await session.commit()
        user_id = user.id

    async with session_factory() as session:
        # Async code must eager-load collections; lazy loading raises MissingGreenlet.
        loaded = await session.scalar(
            select(User).options(selectinload(User.notes)).where(User.id == user_id)
        )

    assert loaded is not None
    assert len(loaded.notes) == 1
    assert loaded.notes[0].title == "First"


async def test_email_must_be_unique(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        session.add(User(email="dup@x.com", hashed_password="x"))
        await session.commit()

        session.add(User(email="dup@x.com", hashed_password="y"))
        with pytest.raises(IntegrityError):
            await session.commit()


async def test_deleting_user_cascades_to_notes(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        user = User(email="a@b.com", hashed_password="x")
        user.notes.append(Note(title="First", body="hello"))
        session.add(user)
        await session.commit()
        user_id = user.id

    async with session_factory() as session:
        user = await session.scalar(
            select(User).options(selectinload(User.notes)).where(User.id == user_id)
        )
        await session.delete(user)
        await session.commit()

    async with session_factory() as session:
        note_count = await session.scalar(select(func.count()).select_from(Note))

    assert note_count == 0
