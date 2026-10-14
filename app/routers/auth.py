"""Authentication routes: register, login, logout.

These render HTML pages and set/clear the session cookie, so they pair with the
`SessionMiddleware` you'll add in `app/main.py`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response

from app import security
from app.database import get_session
from app.models import User
from app.templating import templates

router = APIRouter(tags=["auth"])


@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_form(request: Request) -> Response:
    if request.session.get("user_id") is not None:
        return RedirectResponse("/notes", status_code=303)
    return templates.TemplateResponse(request, "login.html")


@router.post("/login")
async def login(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
    email: str = Form(...),
    password: str = Form(...),  # see note
) -> Response:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or not security.verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request, "login.html", {"error": "Invalid email or password"}
        )
    security.log_in(request, user.id)
    return RedirectResponse("/notes", status_code=303)


@router.get("/register", response_class=HTMLResponse, include_in_schema=False)
async def register_form(request: Request) -> Response:
    """Render the sign-up page (templates/register.html)."""
    if request.session.get("user_id") is not None:
        return RedirectResponse("/notes", status_code=303)
    return templates.TemplateResponse(request, "register.html")


@router.post("/register")
async def register(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_session)],
    email: str = Form(...),
    password: str = Form(...),
) -> Response:
    user = User(email=email, hashed_password=security.hash_password(password))
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        return templates.TemplateResponse(
            request, "register.html", {"error": "That email is already registered"}
        )
    security.log_in(request, user.id)
    return RedirectResponse("/notes", status_code=303)


@router.post("/logout")
async def logout(request: Request) -> RedirectResponse:
    """Clear the session and redirect to /login."""
    security.log_out(request)
    return RedirectResponse("/login", status_code=303)
