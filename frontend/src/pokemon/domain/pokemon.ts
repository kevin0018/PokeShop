// Pokemon domain entities
import { PokemonId, Money } from '../../shared/domain/value-objects';

export interface PokemonType {
  name: string;
  color: string;
}

export interface PokemonStats {
  hp: number;
  attack: number;
  defense: number;
  specialAttack: number;
  specialDefense: number;
  speed: number;
}

export interface PokemonSprites {
  front_default: string;
  front_shiny?: string;
  official_artwork: string;
}

export class Pokemon {
  constructor(
    public readonly id: PokemonId,
    public readonly name: string,
    public readonly height: number,
    public readonly weight: number,
    public readonly types: PokemonType[],
    public readonly stats: PokemonStats,
    public readonly sprites: PokemonSprites,
    public readonly price: Money,
    public readonly description: string,
    public readonly isShiny: boolean = false
  ) {}

  getDisplayName(): string {
    return this.name.charAt(0).toUpperCase() + this.name.slice(1);
  }

  getPrimaryType(): PokemonType {
    return this.types[0];
  }

  getFormattedPrice(): string {
    return this.price.format();
  }

  isMultiType(): boolean {
    return this.types.length > 1;
  }

  getMainImage(): string {
    return this.isShiny && this.sprites.front_shiny 
      ? this.sprites.front_shiny 
      : this.sprites.front_default;
  }

  getOfficialArtwork(): string {
    return this.sprites.official_artwork;
  }

  getTotalStats(): number {
    return Object.values(this.stats).reduce((total, stat) => total + stat, 0);
  }
}
