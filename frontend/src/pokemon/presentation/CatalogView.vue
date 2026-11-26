<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Search,
  ArrowLeft,
  ArrowRight,
  Coins,
  ShoppingBag,
  UsersRound,
  BookOpen,
  Zap,
  Flame,
  Droplets,
  Leaf,
  Ghost,
} from 'lucide-vue-next'
import CatalogFilters from './CatalogFilters.vue'
import PokemonCard from './PokemonCard.vue'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import { useAdventureStore } from '@/adventure/store'
import { useCartStore } from '@/cart/application/cartStore'
import { typeName } from '@/shared/presentation/format'

import type { Pokemon } from '../domain/pokemon'
const shelves = [
  { type: 'planta', icon: Leaf },
  { type: 'fuego', icon: Flame },
  { type: 'agua', icon: Droplets },
  { type: 'electrico', icon: Zap },
  { type: 'fantasma', icon: Ghost },
]
const { t } = useI18n()
const game = useAdventureStore()
const cart = useCartStore()
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
const blockSize = 6
const blocks = computed(() =>
  Array.from({ length: Math.ceil(items.value.length / blockSize) }, (_, index) =>
    items.value.slice(index * blockSize, (index + 1) * blockSize),
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
  if (game.trainer) {
    params.set('currency', 'credits')
    if (value('playable') !== 'false') params.set('playable', 'true')
  }
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
watch([() => route.query, () => Boolean(game.trainer)], load, { immediate: true })
import { onUnmounted } from 'vue'
onUnmounted(() => controller?.abort())
request<typeof metadata.value>('/metadata')
  .then((result) => (metadata.value = result))
  .catch(() => {})
</script>
<template>
  <section class="catalog-section shop-scene">
    <header class="shop-front">
      <div class="section-heading shop-heading">
        <div>
          <p class="eyebrow"><BookOpen :size="16" />PokéShop</p>
          <h1>{{ t('catalog') }}</h1>
          <p class="shop-intro">
            {{ game.trainer ? t('adventure.catalogHelp') : t('catalogIntro') }}
          </p>
        </div>
      </div>
      <div class="album-cards" aria-hidden="true">
        <div v-for="id in [4, 7, 1]" :key="id" class="album-print">
          <span>#{{ String(id).padStart(3, '0') }}</span>
          <img :src="`/studio/${id}.webp`" alt="" width="475" height="475" />
        </div>
      </div>
      <div class="shop-checkout-bar">
        <div v-if="game.trainer" class="catalog-trainer">
          <Coins :size="22" aria-hidden="true" />
          <div>
            <small>{{ t('shopBalance') }}</small
            ><strong>{{ t('adventure.credits', { amount: game.trainer.credits }) }}</strong>
          </div>
        </div>
        <div class="shop-links">
          <RouterLink v-if="game.trainer" to="/aventura"
            ><UsersRound :size="17" aria-hidden="true" />{{ t('adventure.teamTab') }}</RouterLink
          >
          <RouterLink to="/carrito" class="shop-cart"
            ><ShoppingBag :size="18" aria-hidden="true" />{{ t('cart')
            }}<span>{{ cart.count }}</span></RouterLink
          >
        </div>
      </div>
    </header>
    <div v-if="game.trainer" class="shop-playable">
      <label
        ><input
          type="checkbox"
          :checked="value('playable') !== 'false'"
          @change="change('playable', ($event.target as HTMLInputElement).checked ? '' : 'false')"
        />
        {{ t('adventure.onlyPlayable') }}</label
      >
    </div>
    <div v-if="game.trainer && game.error" class="state-box" role="alert">
      {{ t(`adventure.errors.${game.error}`) }}
    </div>
    <div class="type-shelves" role="group" :aria-label="t('studio.browseType')">
      <button
        v-for="shelf in shelves"
        :key="shelf.type"
        class="type-shelf pokemon-palette"
        :data-type="shelf.type"
        :aria-pressed="value('type') === shelf.type"
        @click="change('type', value('type') === shelf.type ? '' : shelf.type)"
      >
        <component :is="shelf.icon" :size="16" />{{ typeName(shelf.type) }}
      </button>
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
        <button
          v-if="Object.keys(route.query).length"
          class="text-button"
          @click="router.replace({ query: {} })"
        >
          {{ t('clearFilters') }}
        </button>
      </div>
      <div v-if="items.length" class="catalog-grid">
        <div
          v-for="block in blocks"
          :key="block[0]!.id"
          class="bento-block"
          :data-count="block.length"
        >
          <PokemonCard
            v-for="pokemon in block"
            :key="pokemon.id"
            :pokemon="pokemon"
            show-measures
          />
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
.catalog-section.shop-scene {
  --catalog-ink: #41304a;
  --catalog-paper: #fff5e7;
  --album-accent: #644570;
  padding-top: clamp(12px, 2vw, 28px);
}

.shop-front {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  position: relative;
  isolation: isolate;
  overflow: clip;
  color: var(--catalog-paper);
  background:
    repeating-linear-gradient(0deg, transparent 0 2px, #ffffff08 2px 3px),
    repeating-linear-gradient(90deg, transparent 0 2px, #ffffff08 2px 3px), #46354d;
  border-radius: 8px 22px 22px 8px;
  border-left: 10px solid #322638;
  box-shadow:
    inset 3px 0 0 #927f8d,
    0 3px 0 #c5b7a5;
}
.shop-front .shop-heading {
  margin: 0;
  padding: clamp(18px, 3vw, 42px);
  align-items: center;
}
.shop-heading .eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e9d3a5;
  font: 700 0.78rem/1.4 var(--font-mono);
  letter-spacing: 0.12em;
}
.shop-heading h1 {
  text-transform: none;
  margin: 4px 0;
  color: #fff0cb;
  font:
    500 clamp(3rem, 7vw, 6rem) / 1.04 Georgia,
    serif;
  letter-spacing: -0.055em;
}
.shop-intro {
  max-width: 44ch;
  margin-top: 8px;
  line-height: 1.45;
}
.album-cards {
  overflow: clip;
  min-width: 0;
  position: relative;
  align-self: stretch;
  isolation: isolate;
}
.album-print {
  position: absolute;
  top: 8%;
  height: 106%;
  aspect-ratio: 0.72;
  left: 40%;
  background: #c9dac1;
  color: #294232;
  border: 5px solid #fff7dc;
  border-radius: 7px;
  box-shadow: 0 3px 9px #23152565;
  display: grid;
  place-items: center;
  transform: rotate(8deg);
}
.album-print:first-child {
  left: 8%;
  top: 23%;
  background: #f1c4aa;
  transform: rotate(-17deg);
}
.album-print:nth-child(2) {
  left: 24%;
  top: 14%;
  background: #bdd4de;
  transform: rotate(-6deg);
}
.album-print span {
  position: absolute;
  top: 4%;
  left: 6%;
  font: 700 clamp(0.55rem, 1vw, 0.8rem) / 1.2 var(--font-mono);
}
.album-print img {
  width: 94%;
  height: 78%;
  object-fit: contain;
}
.type-shelves {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 4px;
  margin: 14px -4px 8px;
}
.type-shelf {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 44px;
  padding: 6px 16px;
  border: 2px solid transparent;
  border-bottom-color: var(--pokemon-tint);
  background: var(--surface);
  color: var(--ink);
  font: 650 0.87rem/1.2 var(--font-body, sans-serif);
  border-radius: 9px 9px 2px 2px;
}
.type-shelf:hover,
.type-shelf[aria-pressed='true'] {
  border-color: var(--catalog-ink);
  background: var(--pokemon-tint);
  color: var(--catalog-ink);
}
.shop-checkout-bar {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 6px clamp(14px, 3.5vw, 44px);
  border-top: 1px solid #ffffff35;
  background: var(--catalog-ink);
}

.shop-checkout-bar a,
.shop-checkout-bar a:hover {
  color: var(--catalog-paper);
}

.shop-checkout-bar :focus-visible {
  outline-color: var(--catalog-paper);
}

.catalog-trainer,
.shop-links,
.shop-links a,
.shop-playable label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.catalog-trainer > div {
  display: grid;
  gap: 2px;
}

.catalog-trainer small {
  color: var(--sign-label);
}

.shop-links {
  margin-left: auto;
  gap: 16px;
}

.shop-links a,
.shop-playable label {
  min-height: 44px;
  font-size: 0.85rem;
}

.shop-links a:hover {
  text-decoration: underline;
}

.shop-cart > span {
  padding: 2px 7px;
  border-radius: 999px;
  color: var(--sign);
  background: var(--sign-ink);
  font: 700 0.72rem/1.4 var(--font-mono);
}

.shop-playable input {
  width: 16px;
  height: 16px;
  accent-color: var(--purple);
}

.catalog-section .catalog-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: stretch;
  gap: 10px;
}

.catalog-section .search-field {
  grid-column: 1;
  padding-inline: 12px;
  border-radius: 2px;
  border: 2px solid var(--control-border);
}

.shop-scene .filter-control > button {
  border-radius: 2px;
  background: var(--catalog-ink);
  color: var(--catalog-paper);
  border-color: var(--catalog-ink);
}

.catalog-section .search-field input {
  font-size: 1rem;
}

.catalog-section .results-bar {
  margin-block: 10px;
  min-height: 44px;
  border-bottom: 1px solid var(--line);
}

.catalog-grid,
.bento-block {
  display: grid;
  gap: clamp(10px, 1.5vw, 20px);
}
.bento-block {
  grid-template-columns: repeat(6, minmax(0, 1fr));
}
.bento-block > article {
  grid-column: span 2;
}
.bento-block[data-count='6'] > :nth-child(-n + 3),
.bento-block:is([data-count='2'], [data-count='4']) > article,
.bento-block[data-count='5'] > :nth-child(-n + 2) {
  grid-column: span 3;
}
.bento-block[data-count='6'] > :first-child {
  grid-row: span 2;
}
.bento-block[data-count='1'] > article {
  grid-column: 1 / -1;
}
@media (max-width: 800px) {
  .bento-block {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .catalog-grid .bento-block > article:nth-child(n) {
    grid-column: span 1;
    grid-row: auto;
  }
  .catalog-grid .bento-block[data-count='6'] > :is(article:first-child, article:last-child),
  .catalog-grid
    .bento-block:is([data-count='1'], [data-count='3'], [data-count='5'])
    > article:first-child {
    grid-column: 1 / -1;
  }
}
@media (max-width: 640px) {
  .catalog-section .catalog-tools .button {
    padding-inline: 10px;
    gap: 5px;
  }

  .shop-front {
    grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  }

  .shop-front .shop-heading {
    padding: 16px 5px 16px 12px;
  }

  .album-print {
    height: auto;
    width: 55%;
    top: 14%;
  }
  .shop-heading h1 {
    font-size: clamp(1.85rem, 8vw, 4rem);
  }

  .shop-intro {
    font-size: 0.85rem;
  }
}
</style>
