"""Application entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Wiring, in order:

  - `SessionMiddleware` signed with `settings.secret_key`, so `request.session`
    works for the login cookie.
  - The routers: pages, auth, notes (HTMX fragments), api (/api/v1 JSON).
  - A `NotAuthenticatedError` handler that redirects HTML requests to /login and
    returns a JSON 401 for /api requests.
  - A `/healthz` liveness probe.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.dependencies import NotAuthenticatedError
from app.routers import api, auth, notes, pages

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Serve CSS and the vendored htmx script from /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie=settings.session_cookie,
    same_site="lax",
    https_only=False,
)

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(notes.router)
app.include_router(api.router)


@app.exception_handler(NotAuthenticatedError)
async def handle_not_authenticated(request: Request, exc: NotAuthenticatedError):
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not authenticated"}, status_code=401)
    return RedirectResponse("/login", status_code=303)


@app.get("/healthz", tags=["meta"])
async def healthz() -> dict[str, str]:
    """Liveness probe, also used by docker compose."""
    return {"status": "ok"}
