import asyncio
import unittest
import httpx
from src.pokemon.infrastructure.postgres_repository import PostgresCatalog, engine, recommend
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
            self.assertEqual((p['weight_kg'],p['height_m'],p['price_cents'],p['stock']),(6,.4,2990,15))
            p = await repo.get(10100)
            self.assertEqual(p['species_id'],26)
            self.assertFalse(p['is_default'])
            self.assertIn('Alola',p['name'])
            first,total = await repo.search(pokemon_type='electrico',generation=1,forms='alternative',limit=2,sort='weight_desc')
            second,total2 = await repo.search(pokemon_type='electrico',generation=1,forms='alternative',limit=2,offset=2,sort='weight_desc')
            self.assertEqual(total,total2)
            self.assertTrue(first)
            self.assertFalse({p['id'] for p in first}&{p['id'] for p in second})
            for p in first+second:
                self.assertEqual(p['generation'],1)
                self.assertFalse(p['is_default'])
                self.assertIn('electrico',p['types'])
        self.run_async(check)

    def test_cached_repeat_recovery_preserves_offers(self):
        async def check():
            def offline(request):
                raise RuntimeError('offline')
            async with httpx.AsyncClient(transport=httpx.MockTransport(offline)) as client:
                importer = Importer(client)
                before = await PostgresCatalog().get(25)
                await importer.entry('https://pokeapi.co/api/v2/pokemon/25/')
                with self.assertRaises(RuntimeError):
                    await importer.entry('https://pokeapi.co/api/v2/missing/0/')
                await importer.entry('https://pokeapi.co/api/v2/pokemon/25/')
                self.assertEqual(before,await PostgresCatalog().get(25))
        self.run_async(check)

    def test_recommendations_exclude_species_and_unavailable(self):
        seed = dict(id=1,species_id=1,types=['planta'],generation=1,price_cents=2490,stock=1)
        candidates = [dict(seed,id=i,species_id=i,stock=0 if i==2 else 1) for i in range(1,8)] + [dict(seed,id=10001)]
        result = recommend(candidates,[seed])
        self.assertEqual([p['id'] for p in result],[3,4,5,6])
        self.assertTrue(all(p['reason']=='sharedType' for p in result))
