"""Note routes.

Everything except the main page returns an HTML *fragment* (a partial template)
so HTMX can swap it into the DOM without a full page reload.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def notes_page(request: Request) -> HTMLResponse:
    """Render the full notes page (templates/notes/index.html)."""
    # TODO
    ...


@router.get("/list", response_class=HTMLResponse, include_in_schema=False)
async def notes_list(request: Request) -> HTMLResponse:
    """HTMX fragment: the list of note cards (templates/notes/_list.html)."""
    # TODO
    ...


@router.post("", response_class=HTMLResponse, include_in_schema=False)
async def create_note(request: Request) -> HTMLResponse:
    """Create a note from submitted form fields; return the new card fragment.

    Hint: with `async def`, read the body via `await request.form()`.
    """
    # TODO
    ...


@router.get("/{note_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_form(request: Request, note_id: int) -> HTMLResponse:
    """HTMX fragment: an inline edit form for one note."""
    # TODO
    ...


@router.put("/{note_id}", response_class=HTMLResponse, include_in_schema=False)
async def update_note(request: Request, note_id: int) -> HTMLResponse:
    """Save edits and return the updated card fragment."""
    # TODO
    ...


@router.patch("/{note_id}/pin", response_class=HTMLResponse, include_in_schema=False)
async def toggle_pin(request: Request, note_id: int) -> HTMLResponse:
    """Flip `is_pinned` and return the updated card fragment."""
    # TODO
    ...


@router.delete("/{note_id}", response_class=HTMLResponse, include_in_schema=False)
async def delete_note(request: Request, note_id: int) -> HTMLResponse:
    """Delete a note; return an empty response so HTMX removes the card."""
    # TODO
    ...
