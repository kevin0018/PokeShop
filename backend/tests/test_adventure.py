"""Real PostgreSQL API tests. Run only against a disposable adventure_test database."""
import asyncio
import concurrent.futures
import copy
import json
import random
import unittest
import uuid
from datetime import timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from main import create_app
from src.adventure.battle import (
    available_moves,
    damage,
    effectiveness,
    fighter,
    resolve_turn,
)
from src.adventure.content import GYMS, LOADOUTS, SHOP_IDS, credit_price, move_data
from src.adventure.routes import get_engine
from src.adventure.security import COOKIE, digest, hash_password, verify_password
from src.database import database_url


def sample(pokemon_id=1, types=None):
    return {
        "id": pokemon_id,
        "name": f"Pokemon {pokemon_id}",
        "names": {},
        "types": types or ["planta"],
        "stats": {
            k: 50
            for k in [
                "hp",
                "attack",
                "defense",
                "special-attack",
                "special-defense",
                "speed",
            ]
        },
    }


class RulesTests(unittest.TestCase):
    def test_real_kanto_stats_have_a_viable_purchase_and_gym_progression(self):
        fixture = json.loads(
            (Path(__file__).parent / "fixtures/adventure_kanto.json").read_text(
                encoding="utf-8-sig"
            )
        )
        data = {p["id"]: p for p in fixture["pokemon"]}
        budget = 1000 - credit_price(data[1]) - credit_price(data[6])
        roster = [1, 6]
        for gym in GYMS:
            additions = [94] if gym["id"] == 4 else [135] if gym["id"] == 6 else []
            for pokemon_id in additions:
                price = credit_price(data[pokemon_id])
                self.assertGreaterEqual(budget, price)
                budget -= price
                roster.append(pokemon_id)
            lead = 94 if gym["id"] == 5 else 135 if gym["id"] == 6 else 1
            order = [lead, *[i for i in roster if i != lead]]
            state = {
                "status": "active",
                "turn": 1,
                "events": [],
                "reward": 0,
                "player": [fighter(data[i]) for i in order],
                "opponent": [fighter(data[i], gym["level"]) for i in gym["pokemon"]],
                "player_active": 0,
                "opponent_active": 0,
            }
            rng = random.Random(1)
            for _ in range(100):
                if state["status"] != "active":
                    break
                player = state["player"][state["player_active"]]
                foe = state["opponent"][state["opponent_active"]]
                best = max(
                    available_moves(player),
                    key=lambda m: damage(player, foe, m) * m["accuracy"],
                )
                state = resolve_turn(state, {"kind": "move", "move": best["id"]}, rng)
            self.assertEqual(state["status"], "won", f"Gym {gym['id']}")
            budget += gym["reward"]
        self.assertEqual(budget, 490)

    def test_hashes_are_salted_and_verified(self):
        encoded = hash_password("test-password-123")
        self.assertNotEqual(encoded, hash_password("test-password-123"))
        self.assertTrue(verify_password("test-password-123", encoded))
        self.assertFalse(verify_password("wrong", encoded))

    def test_type_chart_dual_types_and_immunity(self):
        self.assertEqual(effectiveness("planta", ["roca", "tierra"]), 4)
        self.assertEqual(effectiveness("electrico", ["tierra", "agua"]), 0)
        self.assertEqual(effectiveness("fuego", ["agua", "dragon"]), 0.25)

    def test_turn_does_not_mutate_previous_and_spends_pp(self):
        state = self.state()
        before = copy.deepcopy(state)
        result = resolve_turn(
            state, {"kind": "move", "move": "vine-whip"}, random.Random(3)
        )
        self.assertEqual(state, before)
        self.assertEqual(result["player"][0]["moves"][1]["pp"], 24)
        self.assertLess(result["opponent"][0]["hp"], before["opponent"][0]["hp"])
        self.assertEqual(result["turn"], 2)

    def state(self):
        return {
            "status": "active",
            "turn": 1,
            "events": [],
            "player": [fighter(sample())],
            "opponent": [fighter(sample(74, ["roca", "tierra"]))],
            "player_active": 0,
            "opponent_active": 0,
            "reward": 0,
        }

    def test_faint_cancels_second_attack_and_selects_next(self):
        state = self.state()
        state["player"][0]["stats"]["speed"] = 500
        state["opponent"][0]["hp"] = 1
        state["opponent"].append(fighter(sample(95, ["roca", "tierra"])))
        result = resolve_turn(
            state, {"kind": "move", "move": "vine-whip"}, random.Random(3)
        )
        self.assertEqual(result["opponent_active"], 1)
        self.assertEqual(result["player"][0]["hp"], state["player"][0]["hp"])

    def test_priority_precedes_speed(self):
        state = self.state()
        state["player"][0] = fighter(sample(25, ["electrico"]))
        state["player"][0]["stats"]["speed"] = 1
        state["opponent"][0]["stats"]["speed"] = 500
        result = resolve_turn(
            state, {"kind": "move", "move": "quick-attack"}, random.Random(3)
        )
        self.assertEqual(result["events"][0]["side"], "player")

    def test_switch_allows_enemy_attack_invalid_actions_rejected(self):
        state = self.state()
        state["player"].append(fighter(sample(7, ["agua"])))
        result = resolve_turn(state, {"kind": "switch", "slot": 1}, random.Random(3))
        self.assertEqual(result["player_active"], 1)
        self.assertLess(result["player"][1]["hp"], state["player"][1]["hp"])
        for action in [
            {"kind": "move", "move": "fake"},
            {"kind": "switch", "slot": 0},
            {"kind": "switch", "slot": 6},
        ]:
            with self.assertRaises(ValueError):
                resolve_turn(state, action)

    def test_struggle_available_after_all_pp_exhausted(self):
        state = self.state()
        for move in state["player"][0]["moves"]:
            move["pp"] = 0
        result = resolve_turn(
            state, {"kind": "move", "move": "struggle"}, random.Random(3)
        )
        self.assertTrue(any(e["kind"] == "recoil" for e in result["events"]))
        with self.assertRaises(ValueError):
            resolve_turn(state, {"kind": "move", "move": "tackle"})

    def test_stab_and_stats_affect_damage(self):
        grass, rock = fighter(sample()), fighter(sample(74, ["roca", "tierra"]))
        self.assertGreater(
            damage(grass, rock, move_data("vine-whip")),
            damage(grass, rock, move_data("tackle")),
        )
        self.assertEqual(credit_price(sample()), 200)


@unittest.skipUnless(
    database_url().database.startswith("adventure_test"),
    "Requires disposable adventure_test database",
)
class AdventureAPITests(unittest.TestCase):
    def setUp(self):
        self.db = create_async_engine(database_url(), poolclass=NullPool)
        self.code = "test-invitation-" + uuid.uuid4().hex
        self.expired = "expired-invitation-" + uuid.uuid4().hex
        self.revoked = "revoked-invitation-" + uuid.uuid4().hex
        self.run_async(self.prepare())
        self.app = create_app()
        self.app.dependency_overrides[get_engine] = lambda: self.db
        self.client = TestClient(self.app, base_url="http://localhost")
        self.addCleanup(self.client.close)

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    async def prepare(self):
        async with self.db.begin() as conn:
            await conn.execute(
                text("TRUNCATE trainers,invitations,auth_attempts CASCADE")
            )
            for code, interval, revoked in [
                (self.code, timedelta(days=1), False),
                (self.expired, timedelta(days=-1), False),
                (self.revoked, timedelta(days=1), True),
            ]:
                await conn.execute(
                    text(
                        "INSERT INTO invitations(code_hash,expires_at,revoked) VALUES (:code,now() + CAST(:interval AS interval),:revoked)"
                    ),
                    {"code": digest(code), "interval": interval, "revoked": revoked},
                )
            for pokemon_id in LOADOUTS:
                data = sample(
                    pokemon_id,
                    ["roca", "tierra"] if pokemon_id in [74, 95] else ["planta"],
                )
                await conn.execute(
                    text(
                        "INSERT INTO pokemon(id,data) VALUES (:id,CAST(:data AS jsonb)) ON CONFLICT(id) DO UPDATE SET data=excluded.data"
                    ),
                    {"id": pokemon_id, "data": json.dumps(data)},
                )

    def register(self, username="trainer_one", code=None):
        return self.client.post(
            "/api/v1/adventure/register",
            json={
                "username": username,
                "password": "test-password-123",
                "invitation": code or self.code,
            },
        )

    def sign_in(self):
        self.assertEqual(self.register().status_code, 201)
        self.me = self.client.get("/api/v1/adventure/me").json()
        self.headers = {"X-CSRF-Token": self.me["csrf_token"]}

    def post(self, path, body):
        return self.client.post(
            "/api/v1/adventure/" + path, json=body, headers=self.headers
        )

    def setup_team(self):
        self.sign_in()
        self.assertEqual(self.post("purchases", {"pokemon_id": 1}).status_code, 200)
        self.assertEqual(
            self.client.put(
                "/api/v1/adventure/team", json={"ids": [1]}, headers=self.headers
            ).status_code,
            200,
        )

    def test_invitation_single_use_expiry_revocation_and_initial_balance(self):
        for code in [self.expired, self.revoked, "wrong-code-long-enough"]:
            self.assertEqual(self.register(code=code).status_code, 403)
        self.sign_in()
        self.assertEqual(self.me["credits"], 1000)
        self.assertEqual(self.register("trainer_two").status_code, 403)
        self.assertEqual(
            self.client.get("/api/v1/adventure/me").json()["credits"], 1000
        )

    def test_auth_csrf_origin_logout_and_account_ownership(self):
        self.assertEqual(self.client.get("/api/v1/adventure/me").status_code, 401)
        self.sign_in()
        self.assertEqual(
            self.client.post(
                "/api/v1/adventure/purchases", json={"pokemon_id": 1}
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/adventure/purchases",
                json={"pokemon_id": 1},
                headers={**self.headers, "Origin": "https://evil.invalid"},
            ).status_code,
            403,
        )
        self.assertEqual(self.post("logout", {}).status_code, 200)
        self.assertEqual(self.client.get("/api/v1/adventure/me").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/api/v1/adventure/login",
                json={"username": "trainer_one", "password": "wrong-password"},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/adventure/login",
                json={"username": "TRAINER_ONE", "password": "test-password-123"},
            ).status_code,
            200,
        )
        self.assertIn(
            "httponly",
            self.client.cookies.get(COOKIE)
            and self.client.post(
                "/api/v1/adventure/login",
                json={"username": "trainer_one", "password": "test-password-123"},
            )
            .headers["set-cookie"]
            .lower(),
        )

    def test_checkout_is_atomic_and_repeated_confirmation_is_free(self):
        self.sign_in()
        request_id = str(uuid.uuid4())
        body = {"ids": [1, 4], "request_id": request_id}
        result = self.post("checkout", body)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["total"], 400)
        self.assertEqual(self.post("checkout", body).json(), result.json())
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["credits"], 600)
        self.assertEqual(len(me["collection"]), 2)
        self.assertEqual(
            self.post("checkout", {"ids": [7], "request_id": request_id}).status_code,
            409,
        )
        self.assertEqual(
            self.post(
                "checkout", {"ids": [7, 1], "request_id": str(uuid.uuid4())}
            ).status_code,
            409,
        )
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["credits"], 600)
        self.assertNotIn(7, [p["id"] for p in me["collection"]])
        self.assertEqual(
            self.post(
                "checkout", {"ids": [7, 7], "request_id": str(uuid.uuid4())}
            ).status_code,
            422,
        )

    def test_sale_uses_paid_price_removes_team_and_never_credits_twice(self):
        self.setup_team()
        sale = {"pokemon_id": 1, "request_id": str(uuid.uuid4())}
        result = self.post("sales", sale)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["refund"], 100)
        self.assertEqual(self.post("sales", sale).json(), result.json())
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual((me["credits"], me["team"], me["collection"]), (900, [], []))
        self.assertEqual(
            self.post("sales", {**sale, "request_id": str(uuid.uuid4())}).status_code,
            404,
        )
        self.assertEqual(self.post("purchases", {"pokemon_id": 1}).status_code, 200)
        self.assertEqual(self.post("sales", sale).status_code, 200)
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["credits"], 700)
        self.assertEqual(len(me["collection"]), 1)
        self.assertEqual(me["collection"][0]["sale_price"], 100)

    def test_sale_during_battle_and_concurrent_checkout(self):
        self.setup_team()
        self.assertEqual(self.post("battles", {"gym_id": 1}).status_code, 201)
        self.assertEqual(
            self.post(
                "sales", {"pokemon_id": 1, "request_id": str(uuid.uuid4())}
            ).status_code,
            409,
        )
        body = {"ids": [4, 7], "request_id": str(uuid.uuid4())}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: self.post("checkout", body), range(2)))
        self.assertEqual([r.status_code for r in results], [200, 200])
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["credits"], 400)
        self.assertEqual(len(me["collection"]), 3)

    def test_buy_server_price_duplicate_and_insufficient_balance(self):
        self.sign_in()
        self.assertEqual(
            self.post(
                "purchases", {"pokemon_id": 1, "price": 0, "credits": 9999}
            ).status_code,
            200,
        )
        self.assertEqual(self.client.get("/api/v1/adventure/me").json()["credits"], 800)
        self.assertEqual(self.post("purchases", {"pokemon_id": 1}).status_code, 409)
        for pokemon_id in SHOP_IDS[1:5]:
            self.assertEqual(
                self.post("purchases", {"pokemon_id": pokemon_id}).status_code, 200
            )
        self.assertEqual(self.post("purchases", {"pokemon_id": 6}).status_code, 409)
        self.assertEqual(self.post("purchases", {"pokemon_id": 150}).status_code, 404)

    def test_concurrent_purchase_is_charged_once(self):
        self.sign_in()
        token = self.client.cookies.get(COOKIE)

        def purchase(_):
            with TestClient(self.app, base_url="http://localhost") as client:
                client.cookies.set(COOKIE, token)
                return client.post(
                    "/api/v1/adventure/purchases",
                    json={"pokemon_id": 1},
                    headers=self.headers,
                ).status_code

        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(purchase, range(2)))
        self.assertEqual(sorted(results), [200, 409])
        self.assertEqual(self.client.get("/api/v1/adventure/me").json()["credits"], 800)

    def test_team_validation_and_gym_progression(self):
        self.sign_in()
        self.assertEqual(self.post("battles", {"gym_id": 1}).status_code, 422)
        self.assertEqual(self.post("battles", {"gym_id": 2}).status_code, 403)
        for ids in [[1], [1, 1], list(range(1, 8))]:
            self.assertEqual(
                self.client.put(
                    "/api/v1/adventure/team", json={"ids": ids}, headers=self.headers
                ).status_code,
                422,
            )

    def test_battle_snapshot_revision_and_resume(self):
        self.setup_team()
        battle = self.post("battles", {"gym_id": 1}).json()
        self.assertEqual(self.post("battles", {"gym_id": 1}).status_code, 409)
        self.assertEqual(
            self.client.put(
                "/api/v1/adventure/team", json={"ids": []}, headers=self.headers
            ).status_code,
            409,
        )
        path = f'battles/{battle["id"]}/turns'
        action = {
            "revision": 0,
            "kind": "move",
            "move": "vine-whip",
            "status": "won",
            "reward": 99999,
        }
        result = self.post(path, action)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["revision"], 1)
        self.assertEqual(self.post(path, action).status_code, 409)
        self.assertEqual(
            self.client.get(f'/api/v1/adventure/battles/{battle["id"]}').json(),
            result.json(),
        )
        self.assertEqual(
            self.post(path, {"revision": 1, "kind": "surrender"}).json()["status"],
            "surrendered",
        )

    def test_first_victory_awards_once_and_unlocks_next_gym(self):
        self.setup_team()

        async def weaken(battle_id):
            async with self.db.begin() as conn:
                state = await conn.scalar(
                    text("SELECT state FROM trainer_battles WHERE id=:id"),
                    {"id": uuid.UUID(battle_id)},
                )
                state["opponent"][0]["hp"] = 1
                state["opponent"][1]["hp"] = 0
                await conn.execute(
                    text(
                        "UPDATE trainer_battles SET state=CAST(:state AS jsonb) WHERE id=:id"
                    ),
                    {"id": uuid.UUID(battle_id), "state": json.dumps(state)},
                )

        for expected_reward in [150, 0]:
            battle = self.post("battles", {"gym_id": 1}).json()
            self.run_async(weaken(battle["id"]))
            result = self.post(
                f'battles/{battle["id"]}/turns',
                {"revision": 0, "kind": "move", "move": "vine-whip"},
            ).json()
            self.assertEqual(
                (result["status"], result["reward"]), ("won", expected_reward)
            )
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["credits"], 950)
        self.assertEqual(me["medals"], [1])
        self.assertEqual(self.post("battles", {"gym_id": 2}).status_code, 201)

    def test_rate_limit_survives_new_client(self):
        for _ in range(20):
            response = self.client.post(
                "/api/v1/adventure/login",
                json={"username": "missing_user", "password": "test-password-123"},
            )
            self.assertEqual(response.status_code, 401)
        with TestClient(self.app, base_url="http://localhost") as other:
            self.assertEqual(
                other.post(
                    "/api/v1/adventure/login",
                    json={"username": "missing_user", "password": "test-password-123"},
                ).status_code,
                429,
            )

    def test_concurrent_invitation_redemption_creates_one_trainer(self):
        def redeem(index):
            with TestClient(self.app, base_url="http://localhost") as client:
                return client.post(
                    "/api/v1/adventure/register",
                    json={
                        "username": f"concurrent_{index}",
                        "password": "test-password-123",
                        "invitation": self.code,
                    },
                ).status_code

        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            self.assertEqual(sorted(pool.map(redeem, range(2))), [201, 403])

    def test_battle_cannot_be_read_or_changed_by_another_trainer(self):
        self.setup_team()
        battle = self.post("battles", {"gym_id": 1}).json()

        async def invite():
            async with self.db.begin() as conn:
                await conn.execute(
                    text("UPDATE invitations SET used_by=NULL WHERE code_hash=:code"),
                    {"code": digest(self.code)},
                )

        self.run_async(invite())
        with TestClient(self.app, base_url="http://localhost") as other:
            self.assertEqual(
                other.post(
                    "/api/v1/adventure/register",
                    json={
                        "username": "other_trainer",
                        "password": "test-password-123",
                        "invitation": self.code,
                    },
                ).status_code,
                201,
            )
            csrf = other.get("/api/v1/adventure/me").json()["csrf_token"]
            self.assertEqual(
                other.get(f'/api/v1/adventure/battles/{battle["id"]}').status_code, 404
            )
            self.assertEqual(
                other.post(
                    f'/api/v1/adventure/battles/{battle["id"]}/turns',
                    json={"revision": 0, "kind": "surrender"},
                    headers={"X-CSRF-Token": csrf},
                ).status_code,
                404,
            )

    def test_expired_session_does_not_allow_purchases(self):
        self.sign_in()

        async def expire():
            async with self.db.begin() as conn:
                await conn.execute(
                    text(
                        "UPDATE trainer_sessions SET expires_at=now() - interval '1 second'"
                    )
                )

        self.run_async(expire())
        self.assertEqual(self.client.get("/api/v1/adventure/me").status_code, 401)
        self.assertEqual(self.post("purchases", {"pokemon_id": 1}).status_code, 401)

    def test_complete_campaign_awards_each_badge_once(self):
        self.sign_in()
        ids = [1, 4, 7, 25]
        for pokemon_id in ids:
            self.assertEqual(
                self.post("purchases", {"pokemon_id": pokemon_id}).status_code, 200
            )
        self.assertEqual(
            self.client.put(
                "/api/v1/adventure/team", json={"ids": ids}, headers=self.headers
            ).status_code,
            200,
        )
        for gym_id in range(1, 7):
            battle = self.post("battles", {"gym_id": gym_id}).json()
            for _ in range(150):
                if battle["status"] != "active":
                    break
                player = battle["player"][battle["player_active"]]
                opponent = battle["opponent"][battle["opponent_active"]]
                choices = [m for m in player["moves"] if m["pp"] > 0] or [
                    move_data("struggle")
                ]
                best = max(choices, key=lambda m: damage(player, opponent, m))
                response = self.post(
                    f'battles/{battle["id"]}/turns',
                    {
                        "revision": battle["revision"],
                        "kind": "move",
                        "move": best["id"],
                    },
                )
                self.assertEqual(response.status_code, 200)
                battle = response.json()
            self.assertEqual(battle["status"], "won", f"Gym {gym_id}")
        me = self.client.get("/api/v1/adventure/me").json()
        self.assertEqual(me["medals"], list(range(1, 7)))
        self.assertEqual(me["credits"], 1850)
