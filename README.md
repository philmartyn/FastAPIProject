# FastAPI Notes

A small note-taking app built with **FastAPI + HTMX + PostgreSQL**, used as a
learning project. Notes are private to each user: register → log in → create,
edit, pin, and delete your own notes — all server-rendered with HTMX, so the
list updates with **no page reloads**.

The same operations are also exposed as a versioned **JSON API** under
`/api/v1`, documented automatically at `/docs`. Both layers call into the same
`app/services.py`.

## Status

Feature-complete for the roadmap below (phases 1–5); the JSON API, HTMX UI,
tests, and CI are all in place. The only outstanding polish items are README
screenshots and a seed script.

## Stack

| Concern       | Choice                                             |
| ------------- | -------------------------------------------------- |
| Web framework | FastAPI                                            |
| Templating    | Jinja2 + HTMX 2.0.4 (vendored, server-rendered)    |
| Database      | PostgreSQL via async SQLAlchemy 2.0 (`asyncpg`)    |
| Migrations    | Alembic                                            |
| Auth          | Signed session cookie (Starlette `SessionMiddleware`) |
| Hashing       | `bcrypt`                                           |
| Tests         | pytest + pytest-asyncio + httpx (SQLite in-memory) |
| Containers    | Docker Compose (app + postgres + adminer)          |
| CI            | GitHub Actions (ruff + pytest)                     |

## Layout

```
app/
  main.py          # app factory: middleware, exception handler, routers, static, /healthz
  config.py        # settings (pydantic-settings, reads .env)
  database.py      # async engine, session factory, Base
  models.py        # User, Note ORM models
  schemas.py       # Pydantic request/response models
  security.py      # bcrypt hashing + session helpers
  dependencies.py  # get_session / get_current_user (DbDep / UserDep), NotAuthenticatedError
  services.py      # owner-scoped note queries (shared by HTML + JSON routes)
  templating.py    # shared Jinja2Templates instance
  routers/
    pages.py       # "/" redirect
    auth.py        # GET/POST /login, /register; POST /logout
    notes.py       # HTMX fragment endpoints
    api.py         # /api/v1 JSON CRUD
  templates/
    base.html
    login.html
    register.html
    notes/
      index.html   # full notes page
      _list.html   # list wrapper (empty-state aware)
      _note.html   # single note card (swap target for create/update)
      _edit.html   # inline edit form
  static/          # style.css + vendored htmx.min.js
alembic/           # env.py + initial revision
tests/             # conftest + test_security / test_models / test_auth
                   #          / test_notes / test_notes_routes / test_api
.github/workflows/tests.yml
Dockerfile / docker-compose.yml / pyproject.toml
```

## Endpoints

**HTML / HTMX** (session-auth; return HTML fragments unless noted):

| Method | Path              | Purpose                              |
| ------ | ----------------- | ------------------------------------ |
| GET    | `/`               | redirect to `/notes` or `/login`     |
| GET    | `/login`          | login page                           |
| POST   | `/login`          | authenticate                         |
| GET    | `/register`       | register page                        |
| POST   | `/register`       | create account (auto-logs in)        |
| POST   | `/logout`         | clear session                        |
| GET    | `/notes`          | full notes page                      |
| GET    | `/notes/list`     | list fragment                        |
| POST   | `/notes`          | create note (returns card fragment)  |
| GET    | `/notes/{id}/edit`| inline edit form fragment            |
| PUT    | `/notes/{id}`     | save edit (returns card fragment)    |
| PATCH  | `/notes/{id}/pin` | toggle pin (returns card fragment)   |
| DELETE | `/notes/{id}`     | delete note (empty `200`)            |

**JSON** under `/api/v1` (session-cookie auth; described in `/docs`):

| Method | Path               | Response                     |
| ------ | ------------------ | ---------------------------- |
| GET    | `/api/v1/notes`    | `list[NoteRead]`             |
| POST   | `/api/v1/notes`    | `NoteRead` (`201`)           |
| GET    | `/api/v1/notes/{id}` | `NoteRead` (`404` if not yours) |
| PATCH  | `/api/v1/notes/{id}` | `NoteRead`                   |
| DELETE | `/api/v1/notes/{id}` | `204 No Content`             |
| GET    | `/api/v1/users/me` | `UserRead`                   |

Plus `GET /healthz` (liveness probe → `{"status": "ok"}`).

## Getting started

```bash
# 1. Create the virtualenv and install (editable, with dev tools)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 2. Copy environment config
cp .env.example .env        # then edit SECRET_KEY

# 3. Start just the database (+ Adminer) in Docker
docker compose up -d db adminer

# 4. Apply migrations and run the API with auto-reload
alembic upgrade head
uvicorn app.main:app --reload
```

- App: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- Adminer (DB browser): <http://localhost:8080> (server `db`, user/pass/db `notes`)

To run the whole stack in containers instead:

```bash
docker compose up --build
```

The app container applies migrations (`alembic upgrade head`) before starting
uvicorn. If you'd rather run uvicorn locally against the containerised DB, stop
the containerised app first so port 8000 is free:

```bash
docker compose stop app
```

## Tests & CI

```bash
pytest -q              # 52 tests, SQLite in-memory — no Postgres needed
ruff check .
ruff format --check .
```

`.github/workflows/tests.yml` runs all three on every push and pull request.

## Build roadmap

Work top to bottom; each phase ends with something you can actually verify.

- [x] **1. Database layer** — `database.py` and `models.py`.
  - Verify: `alembic revision --autogenerate -m "initial"` creates a migration
    with `users` and `notes` tables, and `alembic upgrade head` applies it.
- [x] **2. Auth** — `security.py`, `dependencies.py`, `routers/auth.py`;
  `SessionMiddleware` in `main.py`.
  - Verify: register → log in → a protected page loads; logging out sends you back.
- [x] **3. JSON API** — `schemas.py`, `services.py`, `routers/api.py`.
  - Verify: create/read notes from `/docs`; a second user can't see the first
    user's notes (covered by `tests/test_api.py`).
- [x] **4. HTMX UI** — `templates/` and `routers/notes.py`.
  - Verify: add / edit / pin / delete notes with **no page reloads**.
- [x] **5. Tests** — `tests/conftest.py` + `test_security.py`, `test_models.py`,
  `test_auth.py`, `test_notes.py`, `test_notes_routes.py`, `test_api.py`.
  - Verify: `pytest` is green using SQLite (no Postgres needed).
- [ ] **6. Polish** — remaining: README screenshots and a seed script.
  (`/healthz`, ruff formatting, and CI are done.)

## Learning notes / gotchas

- **Async everywhere:** routes, DB access, and hashing helpers you call in routes
  are `async def`. Long CPU work (like bcrypt) technically wants a threadpool,
  but bcrypt is fast enough here — just be aware.
- **Session vs JWT:** a signed session cookie is the natural fit for
  server-rendered HTML. JWT adds value when a separate frontend needs bearer
  tokens — the JSON API still relies on the session cookie today.
- **Scope every note query by `owner_id`** — filtering by id alone is a classic
  authorization bug. Return **404 (not 403)** when it isn't the user's note, so
  the API never reveals that the note exists.
- **PATCH is a partial update:** call
  `payload.model_dump(exclude_unset=True)` so omitted fields aren't wiped. An
  explicit `null` is also ignored, since the columns are non-nullable.
- **HTMX returns fragments, not full pages.** Keep small partial templates
  (`_note.html`, `_edit.html`, `_list.html`) for the swapped-in content.
- **HTMX delete returns an empty `200`, not `204`** — htmx ignores a `204` body
  and won't remove the card. The JSON API, having no such constraint, returns a
  proper `204`.
- **Empty-state styling** relies on `#note-list:empty::after`; the templates are
  whitespace-trimmed so the list element is genuinely empty. CSS `:empty` is
  unreliable with whitespace-only content.
- **`create_note` needs no `db.refresh`** because SQLAlchemy 2.0
  `eager_defaults="auto"` uses `INSERT ... RETURNING` for server-side defaults.
  `update_note` / `toggle_pin` refresh explicitly to pick up the `onupdate`
  timestamp.
- **`python-multipart`** is required for form parsing (`Form(...)`).

## Why `bcrypt` and not `passlib`?

`passlib` is effectively unmaintained and logs errors against recent `bcrypt`
releases. Using `bcrypt` directly is a few lines and avoids the surprise.
