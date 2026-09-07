"""Catalog use cases depend only on the repository port."""

from __future__ import annotations

from src.pokemon.domain.pokemon import Pokemon, PokemonRepository


class Catalog:
    def __init__(self, repository: PokemonRepository) -> None:
        self.repository = repository

    def search(
        self,
        query: str = "",
        pokemon_type: str = "",
        sort: str = "number",
        limit: int = 24,
        offset: int = 0,
    ) -> tuple[list[Pokemon], int]:
        query = query.strip().casefold().lstrip("#")
        items = [
            item for item in self.repository.list_all()
            if (
                not query or query in item.name.casefold()
                or (query.isdecimal() and int(query) == item.id)
            )
            and (not pokemon_type or pokemon_type in item.types)
        ]
        keys = {
            "number": lambda item: item.id,
            "price_asc": lambda item: (item.price_cents, item.id),
            "price_desc": lambda item: (-item.price_cents, item.id),
            "name": lambda item: item.name,
        }
        items.sort(key=keys[sort])
        return items[offset : offset + limit], len(items)

    def get(self, pokemon_id: int) -> Pokemon | None:
        return self.repository.get(pokemon_id)
