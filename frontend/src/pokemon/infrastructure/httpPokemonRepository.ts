import type { Pokemon, PokemonRepository } from '../domain/pokemon'
export const httpPokemonRepository: PokemonRepository = {
  async list() {
    const response = await fetch('/api/v1/pokemon?limit=100', {
      signal: AbortSignal.timeout(10000),
    })
    if (!response.ok) throw new Error('No se pudo cargar el catálogo.')
    const result: { items: Pokemon[]; total: number } = await response.json()
    return result.items
  },
}
