"""Application entrypoint.

Run locally with:
    uvicorn app.main:app --reload

TODO (you) -- finish wiring the app together:

  1. Session middleware (needed for `request.session`):

         from starlette.middleware.sessions import SessionMiddleware
         app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

  2. Include the routers:

         from app.routers import api, auth, notes, pages
         app.include_router(pages.router)
         app.include_router(auth.router)
         app.include_router(notes.router)
         app.include_router(api.router)

  3. (Nicer than @app.on_event) use a lifespan handler for startup/shutdown.

  4. (Optional) an exception handler that turns an "unauthenticated" error into
     a redirect to /login for HTML requests and a JSON 401 for /api requests.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Serve CSS and the vendored htmx script from /static
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# TODO: add SessionMiddleware here
# TODO: include the routers here


@app.get("/healthz", tags=["meta"])
async def healthz() -> dict[str, str]:
    """Liveness probe, also used by docker compose."""
    return {"status": "ok"}
