"""HTTP adapter for the persistent catalog."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from src.pokemon.infrastructure.postgres_repository import PostgresCatalog

from .schemas import CatalogResponse, PokemonItems, PokemonResponse

router = APIRouter()


def get_catalog():
    return PostgresCatalog()


@router.get("", response_model=CatalogResponse)
async def list_pokemon(
    q: str = Query("", max_length=100),
    pokemon_type: str = Query("", alias="type", max_length=30),
    sort: Literal[
        "number", "price_asc", "price_desc", "name", "weight_asc", "weight_desc"
    ] = "number",
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    generation: int = Query(0, ge=0, le=20),
    forms: Literal["all", "default", "alternative"] = "all",
    catalog=Depends(get_catalog),
):
    items, total = await catalog.search(
        q, pokemon_type, sort, limit, offset, generation, forms
    )
    return {"items": items, "total": total}


@router.get("/metadata")
async def metadata(catalog=Depends(get_catalog)):
    return await catalog.metadata()


@router.get("/featured", response_model=PokemonItems)
async def featured(catalog=Depends(get_catalog)):
    return {"items": await catalog.featured()}


def parse_ids(ids):
    values = ids.split(",") if ids else []
    if len(values) > 100 or any(not v.isdigit() or int(v) < 1 for v in values):
        raise HTTPException(422, "Expected up to 100 positive IDs")
    return list(dict.fromkeys(map(int, values)))


@router.get("/batch", response_model=CatalogResponse)
async def batch(ids: str = Query("", max_length=1200), catalog=Depends(get_catalog)):
    items, total = await catalog.search(ids=parse_ids(ids), limit=100)
    return {"items": items, "total": total}


@router.get("/recommendations", response_model=PokemonItems)
async def recommendations(
    ids: str = Query("", max_length=1200), catalog=Depends(get_catalog)
):
    return {"items": await catalog.recommendations(parse_ids(ids))}


@router.get("/{pokemon_id}", response_model=PokemonResponse)
async def get_pokemon(pokemon_id: int, catalog=Depends(get_catalog)):
    pokemon = await catalog.get(pokemon_id)
    if pokemon is None:
        raise HTTPException(404, "Pokémon no encontrado")
    return pokemon
