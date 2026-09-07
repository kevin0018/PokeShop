# Development resources

Docker Compose enforces these memory limits per running container:

| Service | Memory limit |
| --- | --- |
| Vue / Vite | 2 GiB |
| FastAPI | 512 MiB |
| PostgreSQL | 256 MiB |
| Redis | 128 MiB |

The total is 2,944 MiB (2.875 GiB). `memswap_limit` equals `mem_limit`, so
containers cannot consume additional swap. Redis caps cached data at 64 MiB
with `allkeys-lru` eviction, leaving room for its runtime and persistence.
These limits do not cap Docker Desktop, its VM, or image build processes.

Inspect actual usage with `docker stats --no-stream`. Change the limits in
`compose.yaml`, then apply them with `docker compose up --wait`.

The authorized ceiling, only if memory pressure requires it, is 4 GiB total: frontend 2 GiB, backend 1 GiB, PostgreSQL 768 MiB and Redis 256 MiB, each with equal RAM/swap limits. The frontend was raised to 2 GiB after overlapping browser verification processes exhausted 1 GiB; the other services retain their original caps. Checks run sequentially.
