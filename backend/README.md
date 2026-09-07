# PokeShop Backend

FastAPI catalog API for PokeShop, with a domain repository port and a read-only
demonstration adapter. PostgreSQL and Redis are provisioned for future persistence.

- `GET /api/v1/pokemon`: optional `q`, `type`, `sort`, `limit` (1–100), `offset`.
  Sort values: `number`, `name`, `price_asc`, `price_desc`.
- `GET /api/v1/pokemon/{id}`: detail, or HTTP 404.
- `GET /health`: application health; does not probe database/cache connections.

The 12 demo records have fictional prices (integer EUR cents) and stock. There
are no database writes, migrations or seeds. User/account routes are not implemented.

Run tests with `docker compose exec backend python -m unittest discover -s tests -v`.

## Docker development

From the repository root:

```sh
docker compose up --build --wait
docker compose logs -f backend
```

API: http://localhost:8000, Swagger: http://localhost:8000/docs.
Source changes reload automatically. Dependencies use Python 3.12 and Poetry 2.1.3.
Rebuild after changing `pyproject.toml` and `poetry.lock`.

## Local development

Install Python 3.12 and Poetry 2.1.3, then from `backend/`:

```sh
poetry install
# Copy .env.example to .env and adjust values for your local services.
poetry run uvicorn main:app --reload
```

The application reads `.env` without overriding existing environment variables.
`ALLOWED_ORIGINS` and `ALLOWED_HOSTS` are JSON arrays. Compose supplies its own
values and internal database/cache hostnames. Other example settings are reserved
for the business functionality; no external API keys are needed to start the scaffold.
