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
   make migrate-auto m="add field"
   ```
4. Rebuild the image: `docker compose build app`

## Adding a new DB table

1. Define the model in `app/models.py` (inherit `Base`)
2. Run `make migrate-auto m="add new_table"` — this autogenerates and applies the migration
3. Review the migration file in `alembic/versions/`

## Generating architecture diagrams

Architecture diagrams in `docs/` are generated from scripts in [`docs/diagram_scripts/`](diagram_scripts/) using the [Diagrams](https://diagrams.mingrammer.com/) library.

```bash
pip install --user diagrams
python3 docs/diagram.py              # regenerate all
python3 docs/diagram_scripts/stack.py  # regenerate one
```

Three PNGs are produced:

| File | Where used |
|------|-----------|
| `architecture_diagram.png` | [Architecture](architecture.md) — deployment view |
| `module_diagram.png` | [Architecture](architecture.md) — internal module coupling |
| `stack_diagram.png` | [Home](index.md) — technology stack layers |

## Testing

Tests use **pytest** + **pytest-asyncio** + **httpx** (ASGI transport for the
FastAPI app, no real network). A dedicated `db-test` PostgreSQL container runs
alongside the main one — its data is ephemeral (tmpfs) and resets on restart.

The test suite sets `PICSHARE_INVITE_CODE=test-invite-42` so all registration
tests can use that value.

### Running tests

```bash
make test
```

This single command will:
1. Build and start all containers (`docker compose up --build -d`)
2. Create the test directories inside the app container
3. Run pytest with coverage (`--cov=app --cov-report=term --cov-report=html`)

After `make test`, coverage output is printed to the terminal and an HTML
report is written to `htmlcov/` (you can open `htmlcov/index.html` in a
browser to see per-file line-by-line coverage).

For CI or a quick check without the HTML report:

```bash
make test-ci
```

Tests auto-create/drop the schema per run via SQLAlchemy metadata. A dedicated
`db-test` PostgreSQL container runs alongside the main one — its data is
ephemeral (tmpfs) and resets on restart.

## TDD workflow

1. Write a failing test in `tests/`
2. Run the tests with the command above — new test fails
3. Implement the feature in `app/`
4. Run tests again — all pass
5. Repeat

## Code style

- Standard Python type hints everywhere
- Pydantic schemas for all I/O validation
- Async endpoints (`async def`) for DB queries
- Dependencies via FastAPI's `Depends()` mechanism

## Linting and type checking

Lint and type-checking run inside the `app` container (source is bind-mounted
so they check the live code on disk).

```bash
make lint        # Ruff lint + format check on app/ and tests/
make lint-fix    # auto-fix lint issues + format
make typecheck   # mypy type check on app/ (prod code only)
```

Config lives in `ruff.toml` (Ruff rules + line length) and `pyproject.toml`
(`[tool.mypy]`). Type stubs for third-party libraries (`types-python-jose`,
`types-passlib`) are pinned in `requirements.txt` so mypy keeps them fully
typed instead of silencing missing imports.