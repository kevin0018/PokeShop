// Pokemon repository interface (port)
import { Pokemon } from './pokemon';
import { PokemonId } from '../../shared/domain/value-objects';

export interface PokemonFilters {
  type?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
  generation?: number;
}

export interface PaginationOptions {
  page: number;
  limit: number;
}

export interface PokemonSearchResult {
  pokemons: Pokemon[];
  total: number;
  currentPage: number;
  totalPages: number;
}

export interface PokemonRepository {
  findById(id: PokemonId): Promise<Pokemon | null>;
  findByName(name: string): Promise<Pokemon | null>;
  search(filters: PokemonFilters, pagination: PaginationOptions): Promise<PokemonSearchResult>;
  findFeatured(): Promise<Pokemon[]>;
  findByType(type: string): Promise<Pokemon[]>;
  findRandomSelection(count: number): Promise<Pokemon[]>;
}
