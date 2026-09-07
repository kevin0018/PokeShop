<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search, ArrowLeft, ArrowRight } from 'lucide-vue-next'
import AppSelect from '@/components/AppSelect.vue'
import PokemonCard from './PokemonCard.vue'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import { typeName } from '@/shared/presentation/format'
import type { Pokemon } from '../domain/pokemon'
const { t } = useI18n()
const route = useRoute(),
  router = useRouter(),
  catalog = useCatalogStore()
const items = ref<Pokemon[]>([]),
  total = ref(0),
  loading = ref(true),
  error = ref(false)
const metadata = ref<{ types: string[]; generations: number[] }>({ types: [], generations: [] })
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
  for (const key of ['q', 'type', 'generation', 'forms', 'sort'])
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
      <AppSelect
        :model-value="value('type')"
        :label="t('filterType')"
        :options="[
          { value: '', label: t('allTypes') },
          ...metadata.types.map((type) => ({ value: type, label: typeName(type) })),
        ]"
        @update:model-value="change('type', $event)"
      />
      <AppSelect
        :model-value="value('generation')"
        :label="t('generationLabel')"
        :options="[
          { value: '', label: t('allGenerations') },
          ...metadata.generations.map((g) => ({
            value: String(g),
            label: t('generationNumber', { n: g }),
          })),
        ]"
        @update:model-value="change('generation', $event)"
      />
      <AppSelect
        :model-value="value('forms')"
        :label="t('forms')"
        :options="[
          { value: '', label: t('allForms') },
          { value: 'default', label: t('defaultForms') },
          { value: 'alternative', label: t('alternativeForms') },
        ]"
        @update:model-value="change('forms', $event)"
      />
      <AppSelect
        :model-value="value('sort') || 'number'"
        :label="t('sort')"
        :options="
          ['number', 'price_asc', 'price_desc', 'name', 'weight_asc', 'weight_desc'].map(
            (v, i) => ({
              value: v,
              label: t(
                ['sortNumber', 'sortLow', 'sortHigh', 'sortName', 'weightLow', 'weightHigh'][i]!,
              ),
            }),
          )
        "
        @update:model-value="change('sort', $event)"
      />
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
      <div v-if="items.length" class="pokemon-grid">
        <PokemonCard v-for="p in items" :key="p.id" :pokemon="p" />
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
