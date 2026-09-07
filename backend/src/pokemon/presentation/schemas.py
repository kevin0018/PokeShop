"""Public catalog response contract. Localization is carried with each entity."""
from pydantic import BaseModel, ConfigDict, Field


class AbilityResponse(BaseModel):
    name: str
    names: dict[str, str]
    hidden: bool


class PokemonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    types: list[str]
    price_cents: int
    stock: int
    description: str
    image_url: str
    species_id: int | None = None
    names: dict[str, str] = Field(default_factory=dict)
    descriptions: dict[str, str] = Field(default_factory=dict)
    weight_kg: float | None = None
    height_m: float | None = None
    generation: int | None = None
    is_default: bool = True
    form: str = ""
    form_names: dict[str, str] = Field(default_factory=dict)
    abilities: list[AbilityResponse] = Field(default_factory=list)
    stats: dict[str, int] = Field(default_factory=dict)
    reason: str | None = None


class PokemonItems(BaseModel):
    items: list[PokemonResponse]


class CatalogResponse(PokemonItems):
    total: int
