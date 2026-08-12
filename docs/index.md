# picShare

Multi-user photo sharing web app built with **FastAPI** + **PostgreSQL**.

Users register, log in, upload photos with captions, and manage their own
images. Each upload generates a thumbnail automatically.

---

## Quick start

```bash
docker compose up --build
docker compose exec app alembic upgrade head
```

Or with the Makefile:

```bash
make up-build
make migrate
```

Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Stack

![picShare Technology Stack](stack_diagram.png)

| Layer          | Technology                     |
|----------------|--------------------------------|
| Framework      | FastAPI                        |
| Server         | Uvicorn (ASGI)                 |
| Frontend       | Jinja2 + Tailwind CSS + HTMX  |
| API Docs       | Swagger UI / ReDoc             |
| Database       | PostgreSQL 17                  |
| ORM            | SQLAlchemy (async)             |
| Migrations     | Alembic                        |
| Auth           | bcrypt + JWT                   |
| Images         | Pillow (thumbnails)            |
| Container      | Docker Compose                 |
| Lint           | Ruff                           |
| Types          | mypy + typeshed stubs          |