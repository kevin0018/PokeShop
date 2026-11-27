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
        habitat=None,
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
        if habitat:
            clauses.append("""EXISTS (
                SELECT 1 FROM api_cache species
                WHERE species.url = concat('https://pokeapi.co/api/v2/pokemon-species/', p.data->>'species_id', '/')
                  AND species.data->'habitat'->>'name' = :habitat
            )""")
            params["habitat"] = habitat
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
        # Same rounding and lower bound as adventure.content.credit_price.
        credit_price_sql = """GREATEST(100, ((100 + 2 * GREATEST(0,
            (SELECT COALESCE(SUM(value::int),0) FROM jsonb_each_text(p.data->'stats'))
            - 250) + 5) / 10) * 10)"""
        order = {
            "number": "p.id",
            "name": "p.data->>'name'",
            "price_asc": "o.price_cents",
            "price_desc": "o.price_cents DESC",
            "credit_asc": credit_price_sql,
            "credit_desc": credit_price_sql + " DESC",
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
        if not items:
            return None
        pokemon = items[0]
        species_id = pokemon.get("species_id") or pokemon_id
        async with engine.connect() as conn:
            chain = await conn.scalar(
                text("""
                    SELECT chain.data->'chain' FROM api_cache species
                    JOIN api_cache chain ON chain.url = species.data->'evolution_chain'->>'url'
                    WHERE species.url = :species_url
                """),
                {"species_url": f"https://pokeapi.co/api/v2/pokemon-species/{species_id}/"},
            )
            if chain:
                species_ids = []
                stage = [chain]
                while stage:
                    species_ids.extend(
                        int(node["species"]["url"].rstrip("/").split("/")[-1])
                        for node in stage
                    )
                    stage = [child for node in stage for child in node.get("evolves_to", [])]
                if len(species_ids) > 1:
                    rows = await conn.execute(
                        text("""
                            SELECT p.id, p.data->>'name' AS name, p.data->'names' AS names,
                                   p.data->>'image_url' AS image_url
                            FROM pokemon p JOIN offers o ON o.pokemon_id = p.id
                            WHERE (p.data->>'species_id')::int = ANY(:ids)
                              AND (p.id = :current_id OR (
                                (p.data->>'species_id')::int <> :species_id
                                AND (p.data->>'is_default')::boolean))
                            ORDER BY array_position(CAST(:ids AS integer[]), (p.data->>'species_id')::int)
                        """),
                        {"ids": species_ids, "current_id": pokemon_id, "species_id": species_id},
                    )
                    pokemon["evolution_family"] = [dict(row) for row in rows.mappings()]
        return pokemon

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
