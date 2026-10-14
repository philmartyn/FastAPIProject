"""SQLAlchemy ORM models.

(`Mapped[...]` annotations + `mapped_column()`). They should inherit from
`Base` in `app/database.py`.

User
  - id: int, primary key
  - email: str, unique, indexed
  - hashed_password: str
  - created_at: datetime (server default now)

Note
  - id: int, primary key
  - owner_id: int, ForeignKey("users.id", ondelete="CASCADE"), indexed
  - title: str
  - body: str, default ""
  - is_pinned: bool, default False
  - created_at / updated_at: datetime

Tip: add a `relationship()` so you can navigate `user.notes` and `note.owner`.
Tip: think about `onupdate` for `updated_at`.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[list["Note"]] = relationship(back_populates="owner", cascade="all, delete-orphan")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text, default="")
    is_pinned: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner: Mapped["User"] = relationship(back_populates="notes")
