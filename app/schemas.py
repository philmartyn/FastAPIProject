"""Pydantic v2 schemas (request/response models).

TODO (you) -- define the shapes used by the JSON API in `app/routers/api.py`:

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

# TODO: from pydantic import BaseModel, ConfigDict, EmailStr  (EmailStr needs `email-validator`)
