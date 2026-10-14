"""Reusable FastAPI dependencies (wired in with `Depends(...)`).

1. `get_current_user(request, db)` -- reads `user_id` from the session and
   loads the User. If there's no session (or the user is gone), raise a 401
   for API/JSON routes or redirect to /login for HTML routes.

   Hint: you can decide based on the URL path, or raise a custom exception and
   handle it in `app/main.py` with an exception handler.

   `Annotated[AsyncSession, Depends(get_db)]` is the modern, readable way to
   inject these into route functions.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.database import get_session
from app.models import User


class NotAuthenticatedError(Exception):
    """No logged-in user for a route that requires one."""


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    user_id = request.session.get("user_id")
    if user_id is None:
        raise NotAuthenticatedError
    user = await db.get(User, user_id)  # db.get = lookup by primary key
    if user is None:  # session points at a deleted user
        request.session.clear()
        raise NotAuthenticatedError
    return user
