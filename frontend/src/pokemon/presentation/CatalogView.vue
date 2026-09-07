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
const blocks = computed(() =>
  Array.from({ length: Math.ceil(items.value.length / 6) }, (_, i) =>
    items.value.slice(i * 6, i * 6 + 6),
  ),
)
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
        <div
          v-for="(block, index) in blocks"
          :key="index"
          class="bento-block"
          :data-count="block.length"
        >
          <PokemonCard v-for="p in block" :key="p.id" :pokemon="p" bento />
        </div>
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
  gap: 16px;
}
.bento-block {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 16px;
  grid-auto-rows: 200px;
}
.bento-block > .pokemon-card {
  grid-column: span 2;
}
.bento-block[data-count='6'] > .pokemon-card:first-child {
  grid-column: span 3;
  grid-row: span 2;
}
.bento-block[data-count='6'] > .pokemon-card:nth-child(2),
.bento-block[data-count='6'] > .pokemon-card:nth-child(3) {
  grid-column: span 3;
}
.bento-block[data-count='1'] > .pokemon-card {
  grid-column: span 6;
}
.bento-block[data-count='2'] > .pokemon-card,
.bento-block[data-count='4'] > .pokemon-card,
.bento-block[data-count='5'] > .pokemon-card:nth-child(-n + 2) {
  grid-column: span 3;
}
@media (min-width: 901px) {
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-body,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-body,
  .bento-block[data-count='1'] .card-body {
    width: 46%;
    top: 50%;
    bottom: auto;
    transform: translateY(-50%);
  }
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-art img,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-art img,
  .bento-block[data-count='1'] .card-art img {
    width: 54%;
    height: 95%;
    left: auto;
    right: 0;
    top: 2%;
  }
  .bento-block[data-count='6'] > .pokemon-card:first-child .card-art img {
    height: 76%;
    width: 88%;
    left: 6%;
    top: 0;
  }
  .bento-block[data-count='6'] > .pokemon-card:first-child h3 {
    font-size: 1.6rem;
  }
  .bento-block[data-count='6'] > .pokemon-card:first-child .card-body {
    padding: 24px;
  }
}
@media (min-width: 541px) and (max-width: 900px) {
  .bento-block {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-auto-rows: 250px;
  }
  .bento-block > .pokemon-card:nth-child(n) {
    grid-column: span 1;
    grid-row: span 1;
  }
  .bento-block[data-count='6'] > .pokemon-card:first-child,
  .bento-block[data-count='6'] > .pokemon-card:last-child,
  .bento-block[data-count='1'] > .pokemon-card,
  .bento-block[data-count='3'] > .pokemon-card:last-child,
  .bento-block[data-count='5'] > .pokemon-card:last-child {
    grid-column: span 2;
  }
}
@media (max-width: 540px) {
  .bento-block {
    grid-template-columns: minmax(0, 1fr);
    grid-auto-rows: 260px;
  }
  .bento-block > .pokemon-card:nth-child(n) {
    grid-column: span 1;
    grid-row: span 1;
  }
}
</style>
