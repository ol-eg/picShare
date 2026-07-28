# Development

## Viewing docs locally

```bash
pip install mkdocs
mkdocs serve
```

Open [http://127.0.0.1:8001](http://127.0.0.1:8001).

## Adding a new endpoint

1. Define request/response schemas in `app/schemas.py`
2. Add the handler in `app/main.py`
3. If you need a new DB column, create a migration:
   ```bash
   docker compose exec app alembic revision --autogenerate -m "add field"
   docker compose exec app alembic upgrade head
   ```
4. Rebuild the image: `docker compose build app`

## Adding a new DB table

1. Define the model in `app/models.py` (inherit `Base`)
2. Run `alembic revision --autogenerate -m "add new_table"`
3. Review the migration file in `alembic/versions/`
4. Run `alembic upgrade head`

## Code style

- Standard Python type hints everywhere
- Pydantic schemas for all I/O validation
- Async endpoints (`async def`) for DB queries
- Dependencies via FastAPI's `Depends()` mechanism
- `ruff` for linting (no config added yet)