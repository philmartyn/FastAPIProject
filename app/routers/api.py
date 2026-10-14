"""JSON API, versioned under /api/v1.

This gives you the same behaviour as the HTMX routes but returns typed JSON, so
FastAPI's auto-generated docs at /docs become a nice showcase.

shared helpers in app/services.py:

  GET    /api/v1/notes          -> list[NoteRead]
  POST   /api/v1/notes          -> NoteRead          (201 Created)
  GET    /api/v1/notes/{id}     -> NoteRead          (404 if not yours)
  PATCH  /api/v1/notes/{id}     -> NoteRead
  DELETE /api/v1/notes/{id}     -> 204 No Content

Protect them with `Depends(get_current_user)` so the OpenAPI "Authorize" flow
(or your session cookie) is required.
"""

from fastapi import APIRouter, HTTPException, status

from app import dependencies, services
from app.models import Note, User
from app.schemas import NoteCreate, NoteRead, NoteUpdate, UserRead

router = APIRouter(prefix="/api/v1", tags=["api"])

UserDep = dependencies.UserDep
DbDep = dependencies.DbDep


@router.get("/notes", response_model=list[NoteRead])
async def list_notes(db: DbDep, user: UserDep) -> list[Note]:
    return await services.list_notes(db, user)


@router.post("/notes", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(db: DbDep, payload: NoteCreate, user: UserDep) -> Note:
    return await services.create_note(db, user, payload.title, payload.body)


@router.get("/notes/{note_id}", response_model=NoteRead)
async def get_note(note_id: int, db: DbDep, user: UserDep) -> Note:
    note = await services.get_note(db, user, note_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@router.patch("/notes/{note_id}", response_model=NoteRead)
async def update_note(note_id: int, db: DbDep, payload: NoteUpdate, user: UserDep) -> Note:
    note = await services.update_note(db, user, note_id, **payload.model_dump(exclude_unset=True))
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, db: DbDep, user: UserDep) -> None:
    if not await services.delete_note(db, user, note_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note not found")


@router.get("/users/me", response_model=UserRead)
async def read_me(user: UserDep) -> User:
    return user
