import unittest

from src.pokemon.application.pricing import calculate_price, evolution_stage, region_for


class PricingTests(unittest.TestCase):
    def test_agreed_examples(self):
        for weight, stage, cents in [
            (6.9, 1, 10530),
            (100, 3, 56380),
            (90.5, 3, 51910),
            (9.9, 2, 12880),
        ]:
            self.assertEqual(
                calculate_price(
                    {
                        "weight_kg": weight,
                        "evolution_stage": stage,
                        "generation": 1,
                        "region": "kanto",
                    }
                )["price_cents"],
                cents,
            )

    def test_pokedex_number_does_not_change_price(self):
        p = {"weight_kg": 10, "evolution_stage": 2, "generation": 1, "region": "kanto"}
        self.assertEqual(
            calculate_price(dict(p, id=1, species_id=1)),
            calculate_price(dict(p, id=500, species_id=500)),
        )

    def test_missing_and_weight_cap(self):
        self.assertEqual(calculate_price({})["price_cents"], 3000)
        self.assertEqual(len(calculate_price({})["pricing_breakdown"]["missing"]), 4)
        self.assertEqual(
            calculate_price({"weight_kg": 2000}), calculate_price({"weight_kg": 1000})
        )

    def test_region_overrides(self):
        self.assertEqual(
            region_for({"name": "raichu-alola"}, {"name": "raichu"}, "kanto"), "alola"
        )
        self.assertEqual(
            region_for({"name": "enamorus-incarnate"}, {"name": "enamorus"}, "galar"),
            "hisui",
        )
        self.assertEqual(
            region_for({"name": "charizard-mega-x"}, {"name": "charizard"}, "kanto"),
            "kanto",
        )

    def test_branch_depth(self):
        def leaf(i):
            return {
                "species": {"url": f"https://pokeapi.co/api/v2/pokemon-species/{i}/"},
                "evolves_to": [],
            }

        chain = leaf(1)
        chain["evolves_to"] = [leaf(2), leaf(3)]
        chain["evolves_to"][1]["evolves_to"] = [leaf(4)]
        self.assertEqual(evolution_stage(chain, 2), 2)
        self.assertEqual(evolution_stage(chain, 4), 3)
        self.assertIsNone(evolution_stage(chain, 99))
