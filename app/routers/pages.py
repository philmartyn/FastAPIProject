"""Full HTML page routes."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter(tags=["pages"])


@router.get("/", include_in_schema=False)
async def index(request: Request) -> RedirectResponse:
    """Send logged-in users to /notes, everyone else to /login."""
    # TODO: check request.session for "user_id"
    ...
