<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import type { Pokemon } from '../domain/pokemon'
import PokemonCard from './PokemonCard.vue'
const props = defineProps<{ ids: number[] }>()
const { t } = useI18n()
const catalog = useCatalogStore()
const items = ref<Pokemon[]>([]),
  error = ref(false),
  loading = ref(false)
let controller: AbortController | undefined
async function load() {
  controller?.abort()
  controller = new AbortController()
  const current = controller
  error.value = false
  loading.value = true
  try {
    const result = await request<{ items: Pokemon[] }>(
      '/recommendations?ids=' + props.ids.join(','),
      current.signal,
    )
    if (current.signal.aborted) return
    items.value = result.items
    catalog.remember(result.items)
  } catch {
    if (!current.signal.aborted) error.value = true
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}
watch(() => props.ids.join(','), load, { immediate: true })
onUnmounted(() => controller?.abort())
</script>
<template>
  <section class="recommendations">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('featured') }}</p>
        <h2>{{ t('recommendations') }}</h2>
      </div>
    </div>
    <p v-if="ids.length">{{ t('recommendationsIntro') }}</p>
    <p v-if="loading" role="status">{{ t('loadingCatalog') }}</p>
    <div v-else-if="error" role="alert">
      <p>{{ t('recommendationsError') }}</p>
      <button class="button secondary" @click="load">{{ t('retry') }}</button>
    </div>
    <div v-else class="pokemon-grid">
      <div v-for="p in items" :key="p.id">
        <span class="recommendation-reason">{{ t(p.reason || 'featured') }}</span
        ><PokemonCard :pokemon="p" />
      </div>
    </div>
  </section>
</template>
