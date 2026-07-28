# Setup

Prerequisites: **Docker** and **Docker Compose**.

---

## 1. Start the application

```bash
docker compose up --build
```

This starts two containers:

- `picshare-app-1` — the FastAPI application on port **8000**
- `picshare-db-1` — PostgreSQL database on port **5432**

## 2. Run database migrations

```bash
docker compose exec app alembic upgrade head
```

This creates the `users` and `images` tables.

## 3. Open the app

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Stopping

```bash
docker compose down       # stops containers, data persists
docker compose down -v    # stops and deletes all data
```

## Running migrations after schema changes

```bash
docker compose exec app alembic revision --autogenerate -m "description"
docker compose exec app alembic upgrade head
```