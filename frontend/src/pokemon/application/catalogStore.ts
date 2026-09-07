import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Pokemon } from '../domain/pokemon'
import { httpPokemonRepository, request } from '../infrastructure/httpPokemonRepository'
export const useCatalogStore = defineStore('catalog', () => {
  // Entity cache is independent from the current page; cart references never disappear on navigation.
  const items = ref<Pokemon[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref('')
  const types = computed(() => [...new Set(items.value.flatMap((p) => p.types))].sort())
  function remember(products: Pokemon[]) {
    const entities = new Map(items.value.map((p) => [p.id, p]))
    products.forEach((p) => entities.set(p.id, p))
    items.value = [...entities.values()]
  }
  async function hydrate(ids: number[]) {
    if (!ids.length) return
    const result = await request<{ items: Pokemon[] }>(`/batch?ids=${ids.join(',')}`)
    remember(result.items)
  }
  async function load() {
    if (loading.value || loaded.value) return
    loading.value = true
    error.value = ''
    try {
      remember(await httpPokemonRepository.list())
      loaded.value = true
    } catch {
      error.value = 'catalogError'
    } finally {
      loading.value = false
    }
  }
  return { items, loading, loaded, error, types, load, remember, hydrate }
})
