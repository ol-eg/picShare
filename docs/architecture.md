# Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Browser    │────>│  FastAPI / Uvicorn│────>│  PostgreSQL  │
│  (Swagger)   │     │                  │     │              │
│  (Frontend)  │     │  app/main.py     │     │  users       │
└──────────────┘     │  app/models.py   │     │  images      │
                     │  app/auth.py     │     └──────────────┘
                     │  app/schemas.py  │
                     │  app/image_utils │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │  Static files     │
                     │                   │
                     │  uploads/         │
                     │  thumbnails/      │
                     └──────────────────┘
```

## App structure

| Module | Role |
|--------|------|
| `main.py` | Route definitions, app entry point |
| `models.py` | SQLAlchemy ORM models (`User`, `Image`) |
| `schemas.py` | Pydantic request/response validation |
| `auth.py` | Password hashing, JWT creation/verification |
| `database.py` | DB engine, session factory, settings |
| `image_utils.py` | File save, thumbnail generation |

## Request flow

1. Request hits Uvicorn → FastAPI routes it to the matching handler
2. Dependencies (`get_db`, `get_current_user`) run automatically
3. Handler processes the request, talks to DB via SQLAlchemy
4. FastAPI converts the ORM result to a Pydantic schema (validation)
5. JSON response is sent back

## Auth flow

- `POST /register` — hash password with bcrypt → store user → return JWT
- `POST /login` — verify password → return JWT
- Protected endpoints use `Depends(get_current_user)` which decodes the JWT
  from the `Authorization: Bearer <token>` header

## Image storage

Uploaded images and thumbnails are stored on disk under `app/static/`. The
FastAPI app serves them via `StaticFiles` mounts at `/uploads` and
`/thumbnails`. The directory is bind-mounted from the host in
`docker-compose.yml`, so files persist across container restarts.