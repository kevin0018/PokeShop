export interface Pokemon {
  id: number
  name: string
  types: string[]
  price_cents: number
  stock: number
  description: string
  image_url: string
  species_id?: number
  names?: Record<string, string>
  descriptions?: Record<string, string>
  weight_kg?: number
  height_m?: number
  generation?: number
  is_default?: boolean
  form?: string
  form_names?: Record<string, string>
  abilities?: { name: string; names: Record<string, string>; hidden: boolean }[]
  stats?: Record<string, number>
  reason?: string
}
export interface PokemonRepository {
  list(): Promise<Pokemon[]>
}
export type CatalogSort =
  | 'number'
  | 'price_asc'
  | 'price_desc'
  | 'name'
  | 'weight_asc'
  | 'weight_desc'
