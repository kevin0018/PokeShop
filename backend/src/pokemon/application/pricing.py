"""Versioned fictional offer policy; monetary arithmetic never uses binary floats."""
from decimal import ROUND_HALF_UP, Decimal

VERSION = "classic-v1"
REGIONS = [
    "kanto",
    "johto",
    "hoenn",
    "sinnoh",
    "unova",
    "kalos",
    "alola",
    "galar",
    "hisui",
    "paldea",
]
REGION_NAMES = {
    "kanto": ("Kanto", "Kanto"),
    "johto": ("Johto", "Johto"),
    "hoenn": ("Hoenn", "Hoenn"),
    "sinnoh": ("Sinnoh", "Sinnoh"),
    "unova": ("Teselia", "Unova"),
    "kalos": ("Kalos", "Kalos"),
    "alola": ("Alola", "Alola"),
    "galar": ("Galar", "Galar"),
    "hisui": ("Hisui", "Hisui"),
    "paldea": ("Paldea", "Paldea"),
}


def calculate_price(data, base_cents=3000):
    missing = [
        key
        for key in ("weight_kg", "evolution_stage", "generation", "region")
        if data.get(key) is None
    ]
    weight = max(
        Decimal(0), min(Decimal(1000), Decimal(str(data.get("weight_kg") or 0)))
    )
    stage = max(1, int(data.get("evolution_stage") or 1))
    generation = data.get("generation")
    region = data.get("region")
    if generation not in range(1, 10) and "generation" not in missing:
        missing.append("generation")
    if region not in REGIONS and "region" not in missing:
        missing.append("region")
    factors = {
        "weight": 1 + Decimal(".05") * weight,
        "evolution": 1 + Decimal(".10") * (stage - 1),
        "generation": 1 + Decimal(".10") * (9 - generation)
        if generation in range(1, 10)
        else Decimal(1),
        "region": Decimal("1.45") - Decimal(".05") * REGIONS.index(region)
        if region in REGIONS
        else Decimal(1),
    }
    price = Decimal(base_cents)
    for factor in factors.values():
        price *= factor
    cents = int((price / 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 10)
    return {
        "price_cents": cents,
        "base_cents": base_cents,
        "pricing_version": VERSION,
        "pricing_breakdown": {
            "factors": {k: str(v) for k, v in factors.items()},
            "weight_kg": str(weight),
            "evolution_stage": stage,
            "missing": missing,
        },
    }


def region_for(pokemon, species, default):
    for marker, region in [
        ("alola", "alola"),
        ("galar", "galar"),
        ("hisui", "hisui"),
        ("paldea", "paldea"),
    ]:
        if marker in pokemon["name"].split("-"):
            return region
    if species["name"] in {
        "wyrdeer",
        "kleavor",
        "ursaluna",
        "basculegion",
        "sneasler",
        "overqwil",
        "enamorus",
    }:
        return "hisui"
    return default


def evolution_stage(chain, species_id, depth=1):
    if int(chain["species"]["url"].rstrip("/").split("/")[-1]) == species_id:
        return depth
    for child in chain.get("evolves_to", []):
        found = evolution_stage(child, species_id, depth + 1)
        if found is not None:
            return found
    return None
