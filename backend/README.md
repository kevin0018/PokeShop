# PokeShop Backend

FastAPI with a PostgreSQL catalog, separate offers, Alembic migrations and an explicit resumable PokéAPI importer. See the [root README](../README.md) for all routes, import scope, architecture and memory limits.

From the repository root:

```sh
docker compose up --build --wait
docker compose exec backend alembic upgrade head
docker compose exec backend python -m src.pokemon.infrastructure.sync
docker compose exec backend python -m unittest discover -s tests -v
```

`--refresh` explicitly refreshes upstream HTTP data; existing offers remain unchanged. Tests require an imported local database. The original demo adapter is only a test fixture and the source of initial offer defaults. Redis is provisioned but unused.

API: http://localhost:8000; typed Swagger contract: http://localhost:8000/docs. `/health` checks the application, not database/cache connectivity.

Python 3.12 / Poetry 2.1.3. For local development, run `poetry install`, configure `DATABASE_URL` with the `postgresql+asyncpg` driver, then `poetry run alembic upgrade head` and `poetry run uvicorn main:app --reload`. Compose supplies internal service URLs. Alembic and the import CLI read `DATABASE_URL` from the process environment; export it when running outside Docker. `ALLOWED_ORIGINS` and `ALLOWED_HOSTS` are JSON arrays. No accounts, orders, reservations or payment endpoints are implemented.
