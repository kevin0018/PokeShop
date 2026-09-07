"""HTTP adapter and dependency composition for the demonstration catalog."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from src.pokemon.application.catalog import Catalog
from src.pokemon.infrastructure.demo_repository import DemoPokemonRepository

router = APIRouter()
_catalog = Catalog(DemoPokemonRepository())


def get_catalog() -> Catalog:
    return _catalog


class PokemonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    types: list[str]
    price_cents: int
    stock: int
    description: str
    image_url: str


class CatalogResponse(BaseModel):
    items: list[PokemonResponse]
    total: int


@router.get("", response_model=CatalogResponse)
def list_pokemon(
    q: str = Query("", max_length=100),
    pokemon_type: str = Query("", alias="type", max_length=30),
    sort: Literal["number", "price_asc", "price_desc", "name"] = "number",
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    catalog: Catalog = Depends(get_catalog),
):
    items, total = catalog.search(q, pokemon_type, sort, limit, offset)
    return {"items": items, "total": total}


@router.get("/{pokemon_id}", response_model=PokemonResponse)
def get_pokemon(pokemon_id: int, catalog: Catalog = Depends(get_catalog)):
    pokemon = catalog.get(pokemon_id)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon no encontrado")
    return pokemon
