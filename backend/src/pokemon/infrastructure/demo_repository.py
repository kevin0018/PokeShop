"""Read-only demonstration catalog. Prices and stock are fictional."""

from __future__ import annotations

from src.pokemon.domain.pokemon import Pokemon

_DATA = (
    (1, "Bulbasaur", ("planta", "veneno"), 2490, 12, "El compañero ideal para empezar tu colección. Su bulbo crece junto a él."),
    (4, "Charmander", ("fuego",), 2490, 8, "Una pequeña llama con mucha personalidad. Un clásico de los primeros pasos por Kanto."),
    (7, "Squirtle", ("agua",), 2490, 10, "Pequeño, decidido y siempre preparado para una nueva aventura."),
    (25, "Pikachu", ("electrico",), 2990, 15, "La chispa que le falta a tu equipo. Un compañero reconocible por sus mejillas eléctricas."),
    (35, "Clefairy", ("hada",), 2290, 6, "Una incorporación de aire lunar para la parte más especial de tu colección."),
    (37, "Vulpix", ("fuego",), 2790, 4, "Seis colas y un carácter inconfundible. Un pequeño favorito de tipo fuego."),
    (54, "Psyduck", ("agua",), 1990, 9, "Despistado y entrañable, nunca pasa inadvertido en un equipo."),
    (94, "Gengar", ("fantasma", "veneno"), 3990, 5, "Una sonrisa traviesa para quienes prefieren el lado misterioso de Kanto."),
    (133, "Eevee", ("normal",), 2990, 14, "Muchas posibilidades en un solo compañero. Tu próxima aventura empieza aquí."),
    (143, "Snorlax", ("normal",), 4490, 3, "Un gran compañero que sabe disfrutar de una buena pausa."),
    (149, "Dragonite", ("dragon", "volador"), 4990, 0, "El gran final de una colección de Kanto. Volverá a estar disponible más adelante."),
    (150, "Mewtwo", ("psiquico",), 5990, 2, "Una presencia legendaria para completar tu selección de la primera generación."),
)


class DemoPokemonRepository:
    def __init__(self) -> None:
        self._items = tuple(
            Pokemon(*row, image_url=f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{row[0]}.png")
            for row in _DATA
        )

    def list_all(self) -> tuple[Pokemon, ...]:
        return self._items

    def get(self, pokemon_id: int) -> Pokemon | None:
        return next((item for item in self._items if item.id == pokemon_id), None)
