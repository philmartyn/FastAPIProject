"""Reusable FastAPI dependencies (wired in with `Depends(...)`).

TODO (you) -- provide two dependencies:

  1. `get_db()` -- yields an `AsyncSession` from your session factory and closes
     it afterwards. Typical shape:

         async def get_db() -> AsyncIterator[AsyncSession]:
             async with SessionLocal() as session:
                 yield session

  2. `get_current_user(request, db)` -- reads `user_id` from the session and
     loads the User. If there's no session (or the user is gone), raise a 401
     for API/JSON routes or redirect to /login for HTML routes.

     Hint: you can decide based on the URL path, or raise a custom exception and
     handle it in `app/main.py` with an exception handler.

     `Annotated[AsyncSession, Depends(get_db)]` is the modern, readable way to
     inject these into route functions.
"""

