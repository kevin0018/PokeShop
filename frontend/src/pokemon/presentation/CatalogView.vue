<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search, ArrowLeft, ArrowRight } from 'lucide-vue-next'
import CatalogFilters from './CatalogFilters.vue'
import PokemonCard from './PokemonCard.vue'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'

import type { Pokemon } from '../domain/pokemon'
const { t } = useI18n()
const route = useRoute(),
  router = useRouter(),
  catalog = useCatalogStore()
const items = ref<Pokemon[]>([]),
  total = ref(0),
  loading = ref(true),
  error = ref(false)
const metadata = ref<{
  types: string[]
  generations: number[]
  regions?: { id: string; names: Record<string, string> }[]
}>({ types: [], generations: [] })
const page = computed(() => Math.max(1, Number(route.query.page) || 1))
const pages = computed(() => Math.max(1, Math.ceil(total.value / 24)))
const value = (key: string) => String(route.query[key] || '')
function change(key: string, val: string) {
  void router.replace({ query: { ...route.query, [key]: val || undefined, page: undefined } })
}
async function load() {
  controller?.abort()
  controller = new AbortController()
  const current = controller
  loading.value = true
  error.value = false
  const params = new URLSearchParams({ limit: '24', offset: String((page.value - 1) * 24) })
  for (const key of ['q', 'type', 'region', 'generation', 'forms', 'sort'])
    if (value(key)) params.set(key, value(key))
  try {
    const result = await request<{ items: Pokemon[]; total: number }>(`?${params}`, current.signal)
    if (current.signal.aborted) return
    items.value = result.items
    total.value = result.total
    catalog.remember(result.items)
    if (page.value > pages.value)
      await router.replace({ query: { ...route.query, page: String(pages.value) } })
  } catch {
    if (!current.signal.aborted) error.value = true
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}
let controller: AbortController | undefined
watch(() => route.query, load, { immediate: true })
import { onUnmounted } from 'vue'
onUnmounted(() => controller?.abort())
request<typeof metadata.value>('/metadata')
  .then((result) => (metadata.value = result))
  .catch(() => {})
</script>
<template>
  <section class="catalog-section">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('allGenerations') }}</p>
        <h1>{{ t('catalog') }}</h1>
      </div>
      <span>{{ t('catalogIntro') }}</span>
    </div>
    <div class="catalog-tools">
      <label class="search-field"
        ><Search :size="18" /><span class="sr-only">{{ t('search') }}</span
        ><input
          :value="value('q')"
          type="search"
          :placeholder="t('searchPlaceholder')"
          maxlength="100"
          @input="change('q', ($event.target as HTMLInputElement).value)"
      /></label>
      <CatalogFilters :metadata="metadata" />
    </div>
    <p class="bento-caption">{{ t('heightBento') }}</p>
    <p v-if="loading" role="status" class="state-box">{{ t('loadingCatalog') }}</p>
    <div v-else-if="error" role="alert" class="state-box">
      <p>{{ t('catalogError') }}</p>
      <button class="button primary" @click="load">{{ t('retry') }}</button>
    </div>
    <template v-else
      ><div class="results-bar">
        <p role="status">{{ t('found', total) }}</p>
        <button class="text-button" @click="router.replace({ query: {} })">
          {{ t('clearFilters') }}
        </button>
      </div>
      <div v-if="items.length" class="catalog-bento">
        <PokemonCard
          v-for="p in items"
          :key="p.id"
          :pokemon="p"
          bento
          :class="(p.height_m ?? 0) > 2 ? 'tall' : (p.height_m ?? 0) > 1 ? 'medium' : 'small'"
        />
      </div>
      <div v-else class="state-box">{{ t('noMatches') }}</div>
      <nav class="pagination" :aria-label="t('pagination')">
        <button
          class="button secondary"
          :disabled="page <= 1"
          @click="router.push({ query: { ...route.query, page: String(page - 1) } })"
        >
          <ArrowLeft :size="16" />{{ t('previous') }}</button
        ><span>{{ t('pageOf', { page, pages }) }}</span
        ><button
          class="button secondary"
          :disabled="page >= pages"
          @click="router.push({ query: { ...route.query, page: String(page + 1) } })"
        >
          {{ t('next') }}<ArrowRight :size="16" />
        </button>
      </nav>
    </template>
  </section>
</template>

<style>
.catalog-section .catalog-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
}
.catalog-section .search-field {
  flex: 1 1 260px;
}
.catalog-bento {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 24px;
  grid-auto-flow: row;
  grid-auto-rows: 390px;
}
.catalog-bento .pokemon-card {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.catalog-bento .medium,
.catalog-bento .tall {
  grid-column: span 3;
}
.catalog-bento .tall {
  grid-row: span 2;
}
.catalog-bento .card-art {
  flex: 1;
  min-height: 0;
  height: auto;
}
.catalog-bento .card-art img {
  width: 80%;
  padding: 18px;
  height: 100%;
  max-height: 100%;
  object-fit: contain;
}
.catalog-bento .card-body {
  flex: none;
}
.card-measures {
  display: flex;
  gap: 16px;
  color: var(--muted-strong);
  font-size: 0.8rem;
  margin: 10px 0;
}
@media (max-width: 900px) {
  .catalog-bento {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .catalog-bento .pokemon-card {
    grid-column: span 1;
    grid-row: span 1;
  }
}
@media (max-width: 540px) {
  .catalog-bento {
    grid-template-columns: minmax(0, 1fr);
    grid-auto-rows: 410px;
    gap: 18px;
  }
}
</style>
