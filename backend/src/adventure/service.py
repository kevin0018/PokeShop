"""Transactional application operations. All writes lock the trainer first."""
import asyncio
import hmac
import json
import secrets
import uuid

from fastapi import HTTPException
from sqlalchemy import text

from .battle import fighter, resolve_turn
from .content import GYMS, SHOP_IDS, credit_price
from .security import (
    SESSION_SECONDS,
    csrf_token,
    digest,
    hash_password,
    verify_password,
)


def fail(code, status=409):
    raise HTTPException(status, code)


async def session(conn, token, lock=False):
    if not token:
        fail("signInRequired", 401)
    trainer = (
        (
            await conn.execute(
                text(
                    """
        SELECT t.* FROM trainers t JOIN trainer_sessions s ON s.trainer_id=t.id
        WHERE s.token_hash=:token AND s.expires_at > now()
    """
                    + (" FOR UPDATE OF t" if lock else "")
                ),
                {"token": digest(token)},
            )
        )
        .mappings()
        .first()
    )
    if not trainer:
        fail("signInRequired", 401)
    return dict(trainer)


async def throttle(engine, key):
    # Persist across workers/restarts, including failed requests.
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "DELETE FROM auth_attempts WHERE window_start < now() - interval '15 minutes'"
            )
        )
        count = await conn.scalar(
            text(
                """
            INSERT INTO auth_attempts(key,attempts) VALUES (:key,1)
            ON CONFLICT(key) DO UPDATE SET attempts=auth_attempts.attempts+1
            RETURNING attempts
        """
            ),
            {"key": digest(key)},
        )
    if count > 20:
        fail("tooManyAttempts", 429)


async def new_session(conn, trainer_id):
    token = secrets.token_urlsafe(32)
    await conn.execute(text("DELETE FROM trainer_sessions WHERE expires_at <= now()"))
    await conn.execute(
        text(
            """
        INSERT INTO trainer_sessions(token_hash,trainer_id,expires_at)
        VALUES (:token,:id,now() + :seconds * interval '1 second')
    """
        ),
        {"token": digest(token), "id": trainer_id, "seconds": SESSION_SECONDS},
    )
    return token


async def register(engine, username, password, invitation):
    encoded = await asyncio.to_thread(hash_password, password)
    async with engine.begin() as conn:
        valid = (
            await conn.execute(
                text(
                    """
            SELECT code_hash FROM invitations WHERE code_hash=:code AND expires_at > now()
            AND used_by IS NULL AND NOT revoked FOR UPDATE
        """
                ),
                {"code": digest(invitation)},
            )
        ).first()
        if not valid:
            fail("invalidInvitation", 403)
        trainer_id = uuid.uuid4()
        created = await conn.scalar(
            text(
                """
            INSERT INTO trainers(id,username,password_hash) VALUES (:id,:username,:password)
            ON CONFLICT(username) DO NOTHING RETURNING id
        """
            ),
            {"id": trainer_id, "username": username, "password": encoded},
        )
        if not created:
            fail("usernameTaken")
        await conn.execute(
            text("UPDATE invitations SET used_by=:id WHERE code_hash=:code"),
            {"id": trainer_id, "code": digest(invitation)},
        )
        return await new_session(conn, trainer_id)


async def login(engine, username, password):
    async with engine.connect() as conn:
        trainer = (
            (
                await conn.execute(
                    text(
                        "SELECT id,password_hash FROM trainers WHERE username=:username"
                    ),
                    {"username": username},
                )
            )
            .mappings()
            .first()
        )
    # A dummy hash follows the same expensive path for unknown usernames.
    encoded = (
        trainer["password_hash"] if trainer else "scrypt$" + "00" * 16 + "$" + "00" * 64
    )
    valid = await asyncio.to_thread(verify_password, password, encoded)
    if not valid or not trainer:
        fail("invalidCredentials", 401)
    async with engine.begin() as conn:
        return await new_session(conn, trainer["id"])


async def pokemon_data(conn, ids):
    if not ids:
        return []
    rows = (
        await conn.execute(
            text("SELECT id,data FROM pokemon WHERE id=ANY(:ids)"), {"ids": ids}
        )
    ).mappings()
    indexed = {row["id"]: dict(row["data"], id=row["id"]) for row in rows}
    return [indexed[i] for i in ids if i in indexed and indexed[i].get("stats")]


def shop_item(pokemon):
    return {
        "id": pokemon["id"],
        "name": pokemon["name"],
        "names": pokemon.get("names", {}),
        "types": pokemon["types"],
        "image_url": pokemon.get("image_url", ""),
        "price": credit_price(pokemon),
        "stats": pokemon["stats"],
    }


async def profile(conn, trainer, token):
    ids = list(
        (
            await conn.execute(
                text(
                    "SELECT pokemon_id FROM trainer_collection WHERE trainer_id=:id ORDER BY purchased_at,pokemon_id"
                ),
                {"id": trainer["id"]},
            )
        ).scalars()
    )
    medals = list(
        (
            await conn.execute(
                text(
                    "SELECT gym_id FROM gym_medals WHERE trainer_id=:id ORDER BY gym_id"
                ),
                {"id": trainer["id"]},
            )
        ).scalars()
    )
    battle = (
        await conn.execute(
            text(
                "SELECT id FROM trainer_battles WHERE trainer_id=:id ORDER BY created_at DESC LIMIT 1"
            ),
            {"id": trainer["id"]},
        )
    ).scalar()
    return {
        "username": trainer["username"],
        "credits": trainer["credits"],
        "team": trainer["team"],
        "collection": [shop_item(p) for p in await pokemon_data(conn, ids)],
        "medals": medals,
        "csrf_token": csrf_token(token),
        "battle_id": str(battle) if battle else None,
    }


def require_csrf(token, header):
    if not header or not hmac.compare_digest(csrf_token(token), header):
        fail("invalidCsrf", 403)


async def require_idle(conn, trainer_id):
    if await conn.scalar(
        text("SELECT 1 FROM trainer_battles WHERE trainer_id=:id AND status='active'"),
        {"id": trainer_id},
    ):
        fail("battleInProgress")


async def buy(conn, trainer, pokemon_id):
    if pokemon_id not in SHOP_IDS:
        fail("pokemonUnavailable", 404)
    data = await pokemon_data(conn, [pokemon_id])
    if not data:
        fail("pokemonUnavailable", 404)
    price = credit_price(data[0])
    if await conn.scalar(
        text(
            "SELECT 1 FROM trainer_collection WHERE trainer_id=:id AND pokemon_id=:pokemon"
        ),
        {"id": trainer["id"], "pokemon": pokemon_id},
    ):
        fail("alreadyOwned")
    if trainer["credits"] < price:
        fail("notEnoughCredits")
    await conn.execute(
        text(
            "INSERT INTO trainer_collection(trainer_id,pokemon_id,price) VALUES (:id,:pokemon,:price)"
        ),
        {"id": trainer["id"], "pokemon": pokemon_id, "price": price},
    )
    await conn.execute(
        text("UPDATE trainers SET credits=credits-:price WHERE id=:id"),
        {"price": price, "id": trainer["id"]},
    )


async def save_team(conn, trainer, ids):
    await require_idle(conn, trainer["id"])
    owned = set(
        (
            await conn.execute(
                text("SELECT pokemon_id FROM trainer_collection WHERE trainer_id=:id"),
                {"id": trainer["id"]},
            )
        ).scalars()
    )
    if len(ids) > 6 or len(ids) != len(set(ids)) or not set(ids) <= owned:
        fail("invalidTeam", 422)
    await conn.execute(
        text("UPDATE trainers SET team=CAST(:team AS jsonb) WHERE id=:id"),
        {"team": json.dumps(ids), "id": trainer["id"]},
    )


def battle_response(row):
    return {
        "id": str(row["id"]),
        "gym_id": row["gym_id"],
        "revision": row["revision"],
        **row["state"],
    }


async def start_battle(conn, trainer, gym_id):
    await require_idle(conn, trainer["id"])
    if gym_id not in range(1, 7):
        fail("gymUnavailable", 404)
    medals = set(
        (
            await conn.execute(
                text("SELECT gym_id FROM gym_medals WHERE trainer_id=:id"),
                {"id": trainer["id"]},
            )
        ).scalars()
    )
    if not set(range(1, gym_id)) <= medals:
        fail("gymLocked", 403)
    gym = GYMS[gym_id - 1]
    players = await pokemon_data(conn, trainer["team"])
    opponents = await pokemon_data(conn, gym["pokemon"])
    if not players:
        fail("emptyTeam", 422)
    if len(players) != len(trainer["team"]) or len(opponents) != len(gym["pokemon"]):
        fail("catalogNotReady", 503)
    state = {
        "status": "active",
        "turn": 1,
        "player": [fighter(p) for p in players],
        "opponent": [fighter(p, gym["level"]) for p in opponents],
        "player_active": 0,
        "opponent_active": 0,
        "events": [],
        "reward": 0,
    }
    battle_id = uuid.uuid4()
    await conn.execute(
        text(
            "INSERT INTO trainer_battles(id,trainer_id,gym_id,status,state) VALUES (:id,:trainer,:gym,'active',CAST(:state AS jsonb))"
        ),
        {
            "id": battle_id,
            "trainer": trainer["id"],
            "gym": gym_id,
            "state": json.dumps(state),
        },
    )
    return battle_response(
        {"id": battle_id, "gym_id": gym_id, "revision": 0, "state": state}
    )


async def battle_row(conn, trainer_id, battle_id, lock=False):
    row = (
        (
            await conn.execute(
                text(
                    "SELECT * FROM trainer_battles WHERE id=:battle AND trainer_id=:id"
                    + (" FOR UPDATE" if lock else "")
                ),
                {"battle": battle_id, "id": trainer_id},
            )
        )
        .mappings()
        .first()
    )
    if not row:
        fail("battleNotFound", 404)
    return row


async def turn(conn, trainer, battle_id, revision, action):
    row = await battle_row(conn, trainer["id"], battle_id, lock=True)
    if row["revision"] != revision:
        fail("staleTurn")
    try:
        state = resolve_turn(row["state"], action)
    except ValueError as error:
        fail(str(error), 422)
    if state["status"] == "won":
        reward = GYMS[row["gym_id"] - 1]["reward"]
        awarded = await conn.scalar(
            text(
                """
            INSERT INTO gym_medals(trainer_id,gym_id,reward) VALUES (:id,:gym,:reward)
            ON CONFLICT DO NOTHING RETURNING reward
        """
            ),
            {"id": trainer["id"], "gym": row["gym_id"], "reward": reward},
        )
        if awarded:
            state["reward"] = reward
            await conn.execute(
                text("UPDATE trainers SET credits=credits+:reward WHERE id=:id"),
                {"id": trainer["id"], "reward": reward},
            )
    await conn.execute(
        text(
            "UPDATE trainer_battles SET state=CAST(:state AS jsonb),status=:status,revision=revision+1 WHERE id=:id"
        ),
        {"state": json.dumps(state), "status": state["status"], "id": battle_id},
    )
    return battle_response(
        {
            "id": battle_id,
            "gym_id": row["gym_id"],
            "revision": revision + 1,
            "state": state,
        }
    )
