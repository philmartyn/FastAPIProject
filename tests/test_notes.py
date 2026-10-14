"""Tests for the note services in `app.services`.

These exercise the service layer directly against the test database -- no HTTP,
no routes. The security-critical rule (you cannot read or change another user's
note) is what the `other_user` tests pin down.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import services
from app.models import User


async def _make_user(session: AsyncSession, email: str) -> User:
    user = User(email=email, hashed_password="x")
    session.add(user)
    await session.commit()
    return user


async def test_create_note(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "Title", "Body")

        assert note.id is not None
        assert note.owner_id == user.id
        assert note.title == "Title"
        assert note.body == "Body"
        assert note.is_pinned is False
        assert note.created_at is not None
        assert note.updated_at is not None


async def test_list_notes_orders_pinned_first_then_newest(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        old = await services.create_note(session, user, "old", "b")
        new = await services.create_note(session, user, "new", "b")
        pinned = await services.create_note(session, user, "pinned", "b")
        await services.toggle_pin(session, user, pinned.id)

        # SQLite's CURRENT_TIMESTAMP is second-precision, so rows created in the
        # same test can share a timestamp. Assign distinct ones to make the order
        # deterministic -- and note "pinned" is *older* than "new".
        old.created_at = datetime(2024, 1, 1)
        pinned.created_at = datetime(2024, 1, 2)
        new.created_at = datetime(2024, 1, 3)
        await session.commit()

        notes = await services.list_notes(session, user)

    assert [note.title for note in notes] == ["pinned", "new", "old"]


async def test_list_notes_only_returns_own(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        alice = await _make_user(session, "alice@example.com")
        bob = await _make_user(session, "bob@example.com")
        await services.create_note(session, alice, "Alice's", "b")
        await services.create_note(session, bob, "Bob's", "b")

        alice_notes = await services.list_notes(session, alice)

    assert [note.title for note in alice_notes] == ["Alice's"]


async def test_list_notes_empty(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        assert await services.list_notes(session, user) == []


async def test_get_note(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "T", "b")

        fetched = await services.get_note(session, user, note.id)

    assert fetched is not None
    assert fetched.id == note.id


async def test_get_note_other_user_returns_none(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        alice = await _make_user(session, "alice@example.com")
        bob = await _make_user(session, "bob@example.com")
        note = await services.create_note(session, alice, "T", "b")

        assert await services.get_note(session, bob, note.id) is None


async def test_update_note(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "Old", "old body")

        updated = await services.update_note(session, user, note.id, title="New", body="new body")

    assert updated is not None
    assert updated.title == "New"
    assert updated.body == "new body"


async def test_update_note_ignores_unknown_and_none(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "Keep", "keep body")
        original_owner = note.owner_id

        updated = await services.update_note(
            session, user, note.id, title=None, owner_id=999, nope="x"
        )

    assert updated is not None
    assert updated.title == "Keep"
    assert updated.owner_id == original_owner


async def test_update_note_other_user_returns_none(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        alice = await _make_user(session, "alice@example.com")
        bob = await _make_user(session, "bob@example.com")
        note = await services.create_note(session, alice, "Alice's", "b")

        assert await services.update_note(session, bob, note.id, title="Hacked") is None

        unchanged = await services.get_note(session, alice, note.id)

    assert unchanged is not None
    assert unchanged.title == "Alice's"


async def test_delete_note(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "T", "b")

        assert await services.delete_note(session, user, note.id) is True
        assert await services.get_note(session, user, note.id) is None


async def test_delete_note_other_user_returns_false(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        alice = await _make_user(session, "alice@example.com")
        bob = await _make_user(session, "bob@example.com")
        note = await services.create_note(session, alice, "Alice's", "b")

        assert await services.delete_note(session, bob, note.id) is False
        assert await services.get_note(session, alice, note.id) is not None


async def test_toggle_pin(session_factory: async_sessionmaker[AsyncSession]):
    async with session_factory() as session:
        user = await _make_user(session, "a@b.com")
        note = await services.create_note(session, user, "T", "b")
        assert note.is_pinned is False

        pinned = await services.toggle_pin(session, user, note.id)
        assert pinned is not None
        assert pinned.is_pinned is True

        unpinned = await services.toggle_pin(session, user, note.id)
        assert unpinned is not None
        assert unpinned.is_pinned is False


async def test_toggle_pin_other_user_returns_none(
    session_factory: async_sessionmaker[AsyncSession],
):
    async with session_factory() as session:
        alice = await _make_user(session, "alice@example.com")
        bob = await _make_user(session, "bob@example.com")
        note = await services.create_note(session, alice, "T", "b")

        assert await services.toggle_pin(session, bob, note.id) is None
