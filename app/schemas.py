"""Pydantic v2 schemas (request/response models).

  - UserCreate: email, password
  - UserRead:   id, email, created_at   (never expose the password hash!)
  - NoteCreate: title, body (default "")
  - NoteUpdate: title?, body?, is_pinned?  (all optional, partial update)
  - NoteRead:   id, title, body, is_pinned, created_at, updated_at

Tip: for models you build *from* ORM objects, tell Pydantic to read attributes:

    class NoteRead(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        ...

Tip: reuse `NoteRead` as `response_model=` on your API routes so the generated
OpenAPI docs are accurate.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = ""


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = None
    is_pinned: bool | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime
