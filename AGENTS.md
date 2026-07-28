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
- `docker compose up --build` — start app + DB
- `docker compose exec app alembic upgrade head` — run migrations
- `mkdocs serve -a 127.0.0.1:8001` — view docs
- `localhost:8000/docs` — Swagger UI

## User is a novice
Explain things. Suggest approaches. Ask before making changes.