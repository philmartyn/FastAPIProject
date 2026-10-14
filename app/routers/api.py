"""JSON API, versioned under /api/v1.

This gives you the same behaviour as the HTMX routes but returns typed JSON, so
FastAPI's auto-generated docs at /docs become a nice showcase.

TODO (you) -- implement, using the Pydantic schemas from app/schemas.py and the
shared helpers in app/services.py:

  GET    /api/v1/notes          -> list[NoteRead]
  POST   /api/v1/notes          -> NoteRead          (201 Created)
  GET    /api/v1/notes/{id}     -> NoteRead          (404 if not yours)
  PATCH  /api/v1/notes/{id}     -> NoteRead
  DELETE /api/v1/notes/{id}     -> 204 No Content

Protect them with `Depends(get_current_user)` so the OpenAPI "Authorize" flow
(or your session cookie) is required.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["api"])

# TODO: routes...
