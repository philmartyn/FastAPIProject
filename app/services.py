"""Business logic shared by the HTML routes and the JSON API.

Keeping queries here (instead of inside route functions) means the HTMX
endpoints in `app/routers/notes.py` and the JSON endpoints in
`app/routers/api.py` do the exact same thing -- a nice design point to show off.

user's notes:

  - list_notes(db, user)                    -> list[Note] (pinned first)
  - get_note(db, user, note_id)             -> Note | None
  - create_note(db, user, title, body)      -> Note
  - update_note(db, user, note_id, **fields)-> Note | None
  - delete_note(db, user, note_id)          -> bool
  - toggle_pin(db, user, note_id)           -> Note | None
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, User


async def _get_owned(db: AsyncSession, user: User, note_id: int) -> Note | None:
    stmt = select(Note).where(Note.id == note_id, Note.owner_id == user.id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_notes(db: AsyncSession, user: User) -> list[Note]:
    stmt = (
        select(Note)
        .where(Note.owner_id == user.id)
        .order_by(Note.is_pinned.desc(), Note.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_note(db: AsyncSession, user: User, note_id: int) -> Note | None:
    return await _get_owned(db, user, note_id)


async def create_note(db: AsyncSession, user: User, title: str, body: str) -> Note:
    note = Note(owner_id=user.id, title=title, body=body)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


_EDITABLE_FIELDS = {"title", "body", "is_pinned"}


async def update_note(db: AsyncSession, user: User, note_id: int, **fields: object) -> Note | None:
    note = await _get_owned(db, user, note_id)
    if note is None:
        return None
    for key, value in fields.items():
        if value is not None and key in _EDITABLE_FIELDS:
            setattr(note, key, value)
    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(db: AsyncSession, user: User, note_id: int) -> bool:
    note = await _get_owned(db, user, note_id)
    if note is None:
        return False
    await db.delete(note)
    await db.commit()
    return True


async def toggle_pin(db: AsyncSession, user: User, note_id: int) -> Note | None:
    note = await _get_owned(db, user, note_id)
    if note is None:
        return None
    note.is_pinned = not note.is_pinned
    await db.commit()
    await db.refresh(note)
    return note
