# picShare project memory

## What we're building
Multi-user photo sharing web app. FastAPI + PostgreSQL + Docker Compose.

## Current state
Scaffolding complete. App runs (docker compose up --build), migrations run
(alembic upgrade head), Swagger at localhost:8000/docs. MkDocs docs at
localhost:8001.

## Stack
- FastAPI / Uvicorn (ASGI)
- PostgreSQL 17 (Docker)
- SQLAlchemy async + asyncpg
- Alembic for migrations
- bcrypt + JWT for auth
- Registration gated by `PICSHARE_INVITE_CODE` env var (absent = open)
- Pillow for thumbnails
- MkDocs for project docs

## Project structure
```
picShare/
├── app/
│   ├── main.py          # Routes
│   ├── models.py        # User, Image ORM models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # DB engine + Settings
│   ├── auth.py          # Hashing + JWT + get_current_user
│   ├── image_utils.py   # Save/thumbnail uploads
│   └── static/uploads/  # On-disk images
├── docs/                # MkDocs markdown pages
├── alembic/             # Migrations
├── docker-compose.yml
├── Dockerfile
└── mkdocs.yml
```

## Running
- `make up` — start app + DB (background)
- `make migrate` — run migrations
- `make test` — build + test
- `mkdocs serve -a 127.0.0.1:8001` — view docs
- `localhost:8000/docs` — Swagger UI

## Testing (TDD workflow)
- `make test` — build, start containers, create test dirs, run pytest with coverage
- Stack: pytest + pytest-asyncio + httpx (ASGI transport, no real network)
- Test DB (`db-test`) is ephemeral (tmpfs) — resets on restart
- Tests auto-create/drop schema per run via SQLAlchemy metadata
- Test DB (`db-test`) is ephemeral (tmpfs) — resets on restart
- Tests auto-create/drop schema per run via SQLAlchemy metadata
- Stack: pytest + pytest-asyncio + httpx (ASGI transport, no real network)

## Session history
- 2026-07-28: Scaffold done, docker compose works, migrations run, Swagger at /docs.
  MkDocs added (serve on 8001). Git init'd, SSH configured with ~/.ssh/id_rsa.
  User needs to add SSH key to GitHub, create empty repo, and push.

## User is a novice
Explain things. Suggest approaches. Ask before making changes.