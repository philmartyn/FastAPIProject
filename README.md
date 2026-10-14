# FastAPI Notes

A small note-taking app built with **FastAPI + HTMX + PostgreSQL**, used as a
learning project. Notes are private to each user (register → log in → manage
your own notes).

This repo currently contains **scaffolding only**: the project structure, config
wiring, Docker setup, and stub modules marked with `TODO`. The implementation is
yours to write.

## Stack

| Concern      | Choice                                             |
| ------------ | -------------------------------------------------- |
| Web framework| FastAPI                                            |
| Templating   | Jinja2 + HTMX (server-rendered HTML)              |
| Database     | PostgreSQL via async SQLAlchemy 2.0 (`asyncpg`)    |
| Migrations   | Alembic                                            |
| Auth         | Signed session cookie (Starlette `SessionMiddleware`) |
| Hashing      | `bcrypt`                                           |
| Tests        | pytest + pytest-asyncio + httpx (SQLite in-memory) |
| Containers   | Docker Compose (app + postgres + adminer)          |

## Layout

```
app/
  main.py          # app factory: middleware, routers, static mount
  config.py        # settings (DONE -- reads .env)
  database.py      # TODO: engine, session factory, Base
  models.py        # TODO: User, Note
  schemas.py       # TODO: Pydantic request/response models
  security.py      # TODO: bcrypt hashing + session helpers
  dependencies.py  # TODO: get_db, get_current_user
  services.py      # TODO: shared note queries (used by HTML + JSON routes)
  routers/
    pages.py       # TODO: "/" redirect
    auth.py        # TODO: login / register / logout
    notes.py       # TODO: HTMX fragment endpoints
    api.py         # TODO: /api/v1 JSON CRUD
  templates/       # Jinja2 (base + skeletons)
  static/          # style.css + vendored htmx.min.js
tests/             # TODO: fixtures + tests
Dockerfile / docker-compose.yml / pyproject.toml
```

## Getting started

```bash
# 1. Create the virtualenv and install (editable, with dev tools)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Copy environment config
cp .env.example .env        # then edit SECRET_KEY

# 3. Start just the database in Docker
docker compose up -d db adminer

# 4. Run the API with auto-reload
uvicorn app.main:app --reload
```

- App: <http://localhost:8000>
- API docs (once routes exist): <http://localhost:8000/docs>
- Adminer (DB browser): <http://localhost:8080> (server `db`, user/pass/db `notes`)

To run the whole stack in containers instead:

```bash
docker compose up --build
```

## Build roadmap

Work top to bottom; each phase ends with something you can actually verify.

- [x] **1. Database layer** — fill in `database.py` and `models.py`.
  - Verify: `alembic init alembic` then `alembic revision --autogenerate -m "initial"` creates a migration with `users` and `notes` tables, and `alembic upgrade head` applies it.
- [x] **2. Auth** — `security.py`, `dependencies.py`, `routers/auth.py`; add `SessionMiddleware` in `main.py`.
  - Verify: register → log in → a protected page loads; logging out sends you back.
- [ ] **3. JSON API** — `schemas.py`, `services.py`, `routers/api.py`.
  - Verify: create/read notes from `/docs`; a second user can't see the first user's notes.
- [x] **4. HTMX UI** — flesh out `templates/` and `routers/notes.py`.
  - Verify: add / edit / pin / delete notes with **no page reloads**.
- [ ] **5. Tests** — `tests/conftest.py` + `test_auth.py`, `test_notes.py`, `test_api.py`.
  - Verify: `pytest` is green using SQLite (no Postgres needed).
- [ ] **6. Polish** — README screenshots, `/healthz`, seed script, ruff formatting.

## Learning notes / gotchas

- **Async everywhere:** routes, DB access, and hashing helpers you call in routes
  should be `async def`. Long CPU work (like bcrypt) technically wants a
  threadpool, but bcrypt is fast enough here — just be aware.
- **Session vs JWT:** a signed session cookie is the natural fit for
  server-rendered HTML. JWT adds value when a separate frontend needs bearer
  tokens.
- **Scope every note query by `owner_id`** — filtering by id alone is a classic
  authorization bug. Return 404 (not 403) when it isn't the user's note.
- **HTMX returns fragments, not full pages.** Keep small partial templates
  (e.g. `_card.html`) for the swapped-in content.
- **`python-multipart`** is required for form parsing (`Form(...)`).

## Why `bcrypt` and not `passlib`?

`passlib` is effectively unmaintained and logs errors against recent `bcrypt`
releases. Using `bcrypt` directly is a few lines and avoids the surprise.
