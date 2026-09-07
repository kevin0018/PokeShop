"""Explicit resumable sync: python -m src.pokemon.infrastructure.sync [--refresh]."""
import argparse
import asyncio
import json
from collections import defaultdict

import httpx
from sqlalchemy import text

from ..application.pricing import (
    REGION_NAMES,
    calculate_price,
    evolution_stage,
    region_for,
)
from .postgres_repository import engine

TYPE_NAMES = dict(
    zip(
        "normal fighting flying poison ground rock bug ghost steel fire water grass electric psychic ice dragon dark fairy".split(),
        "normal lucha volador veneno tierra roca bicho fantasma acero fuego agua planta electrico psiquico hielo dragon siniestro hada".split(),
        strict=True,
    )
)


def names(entries):
    return {
        e["language"]["name"]: e["name"]
        for e in entries
        if e["language"]["name"] in ("es", "en")
    }


def normalize(p, species, form, abilities):
    localized = names(species["names"])
    form_names = names(form.get("form_names", []))
    suffix = (
        p["name"].removeprefix(species["name"]).strip("-")
        if not p["is_default"]
        else ""
    )
    display = {
        lang: localized.get(lang, species["name"].title())
        + (
            (" · " + form_names.get(lang, suffix.replace("-", " ").title()))
            if suffix
            else ""
        )
        for lang in ("es", "en")
    }
    descriptions = {}
    for entry in species.get("flavor_text_entries", []):
        lang = entry["language"]["name"]
        if lang in ("es", "en"):
            descriptions[lang] = " ".join(entry["flavor_text"].split())
    return {
        "id": p["id"],
        "species_id": species["id"],
        "name": display["en"],
        "names": display,
        "types": [
            TYPE_NAMES.get(t["type"]["name"], t["type"]["name"]) for t in p["types"]
        ],
        "description": descriptions.get("es", ""),
        "descriptions": descriptions,
        "weight_kg": p["weight"] / 10,
        "height_m": p["height"] / 10,
        "generation": int(species["generation"]["url"].rstrip("/").split("/")[-1]),
        "is_default": p["is_default"],
        "form": suffix,
        "form_names": form_names,
        "abilities": [
            {
                "name": a["name"],
                "names": names(a["names"]),
                "hidden": entry["is_hidden"],
            }
            for a, entry in zip(abilities, p["abilities"], strict=True)
        ],
        "stats": {s["stat"]["name"]: s["base_stat"] for s in p["stats"]},
        "image_url": p["sprites"]["other"]["official-artwork"]["front_default"]
        or p["sprites"]["front_default"]
        or "",
    }


class Importer:
    def __init__(self, client, refresh=False):
        self.client, self.refresh = client, refresh
        self.locks = defaultdict(asyncio.Lock)
        self.semaphore = asyncio.Semaphore(4)
        self.seen = set()

    async def fetch(self, url):
        async with self.locks[url]:
            async with engine.connect() as conn:
                cached = await conn.scalar(
                    text("SELECT data FROM api_cache WHERE url=:url"), {"url": url}
                )
            if cached is not None and (not self.refresh or url in self.seen):
                return cached
            for attempt in range(3):
                try:
                    async with self.semaphore:
                        response = await self.client.get(url)
                        response.raise_for_status()
                    data = response.json()
                    async with engine.begin() as conn:
                        await conn.execute(
                            text(
                                "INSERT INTO api_cache(url,data) VALUES (:url,CAST(:data AS jsonb)) ON CONFLICT(url) DO UPDATE SET data=excluded.data,fetched_at=now()"
                            ),
                            {"url": url, "data": json.dumps(data)},
                        )
                    self.seen.add(url)
                    return data
                except (httpx.HTTPError, ValueError):
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2**attempt)

    async def entry(self, url):
        p = await self.fetch(url)
        species = await self.fetch(p["species"]["url"])
        form = await self.fetch(p["forms"][0]["url"]) if p["forms"] else {}
        abilities = [await self.fetch(a["ability"]["url"]) for a in p["abilities"]]
        data = normalize(p, species, form, abilities)
        generation = await self.fetch(species["generation"]["url"])
        region_resource = await self.fetch(generation["main_region"]["url"])
        chain = (
            await self.fetch(species["evolution_chain"]["url"])
            if species.get("evolution_chain")
            else None
        )
        region = region_for(p, species, region_resource["name"])
        localized_region = (
            names(region_resource["names"])
            if region == region_resource["name"]
            else dict(zip(("es", "en"), REGION_NAMES[region], strict=True))
        )
        data.update(
            region=region,
            region_names=localized_region,
            evolution_stage=evolution_stage(chain["chain"], species["id"])
            if chain
            else None,
        )
        offer = calculate_price(data)
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "INSERT INTO pokemon(id,data) VALUES (:id,CAST(:data AS jsonb)) ON CONFLICT(id) DO UPDATE SET data=excluded.data"
                ),
                {"id": p["id"], "data": json.dumps(data)},
            )
            await conn.execute(
                text(
                    "INSERT INTO offers(pokemon_id,price_cents,stock,base_cents,pricing_version,pricing_breakdown) VALUES (:id,:price,10,:base,:version,CAST(:breakdown AS jsonb)) ON CONFLICT(pokemon_id) DO NOTHING"
                ),
                {
                    "id": p["id"],
                    "price": offer["price_cents"],
                    "base": offer["base_cents"],
                    "version": offer["pricing_version"],
                    "breakdown": json.dumps(offer["pricing_breakdown"]),
                },
            )


async def main(refresh=False):
    failures, completed = [], 0
    async with httpx.AsyncClient(
        timeout=30, limits=httpx.Limits(max_connections=4)
    ) as client:
        importer = Importer(client, refresh)
        url = "https://pokeapi.co/api/v2/pokemon?limit=100"
        while url:
            page = await importer.fetch(url)
            for start in range(0, len(page["results"]), 4):
                batch = page["results"][start : start + 4]
                outcomes = await asyncio.gather(
                    *(importer.entry(e["url"]) for e in batch), return_exceptions=True
                )
                for entry, outcome in zip(batch, outcomes, strict=True):
                    if isinstance(outcome, BaseException):
                        failures.append(entry["name"])
                        print(f"FAILED {entry['name']}: {outcome}", flush=True)
                    else:
                        completed += 1
            print(
                f'Imported {completed}/{page["count"]}; failures {len(failures)}',
                flush=True,
            )
            url = page["next"]
    await engine.dispose()
    if failures:
        raise SystemExit(f"Rerun to recover: {failures}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Refresh cached upstream responses; preserve offers",
    )
    asyncio.run(main(parser.parse_args().refresh))
