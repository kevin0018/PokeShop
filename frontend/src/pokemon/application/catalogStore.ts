import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Pokemon } from '../domain/pokemon'
import { httpPokemonRepository } from '../infrastructure/httpPokemonRepository'

export const useCatalogStore = defineStore('catalog', () => {
  const items = ref<Pokemon[]>([])
  const loading = ref(false)
  const loaded = ref(false)
  const error = ref('')
  const types = computed(() => [...new Set(items.value.flatMap((item) => item.types))].sort())
  async function load() {
    if (loading.value || loaded.value) return
    loading.value = true
    error.value = ''
    try {
      items.value = await httpPokemonRepository.list()
      loaded.value = true
    } catch {
      error.value = 'catalogError'
    } finally {
      loading.value = false
    }
  }
  return { items, loading, loaded, error, types, load }
})
