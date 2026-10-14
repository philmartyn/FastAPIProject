"""Full HTML page routes."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
async def index(request: Request) -> RedirectResponse:
    """Send logged-in users to /notes, everyone else to /login."""
    if request.session.get("user_id") is not None:
        return RedirectResponse("/notes", status_code=303)
    return RedirectResponse("/login", status_code=303)
