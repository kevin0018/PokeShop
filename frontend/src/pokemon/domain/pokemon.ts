export interface Pokemon {
  id: number
  name: string
  types: string[]
  price_cents: number
  stock: number
  description: string
  image_url: string
}
export interface PokemonRepository {
  list(): Promise<Pokemon[]>
}
export type CatalogSort = 'number' | 'price_asc' | 'price_desc' | 'name'
