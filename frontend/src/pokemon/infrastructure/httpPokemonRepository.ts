import type { Pokemon } from '../domain/pokemon'
export async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api/v1/pokemon${path}`, {
    signal: signal
      ? AbortSignal.any([signal, AbortSignal.timeout(15000)])
      : AbortSignal.timeout(15000),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}
export const httpPokemonRepository = {
  async list(): Promise<Pokemon[]> {
    return (await request<{ items: Pokemon[] }>('?limit=24')).items
  },
}
