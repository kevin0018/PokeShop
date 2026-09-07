# PokeShop Backend

FastAPI backend scaffold for PokeShop. The business contexts currently contain
placeholders; only `/health` and the generated API documentation are available.
PostgreSQL and Redis are provisioned by Compose for future repositories and caching.

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
