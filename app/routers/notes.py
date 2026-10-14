"""Note routes.

Everything except the main page returns an HTML *fragment* (a partial template)
so HTMX can swap it into the DOM without a full page reload.
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse

from app import dependencies, services
from app.templating import templates

UserDep = dependencies.UserDep
DbDep = dependencies.DbDep

router = APIRouter(prefix="/notes")


@router.get("", response_class=HTMLResponse, include_in_schema=False)
async def notes_page(request: Request, db: DbDep, user: UserDep) -> HTMLResponse:
    """Render the full notes page (templates/notes/index.html)."""
    notes = await services.list_notes(db, user)
    return templates.TemplateResponse(request, "notes/index.html", {"notes": notes, "user": user})


@router.get("/list", response_class=HTMLResponse, include_in_schema=False)
async def notes_list(request: Request, db: DbDep, user: UserDep) -> HTMLResponse:
    """HTMX fragment: the list of note cards (templates/notes/_list.html)."""
    notes = await services.list_notes(db, user)
    return templates.TemplateResponse(request, "notes/_list.html", {"notes": notes, "user": user})


@router.post("", response_class=HTMLResponse, include_in_schema=False)
async def create_note(
    request: Request, db: DbDep, user: UserDep, title: str = Form(...), body: str = Form(...)
) -> HTMLResponse:
    """Create a note from submitted form fields; return the new card fragment.

    Hint: with `async def`, read the body via `await request.form()`.
    """
    note = await services.create_note(db, user, title, body)
    return templates.TemplateResponse(request, "notes/_note.html", {"note": note})


@router.get("/{note_id}/edit", response_class=HTMLResponse, include_in_schema=False)
async def edit_form(request: Request, db: DbDep, user: UserDep, note_id: int) -> HTMLResponse:
    """HTMX fragment: an inline edit form for one note."""
    note = await services.get_note(db, user, note_id)
    if note is None:
        return HTMLResponse(status_code=404)
    return templates.TemplateResponse(request, "notes/_edit.html", {"note": note})


@router.put("/{note_id}", response_class=HTMLResponse, include_in_schema=False)
async def update_note(request: Request, db: DbDep, user: UserDep, note_id: int) -> HTMLResponse:
    """Save edits and return the updated card fragment."""
    form = await request.form()
    note = await services.update_note(
        db, user, note_id, title=form.get("title"), body=form.get("body")
    )
    if note is None:
        return HTMLResponse(status_code=404)
    return templates.TemplateResponse(request, "notes/_note.html", {"note": note})


@router.patch("/{note_id}/pin", response_class=HTMLResponse, include_in_schema=False)
async def toggle_pin(request: Request, db: DbDep, user: UserDep, note_id: int) -> HTMLResponse:
    """Flip `is_pinned` and return the updated card fragment."""
    note = await services.toggle_pin(db, user, note_id)
    if note is None:
        return HTMLResponse(status_code=404)
    return templates.TemplateResponse(request, "notes/_note.html", {"note": note})


@router.delete("/{note_id}", response_class=HTMLResponse, include_in_schema=False)
async def delete_note(request: Request, db: DbDep, user: UserDep, note_id: int) -> HTMLResponse:
    """Delete a note; return an empty response so HTMX removes the card."""
    if not await services.delete_note(db, user, note_id):
        return HTMLResponse(status_code=404)
    return HTMLResponse(status_code=200)
