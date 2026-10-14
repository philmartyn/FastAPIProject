"""Tests for the JSON API under /api/v1, via the HTTP layer.

Reuses the `auth_client` fixture (already registered and logged in as TEST_USER).
Unlike the HTML routes, these speak JSON: the session cookie authenticates the
request, and an unauthenticated call gets a ``401`` with a JSON body instead of a
redirect to /login -- the ``/api`` branch of the NotAuthenticatedError handler.
"""

from httpx import AsyncClient

from tests.conftest import TEST_USER


async def test_notes_require_auth(client: AsyncClient):
    response = await client.get("/api/v1/notes")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


async def test_create_note_returns_read_shape(auth_client: AsyncClient):
    response = await auth_client.post("/api/v1/notes", json={"title": "First", "body": "hello"})

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "First"
    assert data["body"] == "hello"
    assert data["is_pinned"] is False
    # The exact read shape: no owner_id, and certainly no password hash.
    assert set(data) == {"id", "title", "body", "is_pinned", "created_at", "updated_at"}


async def test_create_note_validates_input(auth_client: AsyncClient):
    assert (await auth_client.post("/api/v1/notes", json={"body": "no title"})).status_code == 422
    assert (await auth_client.post("/api/v1/notes", json={"title": ""})).status_code == 422


async def test_list_notes_puts_pinned_first(auth_client: AsyncClient):
    await auth_client.post("/api/v1/notes", json={"title": "old"})
    await auth_client.post("/api/v1/notes", json={"title": "new"})
    pinned = await auth_client.post("/api/v1/notes", json={"title": "pinned"})
    await auth_client.patch(f"/api/v1/notes/{pinned.json()['id']}", json={"is_pinned": True})

    response = await auth_client.get("/api/v1/notes")

    assert response.status_code == 200
    titles = [note["title"] for note in response.json()]
    # Only the pin ordering is deterministic here; the other two share a
    # second-precision timestamp (see tests/test_notes.py).
    assert titles[0] == "pinned"
    assert set(titles) == {"old", "new", "pinned"}


async def test_get_note_and_missing_note(auth_client: AsyncClient):
    created = await auth_client.post("/api/v1/notes", json={"title": "First"})
    note_id = created.json()["id"]

    assert (await auth_client.get(f"/api/v1/notes/{note_id}")).status_code == 200
    assert (await auth_client.get("/api/v1/notes/999")).status_code == 404


async def test_patch_updates_only_provided_fields(auth_client: AsyncClient):
    created = await auth_client.post("/api/v1/notes", json={"title": "Old", "body": "keep me"})
    note_id = created.json()["id"]

    response = await auth_client.patch(f"/api/v1/notes/{note_id}", json={"title": "New"})

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New"
    assert data["body"] == "keep me"  # untouched -- this is what exclude_unset buys


async def test_patch_can_pin(auth_client: AsyncClient):
    created = await auth_client.post("/api/v1/notes", json={"title": "First"})
    note_id = created.json()["id"]

    response = await auth_client.patch(f"/api/v1/notes/{note_id}", json={"is_pinned": True})

    assert response.status_code == 200
    assert response.json()["is_pinned"] is True


async def test_delete_note(auth_client: AsyncClient):
    created = await auth_client.post("/api/v1/notes", json={"title": "First"})
    note_id = created.json()["id"]

    response = await auth_client.delete(f"/api/v1/notes/{note_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert (await auth_client.get(f"/api/v1/notes/{note_id}")).status_code == 404


async def test_users_me_never_exposes_password(auth_client: AsyncClient):
    response = await auth_client.get("/api/v1/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert set(data) == {"id", "email", "created_at"}


async def test_second_user_cannot_see_or_touch_first_users_note(auth_client: AsyncClient):
    created = await auth_client.post("/api/v1/notes", json={"title": "Alice's", "body": "secret"})
    note_id = created.json()["id"]

    await auth_client.post("/logout")
    response = await auth_client.post(
        "/register", data={"email": "bob@example.com", "password": "password123"}
    )
    assert response.status_code == 303  # registered (auto-logged-in) as Bob

    assert (await auth_client.get("/api/v1/notes")).json() == []
    assert (await auth_client.get(f"/api/v1/notes/{note_id}")).status_code == 404
    assert (
        await auth_client.patch(f"/api/v1/notes/{note_id}", json={"title": "Hacked"})
    ).status_code == 404
    assert (await auth_client.delete(f"/api/v1/notes/{note_id}")).status_code == 404
