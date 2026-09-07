# VPS deployment

[English README](../README.md) · [README en español](../README.es.md)

PokeShop is deployed at **http://62.171.169.187** on the existing Contabo VPS.
Domain selection and HTTPS are still pending. This is a demonstration store with
no accounts, checkout or payment processing. Deployment is manual; GitHub pushes
do not deploy automatically.

## Runtime

```text
Internet :80 → host Nginx → 127.0.0.1:8091 → frontend Nginx
                                            ├─ Vue static files / SPA fallback
                                            └─ /api → FastAPI → PostgreSQL
```

`compose.production.yaml` is standalone: do not merge it with the development
Compose file. The project name is `pokeshop-prod`, with its own network and
`pokeshop-prod_postgres_data` volume. PostgreSQL and FastAPI publish no host ports.
The unrelated existing website and its containers remain in place.

| Service | RAM limit | Additional swap |
| --- | ---: | ---: |
| Static frontend / Nginx | 128 MiB | 0 |
| FastAPI, one worker | 512 MiB | 0 |
| PostgreSQL | 256 MiB | 0 |
| **Total** | **896 MiB** | **0** |

Redis is unused by the application and is omitted here. These limits cover the
running containers, not image builds or the other website. Builds run sequentially;
the frontend build limits the Node heap to 1.5 GiB. Container logs rotate at 10 MiB
with three files. Services restart automatically unless manually stopped.

## Server paths and operation

- Initial code release: `/opt/pokeshop/releases/7ae4f34`.
- Active release symlink: `/opt/pokeshop/current`.
- Production environment: `/opt/pokeshop/shared/.env`, mode `0600`.
- Initial database backup: `/opt/pokeshop/backups/initial-2026-09-07.dump`.
- Host routing: `/etc/nginx/sites-available/pokeshop`, enabled via a symlink.

The production password was generated on the VPS; it is separate from the local
development password and is never bundled into frontend assets. Required setting:
`POSTGRES_PASSWORD`; optional settings: `PRODUCTION_PORT` (8091) and
`ALLOWED_ORIGINS` (JSON array). Keep secrets and database backups out of Git.

Run on the VPS:

```sh
cd /opt/pokeshop/current
dc() { docker compose --env-file /opt/pokeshop/shared/.env -f compose.production.yaml "$@"; }
dc ps
dc logs --tail 100 backend
dc exec backend alembic current
```

For a future release, transfer an archive of the reviewed Git commit into a new
release directory. Keep the same environment file and Compose project name.
Back up the database before migrations, then run from the new release directory:

```sh
dc build backend
dc build frontend
dc run --rm --no-deps backend alembic upgrade head
dc up -d --wait
```

Update `/opt/pokeshop/current` only after successful health and route checks.
For an application rollback, rebuild and start the previous release using the same
project and environment. Database migrations may require a separate compatible
rollback or backup restore; changing the code symlink does not undo migrations.
Do not use `down -v`: it destroys the production database volume.

## Data and backups

The first deployment restored the existing PostgreSQL catalog, including offers,
upstream cache and Alembic history. It did not rerun import or pricing.
Administrative synchronization and repricing remain explicit:

```sh
dc exec backend python -m src.pokemon.infrastructure.sync
dc exec backend python -m src.pokemon.infrastructure.reprice
# --apply explicitly commits the previewed pricing policy.
```

Manual backup from the server shell:

```sh
umask 077
dc exec -T db pg_dump -U pokeshop -d pokeshop -Fc \
  > /opt/pokeshop/backups/catalog-$(date +%Y%m%d-%H%M%S).dump
```

Restore into a **new, empty database**, with application traffic stopped for the
cutover, using `pg_restore --exit-on-error --no-owner --no-privileges` and the
`pokeshop` database user. Never restore blindly over the active database. The initial
restore was verified; scheduled backups, off-server copies and disaster recovery
automation are still pending. An on-server backup alone does not protect against
loss of the VPS.

## Verification — 2026-09-07

- Both production images built successfully; frontend types and bundling passed.
- Nginx syntax and Compose health checks passed.
- All four Vue routes, favicon and catalog API returned HTTP 200 publicly.
- 1,351 offers; total stock 13,478; price/stock checksum matched the local source.
- Runtime used approximately 155 MiB at the initial check, within the 896 MiB cap.
- Existing website still returned HTTP 200; no PokeShop database/API host ports.
- All 33 Chromium tests passed against the public VPS URL: interactions and all
  four routes at five widths, in both languages and themes (80 generated captures).
- A controlled stop/start preserved the catalog checksum and restored healthy
  services; public routes and the existing website still returned HTTP 200.

[Actual capture from the deployed site](deployment-home.png).

## Next: domain and HTTPS

Choose a domain/subdomain, point its DNS to the VPS, extend the separate PokeShop
Nginx server name, and configure TLS and an HTTP-to-HTTPS redirect. Update allowed
origins and README demo links, then verify the certificate and routes. No domain
has been purchased and HTTPS is not currently configured for PokeShop.

Browser storage is scoped to the origin: a cart saved on localhost, the IP, or a
future HTTPS domain is separate. Deployments preserve the server catalog; they do
not copy a user's browser cart between origins.
