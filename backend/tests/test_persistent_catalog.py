import asyncio
import contextlib
import io
import unittest

import httpx
from sqlalchemy import text

from src.pokemon.application.recommendations import recommend
from src.pokemon.infrastructure.postgres_repository import (
    PostgresCatalog,
    engine,
)
from src.pokemon.infrastructure.reprice import reprice
from src.pokemon.infrastructure.sync import Importer


class PersistentCatalogTests(unittest.TestCase):
    def run_async(self, fn):
        async def run():
            try:
                await fn()
            finally:
                await engine.dispose()

        asyncio.run(run())

    def test_units_forms_filters_pagination(self):
        async def check():
            repo = PostgresCatalog()
            p = await repo.get(25)
            self.assertEqual(
                (p["weight_kg"], p["height_m"], p["price_cents"], p["stock"]),
                (6, 0.4, 11200, 15),
            )
            p = await repo.get(10100)
            self.assertEqual(p["species_id"], 26)
            self.assertFalse(p["is_default"])
            self.assertIn("Alola", p["name"])
            first, total = await repo.search(
                pokemon_type="electrico",
                generation=1,
                forms="alternative",
                limit=2,
                sort="weight_desc",
            )
            second, total2 = await repo.search(
                pokemon_type="electrico",
                generation=1,
                forms="alternative",
                limit=2,
                offset=2,
                sort="weight_desc",
            )
            self.assertEqual(total, total2)
            self.assertTrue(first)
            self.assertFalse({p["id"] for p in first} & {p["id"] for p in second})
            for p in first + second:
                self.assertEqual(p["generation"], 1)
                self.assertFalse(p["is_default"])
                self.assertIn("electrico", p["types"])

        self.run_async(check)

    def test_reprice_preview_and_repeat_preserve_all_offers_and_stock(self):
        async def check():
            async def snapshot():
                async with engine.connect() as conn:
                    return (
                        await conn.execute(
                            text(
                                "SELECT pokemon_id,price_cents,stock,base_cents,pricing_version,pricing_breakdown::text FROM offers ORDER BY pokemon_id"
                            )
                        )
                    ).all()

            before = await snapshot()
            with contextlib.redirect_stdout(io.StringIO()):
                await reprice()
                self.assertEqual(before, await snapshot())
                await reprice(apply=True)
                self.assertEqual(before, await snapshot())
            self.assertGreater(len(before), 1000)

        self.run_async(check)

    def test_regions_and_height_order(self):
        async def check():
            repo = PostgresCatalog()
            self.assertEqual((await repo.get(1))["region"], "kanto")
            self.assertEqual((await repo.get(10100))["region"], "alola")
            self.assertEqual((await repo.get(899))["region"], "hisui")
            self.assertEqual((await repo.get(6))["evolution_stage"], 3)
            self.assertEqual((await repo.get(10034))["evolution_stage"], 3)
            items, total = await repo.search(
                region="alola", sort="height_desc", limit=24
            )
            self.assertGreater(total, 24)
            self.assertTrue(all(p["region"] == "alola" for p in items))
            heights = [p["height_m"] for p in items]
            self.assertEqual(heights, sorted(heights, reverse=True))

        self.run_async(check)

    def test_cached_repeat_recovery_preserves_offers(self):
        async def check():
            def offline(request):
                raise RuntimeError("offline")

            async with httpx.AsyncClient(
                transport=httpx.MockTransport(offline)
            ) as client:
                importer = Importer(client)
                before = await PostgresCatalog().get(25)
                await importer.entry("https://pokeapi.co/api/v2/pokemon/25/")
                with self.assertRaises(RuntimeError):
                    await importer.entry("https://pokeapi.co/api/v2/missing/0/")
                await importer.entry("https://pokeapi.co/api/v2/pokemon/25/")
                self.assertEqual(before, await PostgresCatalog().get(25))

        self.run_async(check)

    def test_recommendations_exclude_species_and_unavailable(self):
        seed = {
            "id": 1,
            "species_id": 1,
            "types": ["planta"],
            "generation": 1,
            "price_cents": 2490,
            "stock": 1,
        }
        candidates = [
            dict(seed, id=i, species_id=i, stock=0 if i == 2 else 1)
            for i in range(1, 8)
        ] + [dict(seed, id=10001)]
        result = recommend(candidates, [seed])
        self.assertEqual([p["id"] for p in result], [3, 4, 5, 6])
        self.assertTrue(all(p["reason"] == "sharedType" for p in result))
