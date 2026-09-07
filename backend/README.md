# PokeShop Backend

FastAPI with a PostgreSQL catalog, separate offers, Alembic migrations and an explicit resumable PokéAPI importer. See the [root README](../README.md) for all routes, import scope, architecture and memory limits.

From the repository root:

```sh
cp .env.example .env
# Set POSTGRES_PASSWORD in .env
docker compose up --build --wait
docker compose exec backend alembic upgrade head
docker compose exec backend python -m src.pokemon.infrastructure.sync
docker compose exec backend python -m unittest discover -s tests -v
```

`--refresh` explicitly refreshes upstream HTTP data; existing offers remain unchanged. Tests require an imported local database. The original demo adapter is only a test fixture. Redis is provisioned but unused.

API: http://localhost:8000; typed Swagger contract: http://localhost:8000/docs. `/health` checks the application, not database/cache connectivity.

Python 3.12 / Poetry 2.1.3. For local development, run `poetry install`, configure `DATABASE_URL` with the `postgresql+asyncpg` driver, then `poetry run alembic upgrade head` and `poetry run uvicorn main:app --reload`. Compose supplies internal service URLs. Connection configuration is shared by API, Alembic and importer. `ALLOWED_ORIGINS` and `ALLOWED_HOSTS` are JSON arrays. No accounts, orders, reservations or payment endpoints are implemented.

API, Alembic and sync share `src/database.py`: use backend-only `POSTGRES_*` variables (required password) or an encoded `DATABASE_URL`. Compose gets the password from the ignored root `.env`. Regions and chain depth are cached during sync. `python -m src.pokemon.infrastructure.reprice` previews the classic-v1 policy; `--apply` updates offers in one transaction without altering stock. See both root READMEs for factors and examples.

## Deployment status

**Live at [https://pokeshop-app.duckdns.org](https://pokeshop-app.duckdns.org)** on the Contabo VPS. HTTPS is enabled with automatic certificate renewal. Production uses the standalone root `compose.production.yaml`; the default Compose remains for development. See the [deployment runbook](../docs/deployment.md) for routing, private configuration, data and release procedures.
