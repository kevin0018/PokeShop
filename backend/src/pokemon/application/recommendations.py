"""Deterministic recommendation policy, independent of storage and HTTP."""


def recommend(items, seeds):
    species = {p["species_id"] for p in seeds}
    types = {t for p in seeds for t in p["types"]}
    generations = {p["generation"] for p in seeds}

    def rank(p):
        return (
            not bool(types.intersection(p["types"])),
            p["generation"] not in generations,
            min(abs(p["price_cents"] - s["price_cents"]) for s in seeds),
            p["id"],
        )

    result = []
    for p in sorted(
        (p for p in items if p["stock"] > 0 and p["species_id"] not in species),
        key=rank,
    ):
        if p["species_id"] in species:
            continue
        species.add(p["species_id"])
        result.append(
            dict(
                p,
                reason="sharedType"
                if types.intersection(p["types"])
                else "sameGeneration"
                if p["generation"] in generations
                else "similarPrice",
            )
        )
        if len(result) == 4:
            break
    return result
