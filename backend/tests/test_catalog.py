"""Exercise the public API contract, including filtering and pagination."""

import unittest

from fastapi.testclient import TestClient
from main import create_app
from src.pokemon.presentation.pokemon_routes import get_catalog
from src.pokemon.application.catalog import Catalog
from src.pokemon.infrastructure.demo_repository import DemoPokemonRepository


class FixtureCatalog:
    async def search(self, q='', pokemon_type='', sort='number', limit=24, offset=0, generation=0, forms='all'):
        return Catalog(DemoPokemonRepository()).search(q, pokemon_type, sort, limit, offset)

    async def get(self, pokemon_id):
        return DemoPokemonRepository().get(pokemon_id)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.dependency_overrides[get_catalog] = FixtureCatalog
        self.client = TestClient(app, base_url="http://localhost")
        self.addCleanup(self.client.close)

    def test_catalog_and_detail_agree(self):
        result = self.client.get("/api/v1/pokemon").json()
        self.assertEqual(result["total"], 12)
        for item in result["items"]:
            self.assertEqual(self.client.get(f'/api/v1/pokemon/{item["id"]}').json(), item)
            self.assertGreater(item["price_cents"], 0)

    def test_filter_by_name_number_and_type(self):
        for query in ("PIKA", "#025"):
            result = self.client.get("/api/v1/pokemon", params={"q": query}).json()
            self.assertEqual([item["id"] for item in result["items"]], [25])
        result = self.client.get("/api/v1/pokemon", params={"type": "fuego"}).json()
        self.assertEqual([item["id"] for item in result["items"]], [4, 37])

    def test_pagination_after_sorting(self):
        result = self.client.get("/api/v1/pokemon?sort=price_desc&limit=1&offset=1").json()
        self.assertEqual(result["total"], 12)
        self.assertEqual(result["items"][0]["id"], 149)

    def test_empty_and_not_found(self):
        self.assertEqual(self.client.get("/api/v1/pokemon?q=missing").json(), {"items": [], "total": 0})
        self.assertEqual(self.client.get("/api/v1/pokemon/9999").status_code, 404)

    def test_invalid_query(self):
        for query in ("limit=101", "limit=0", "offset=-1", "sort=invalid"):
            self.assertEqual(self.client.get(f"/api/v1/pokemon?{query}").status_code, 422)
