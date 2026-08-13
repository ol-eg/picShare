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
- `make lint` — run Ruff lint + format check on `app/` and `tests/`
- `make lint-fix` — auto-fix lint issues + format `app/` and `tests/`
- `make typecheck` — run mypy on `app/` (prod code only)

Tests run inside the `app` container against a dedicated test DB
(`db-test`) and set test-specific env vars (upload/thumb dirs, secret key).

Lint and type-checking also run inside the `app` container. Source files
(`app/`), tests (`tests/`), and migrations (`alembic/`) are bind-mounted so the
container always sees the live code on disk.

First-time DB setup: the `alembic/versions/` dir ships with an initial migration
creating the `users`/`images` tables, so a fresh database just needs
`make migrate`. `make migrate-auto` generates migration files straight into the
bind-mounted `alembic/versions/`, so they land on disk automatically.

### Workflow — TDD
We practice TDD here, always:
1. Write a small failing test first
2. Run it and confirm it fails (red)
3. Write the minimum code to make it pass (green)
4. Rinse and repeat — small, iterative steps

### How to run tests, lint, and type checking
Prefer the `make` wrappers for the verification gates — `make test`,
`make lint`, `make lint-fix`, and `make typecheck`. The user likes to run
these themselves to see them in action and build confidence, so use the
make targets rather than calling `docker compose exec ...` directly.

Serve docs locally: `mkdocs serve -a 127.0.0.1:8001`

## Pre-commit checklist

1. Run `make test` — all tests must pass
2. Run `make lint` and `make typecheck` — lint and type check must pass
3. Regenerate diagrams: `python3 docs/diagram.py`
4. Quick scan: `git diff --stat` for unintended files
5. If docs changed, start `mkdocs serve -a 127.0.0.1:8001` and verify the rendered pages look correct