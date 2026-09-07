"""Catalog entities and the repository port, independent of HTTP and storage."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Pokemon:
    id: int
    name: str
    types: tuple[str, ...]
    price_cents: int
    stock: int
    description: str
    image_url: str


class PokemonRepository(Protocol):
    def list_all(self) -> tuple[Pokemon, ...]: ...

    def get(self, pokemon_id: int) -> Pokemon | None: ...
