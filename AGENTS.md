# picShare

User is a novice — explain things, suggest approaches, ask before making changes.

Multi-user photo sharing web app: FastAPI + SQLAlchemy (async) + PostgreSQL, containerized with Docker Compose. Auth is JWT-based (bcrypt) and registration is gated by an invite code.

## Layout

- `app/` — FastAPI application
  - `main.py` — app entrypoint and routing
  - `database.py` — async SQLAlchemy engine/session
  - `models.py` / `schemas.py` — ORM models and Pydantic schemas
  - `image_utils.py` — Pillow thumbnail generation
  - `auth.py` — bcrypt + JWT auth
  - `static/` / `templates/` — Jinja2 frontend
- `alembic/` — DB migrations
- `tests/` — pytest suite (async, uses `testpaths = ["tests"]`)
- `docs/` — MkDocs site; `docs/diagram.py` regenerates architecture diagrams

## Commands

All containers/commands run via Docker Compose:

- `make up` — build + start in background
- `make up-build` — build + start with live logs
- `make migrate` — apply Alembic migrations
- `make migrate-auto m="msg"` — autogenerate + apply a migration
- `make test` — run full pytest suite with coverage (HTML + term)
- `make test-ci` — same but terminal coverage only

Tests run inside the `app` container against a dedicated test DB
(`db-test`) and set test-specific env vars (upload/thumb dirs, secret key).

### Workflow — TDD
We practice TDD here, always:
1. Write a small failing test first
2. Run it and confirm it fails (red)
3. Write the minimum code to make it pass (green)
4. Rinse and repeat — small, iterative steps

Serve docs locally: `mkdocs serve -a 127.0.0.1:8001`

## Pre-commit checklist

1. Run `make test` — all tests must pass
2. Regenerate diagrams: `python3 docs/diagram.py`
3. Quick scan: `git diff --stat` for unintended files
4. If docs changed, start `mkdocs serve -a 127.0.0.1:8001` and verify the rendered pages look correct