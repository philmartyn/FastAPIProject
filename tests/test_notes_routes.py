"""Route-level tests for the HTMX note endpoints.

Unlike `tests/test_notes.py` (which calls the services directly), these go
through HTTP via the `auth_client` fixture -- so they check that the routes, the
auth dependency, the exception handler and the fragment templates all agree.

`auth_client` is already registered and logged in as `TEST_USER`.
"""

import re

from httpx import AsyncClient

# Rather than assume a note's primary key, pull it out of the card's swap target
# (`id="note-3"`) -- the same thing htmx relies on.
NOTE_ID = re.compile(r'id="note-(\d+)"')


def _note_id(html: str) -> int:
    match = NOTE_ID.search(html)
    assert match is not None, f"expected a note card in the response, got: {html!r}"
    return int(match.group(1))


async def test_notes_page_requires_login(client: AsyncClient):
    """An anonymous visit is redirected to /login (exercises the handler)."""
    response = await client.get("/notes")

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


async def test_notes_page_shows_create_form(auth_client: AsyncClient):
    response = await auth_client.get("/notes")

    assert response.status_code == 200
    assert 'hx-post="/notes"' in response.text


async def test_created_note_renders_on_full_page(auth_client: AsyncClient):
    await auth_client.post("/notes", data={"title": "Shopping", "body": "milk"})

    response = await auth_client.get("/notes")

    assert response.status_code == 200
    assert "Shopping" in response.text
    assert "milk" in response.text


async def test_create_note_returns_card_fragment(auth_client: AsyncClient):
    """The response is a card (not a page) so htmx can prepend it into the list."""
    response = await auth_client.post("/notes", data={"title": "First", "body": "hello"})

    assert response.status_code == 200
    assert _note_id(response.text) == 1
    assert "First" in response.text


async def test_edit_form_is_prefilled(auth_client: AsyncClient):
    created = await auth_client.post("/notes", data={"title": "Old", "body": "draft"})
    note_id = _note_id(created.text)

    response = await auth_client.get(f"/notes/{note_id}/edit")

    assert response.status_code == 200
    assert f'hx-put="/notes/{note_id}"' in response.text
    assert 'value="Old"' in response.text
    assert ">draft<" in response.text  # textarea body sits between the tags


async def test_update_note_saves_and_returns_card(auth_client: AsyncClient):
    created = await auth_client.post("/notes", data={"title": "Old", "body": "a"})
    note_id = _note_id(created.text)

    response = await auth_client.put(f"/notes/{note_id}", data={"title": "New", "body": "b"})

    assert response.status_code == 200
    assert "New" in response.text
    assert "hx-put" not in response.text  # a card again, not the edit form

    listed = await auth_client.get("/notes/list")
    assert "New" in listed.text


async def test_toggle_pin_flips_state(auth_client: AsyncClient):
    created = await auth_client.post("/notes", data={"title": "First", "body": "b"})
    note_id = _note_id(created.text)

    pinned = await auth_client.patch(f"/notes/{note_id}/pin")
    assert pinned.status_code == 200
    assert "Unpin" in pinned.text  # note: "Pin" is a substring of "Unpin"

    unpinned = await auth_client.patch(f"/notes/{note_id}/pin")
    assert "Unpin" not in unpinned.text


async def test_delete_returns_empty_body_so_htmx_removes_card(auth_client: AsyncClient):
    """An empty 200 swaps the card out. A 204 would make htmx do nothing."""
    created = await auth_client.post("/notes", data={"title": "First", "body": "b"})
    note_id = _note_id(created.text)

    response = await auth_client.delete(f"/notes/{note_id}")

    assert response.status_code == 200
    assert response.text == ""

    listed = await auth_client.get("/notes/list")
    assert "First" not in listed.text


async def test_missing_note_returns_404(auth_client: AsyncClient):
    assert (await auth_client.get("/notes/999/edit")).status_code == 404
    assert (await auth_client.put("/notes/999", data={"title": "x"})).status_code == 404
    assert (await auth_client.patch("/notes/999/pin")).status_code == 404
    assert (await auth_client.delete("/notes/999")).status_code == 404


async def test_cannot_touch_another_users_note(auth_client: AsyncClient):
    """Register as a second user and confirm the first user's note is invisible."""
    created = await auth_client.post("/notes", data={"title": "Alice's", "body": "secret"})
    note_id = _note_id(created.text)

    await auth_client.post("/logout")
    response = await auth_client.post(
        "/register", data={"email": "bob@example.com", "password": "password123"}
    )
    assert response.status_code == 303  # registered (and auto-logged-in) as Bob

    listed = await auth_client.get("/notes/list")
    assert "Alice's" not in listed.text

    assert (await auth_client.get(f"/notes/{note_id}/edit")).status_code == 404
    assert (await auth_client.put(f"/notes/{note_id}", data={"title": "Hacked"})).status_code == 404
    assert (await auth_client.delete(f"/notes/{note_id}")).status_code == 404
