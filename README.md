# picShare

Multi-user photo sharing web app built with **FastAPI** + **PostgreSQL**.

> Full documentation is available at [docs/](docs/) (rendered with MkDocs).

## Quick start

```bash
make up-build
make migrate
```

Open [http://localhost:8000/docs](http://localhost:8000/docs)

## Stack

| Layer       | Technology                     |
|-------------|--------------------------------|
| Framework   | FastAPI                        |
| Server      | Uvicorn (ASGI)                 |
| Database    | PostgreSQL 17                  |
| ORM         | SQLAlchemy (async)             |
| Migrations  | Alembic                        |
| Auth        | bcrypt + JWT                   |
| Images      | Pillow (thumbnails)            |
| Container   | Docker Compose                 |
| Testing     | pytest / pytest-asyncio / httpx|

## Make targets

- `make up` — build and start containers in background
- `make up-build` — build and start with live logs
- `make migrate` — apply pending Alembic migrations
- `make migrate-auto m="message"` — autogenerate + apply a migration
- `make test` — build, start, create test dirs, run all tests

See [docs/dev.md](docs/dev.md) for the development guide.