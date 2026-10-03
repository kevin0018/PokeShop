"""Pure turn resolver. Persistence and rewards belong to the application service."""
import copy
import random

from .content import CHART, LOADOUTS, move_data


def fighter(pokemon, level=50):
    base = pokemon["stats"]
    stats = {
        key: (2 * value * level // 100) + (level + 10 if key == "hp" else 5)
        for key, value in base.items()
    }
    return {
        "id": pokemon["id"],
        "name": pokemon["name"],
        "names": pokemon.get("names", {}),
        "types": pokemon["types"],
        "level": level,
        "stats": stats,
        "hp": stats["hp"],
        "max_hp": stats["hp"],
        "front": f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon["id"]}.png',
        "back": f'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{pokemon["id"]}.png',
        "moves": [move_data(key) for key in LOADOUTS[pokemon["id"]]],
    }


def effectiveness(kind, types):
    strong, weak, immune = CHART.get(kind, ([], [], []))
    multiplier = 1
    for target in types:
        multiplier *= (
            0
            if target in immune
            else 2
            if target in strong
            else 0.5
            if target in weak
            else 1
        )
    return multiplier


def damage(attacker, defender, move):
    # Forcejeo is neutral and available only when all PP have been exhausted.
    multiplier = (
        1
        if move["id"] == "struggle"
        else effectiveness(move["type"], defender["types"])
    )
    if not multiplier:
        return 0
    attack = "attack" if move["category"] == "physical" else "special-attack"
    defense = "defense" if move["category"] == "physical" else "special-defense"
    stab = 1.5 if move["type"] in attacker["types"] and move["id"] != "struggle" else 1
    raw = (
        (2 * attacker["level"] // 5 + 2)
        * move["power"]
        * attacker["stats"][attack]
        // max(1, defender["stats"][defense])
        // 50
    ) + 2
    return max(1, int(raw * stab * multiplier))


def available_moves(pokemon):
    moves = [m for m in pokemon["moves"] if m["pp"] > 0]
    return moves or [move_data("struggle")]


def resolve_turn(previous, action, rng=None):
    """Validate the intent and return a new state without modifying the snapshot."""
    rng = rng or random.SystemRandom()
    state = copy.deepcopy(previous)
    if state["status"] != "active":
        raise ValueError("battleFinished")
    if "history" not in state:
        state["history"] = (
            [
                {
                    "turn": max(1, state["turn"] - 1),
                    "events": copy.deepcopy(state["events"]),
                }
            ]
            if state.get("events")
            else []
        )
    state["events"] = []
    events = state["events"]
    if action["kind"] == "surrender":
        state["status"] = "surrendered"
        events.append({"kind": "surrender", "side": "player"})
        state["history"].append(
            {"turn": state["turn"], "events": copy.deepcopy(events)}
        )
        return state
    player = state["player"][state["player_active"]]
    opponent = state["opponent"][state["opponent_active"]]
    if action["kind"] == "switch":
        index = action.get("slot")
        if (
            not isinstance(index, int)
            or index == state["player_active"]
            or index not in range(len(state["player"]))
            or state["player"][index]["hp"] <= 0
        ):
            raise ValueError("invalidSwitch")
        state["player_active"] = index
        player = state["player"][index]
        events.append({"kind": "switch", "side": "player", "pokemon": player["id"]})
        player_move = None
    else:
        player_move = next(
            (m for m in available_moves(player) if m["id"] == action.get("move")), None
        )
        if player_move is None:
            raise ValueError("invalidMove")
    enemy_move = max(
        available_moves(opponent),
        key=lambda m: damage(opponent, player, m) * m["accuracy"],
    )
    order = (
        [("player", player_move), ("opponent", enemy_move)]
        if player_move
        else [("opponent", enemy_move)]
    )
    if player_move:
        player_speed = (player_move["priority"], player["stats"]["speed"], rng.random())
        enemy_speed = (enemy_move["priority"], opponent["stats"]["speed"], rng.random())
        if enemy_speed > player_speed:
            order.reverse()
    for side, move in order:
        attacker, defender = (
            (player, opponent) if side == "player" else (opponent, player)
        )
        if attacker["hp"] <= 0 or defender["hp"] <= 0:
            continue
        if move["id"] != "struggle":
            move["pp"] -= 1
        events.append(
            {
                "kind": "attack",
                "side": side,
                "pokemon": attacker["id"],
                "move": move["id"],
            }
        )
        if rng.randint(1, 100) > move["accuracy"]:
            events.append({"kind": "miss", "side": side})
            continue
        amount = min(defender["hp"], damage(attacker, defender, move))
        defender["hp"] -= amount
        events.append(
            {
                "kind": "damage",
                "side": "opponent" if side == "player" else "player",
                "pokemon": defender["id"],
                "amount": amount,
                "hp": defender["hp"],
                "effectiveness": 1
                if move["id"] == "struggle"
                else effectiveness(move["type"], defender["types"]),
            }
        )
        if move["id"] == "struggle":
            attacker["hp"] = max(0, attacker["hp"] - max(1, attacker["max_hp"] // 4))
            events.append(
                {
                    "kind": "recoil",
                    "side": side,
                    "pokemon": attacker["id"],
                    "hp": attacker["hp"],
                }
            )
    for side in ["player", "opponent"]:
        current = state[side][state[f"{side}_active"]]
        if current["hp"] <= 0:
            events.append({"kind": "faint", "side": side, "pokemon": current["id"]})
            alive = next((i for i, p in enumerate(state[side]) if p["hp"] > 0), None)
            if alive is not None:
                state[f"{side}_active"] = alive
                events.append(
                    {
                        "kind": "switch",
                        "side": side,
                        "pokemon": state[side][alive]["id"],
                    }
                )
    if not any(p["hp"] > 0 for p in state["player"]):
        state["status"] = "lost"
    elif not any(p["hp"] > 0 for p in state["opponent"]):
        state["status"] = "won"
    state["history"].append({"turn": state["turn"], "events": copy.deepcopy(events)})
    state["turn"] += 1
    return state
