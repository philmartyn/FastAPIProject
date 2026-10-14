"""Authentication routes: register, login, logout.

These render HTML pages and set/clear the session cookie, so they pair with the
`SessionMiddleware` you'll add in `app/main.py`.
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_form(request: Request) -> HTMLResponse:
    """Render the login page (templates/login.html)."""
    # TODO
    ...


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    """Look up the user, verify the password, store `user_id`, redirect to /notes.

    On failure, re-render the login page with an error message.
    """
    # TODO
    ...


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_form(request: Request) -> HTMLResponse:
    """Render the sign-up page (templates/register.html)."""
    # TODO
    ...


@router.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    """Create a user (reject duplicates), then log them in."""
    # TODO
    ...


@router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    """Clear the session and redirect to /login."""
    # TODO
    ...
