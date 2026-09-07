"""PostgreSQL catalog adapter. Offers never enter the upstream payload."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.database import database_url
from src.pokemon.application.recommendations import recommend

engine = create_async_engine(database_url(), pool_size=4, max_overflow=0)

FEATURED = [143, 448, 10100, 25, 133, 722]


class PostgresCatalog:
    async def search(
        self,
        q="",
        pokemon_type="",
        sort="number",
        limit=24,
        offset=0,
        generation=0,
        forms="all",
        ids=None,
        region="",
    ):
        clauses, params = [], {"limit": limit, "offset": offset}
        if q:
            params["q"] = (
                "%" + q.strip().lower().replace("%", r"\%").replace("_", r"\_") + "%"
            )
            clauses.append(
                "(lower(p.data->>'name') LIKE :q OR p.data->'names'->>'es' ILIKE :q OR p.data->>'species_id' = :dex)"
            )
            params["dex"] = str(int(q.lstrip("#"))) if q.lstrip("#").isdigit() else ""
        if pokemon_type:
            clauses.append("p.data->'types' ? :type")
            params["type"] = pokemon_type
        if region:
            clauses.append("p.data->>'region' = :region")
            params["region"] = region
        if generation:
            clauses.append("(p.data->>'generation')::int = :generation")
            params["generation"] = generation
        if forms != "all":
            clauses.append("(p.data->>'is_default')::boolean = :default")
            params["default"] = forms == "default"
        if ids is not None:
            clauses.append("p.id = ANY(:ids)")
            params["ids"] = ids
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        order = {
            "number": "p.id",
            "name": "p.data->>'name'",
            "price_asc": "o.price_cents",
            "price_desc": "o.price_cents DESC",
            "height_asc": "(p.data->>'height_m')::float",
            "height_desc": "(p.data->>'height_m')::float DESC",
            "weight_asc": "(p.data->>'weight_kg')::float",
            "weight_desc": "(p.data->>'weight_kg')::float DESC",
        }[sort]
        async with engine.connect() as conn:
            total = await conn.scalar(
                text(
                    "SELECT count(*) FROM pokemon p JOIN offers o ON o.pokemon_id=p.id"
                    + where
                ),
                params,
            )
            rows = (
                await conn.execute(
                    text(
                        "SELECT p.data, o.price_cents, o.stock, o.base_cents, o.pricing_version, o.pricing_breakdown FROM pokemon p JOIN offers o ON o.pokemon_id=p.id"
                        + where
                        + " ORDER BY "
                        + order
                        + ", p.id LIMIT :limit OFFSET :offset"
                    ),
                    params,
                )
            ).mappings()
            return [
                dict(
                    row["data"],
                    price_cents=row["price_cents"],
                    stock=row["stock"],
                    base_cents=row["base_cents"],
                    pricing_version=row["pricing_version"],
                    pricing_breakdown=row["pricing_breakdown"],
                )
                for row in rows
            ], total

    async def get(self, pokemon_id):
        items, _ = await self.search(ids=[pokemon_id])
        return items[0] if items else None

    async def featured(self):
        items, _ = await self.search(ids=FEATURED)
        return sorted(
            (p for p in items if p["stock"] > 0), key=lambda p: FEATURED.index(p["id"])
        )

    async def metadata(self):
        async with engine.connect() as conn:
            generations = list(
                (
                    await conn.execute(
                        text(
                            "SELECT DISTINCT (data->>'generation')::int FROM pokemon ORDER BY 1"
                        )
                    )
                ).scalars()
            )
            types = list(
                (
                    await conn.execute(
                        text(
                            "SELECT DISTINCT jsonb_array_elements_text(data->'types') FROM pokemon ORDER BY 1"
                        )
                    )
                ).scalars()
            )
            regions = list(
                (
                    await conn.execute(
                        text(
                            "SELECT DISTINCT data->>'region' FROM pokemon WHERE data->>'region' IS NOT NULL ORDER BY 1"
                        )
                    )
                ).scalars()
            )
        from src.pokemon.application.pricing import REGION_NAMES, REGIONS

        return {
            "generations": generations,
            "types": types,
            "regions": [
                {
                    "id": r,
                    "names": dict(
                        zip(("es", "en"), REGION_NAMES.get(r, (r, r)), strict=True)
                    ),
                }
                for r in sorted(
                    regions, key=lambda r: REGIONS.index(r) if r in REGIONS else 99
                )
            ],
        }

    async def recommendations(self, ids):
        if not ids:
            return [dict(p, reason="featured") for p in (await self.featured())[:4]]
        seeds, _ = await self.search(ids=ids, limit=100)
        if not seeds:
            return []
        items, total = await self.search(limit=100)
        for offset in range(100, total, 100):
            page, _ = await self.search(limit=100, offset=offset)
            items.extend(page)
        return recommend(items, seeds)
