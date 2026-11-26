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
  Radio,
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
          <p class="eyebrow"><Radio :size="15" />PokéShop TV</p>
          <h1>{{ t('catalog') }}</h1>
          <p class="shop-intro">
            {{ game.trainer ? t('adventure.catalogHelp') : t('catalogIntro') }}
          </p>
        </div>
      </div>
      <div class="catalog-mascot" aria-hidden="true">
        <span class="mascot-number">025</span>
        <img src="/studio/25.webp" alt="" width="475" height="475" />
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
      <div v-if="items.length" class="pokemon-grid catalog-grid">
        <PokemonCard v-for="pokemon in items" :key="pokemon.id" :pokemon="pokemon" show-measures />
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
  --catalog-ink: #181419;
  --catalog-paper: #fff5e7;
  --catalog-red: #c51933;
  padding-top: clamp(12px, 2vw, 28px);
}

.shop-front {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  position: relative;
  isolation: isolate;
  overflow: clip;
  color: var(--catalog-paper);
  background: var(--catalog-ink);
  border: 3px solid var(--catalog-ink);
}
.shop-front .shop-heading {
  margin: 0;
  padding: clamp(16px, 3vw, 42px);
  align-items: center;
}
.shop-heading .eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--catalog-paper);
  border-bottom: 3px solid #ff3451;
  font: 700 0.72rem/1.7 var(--font-mono);
  text-transform: uppercase;
}
.shop-heading h1 {
  margin: 9px 0;
  color: var(--catalog-paper);
  font: 900 clamp(3.4rem, 8vw, 7rem) / 0.91 var(--font-display);
  letter-spacing: -0.035em;
  transform: skewX(-8deg) rotate(-2deg);
  text-transform: uppercase;
  text-shadow: 3px 4px 0 var(--catalog-red);
}
.shop-intro {
  max-width: 44ch;
  margin-top: 15px;
  line-height: 1.4;
}
.catalog-mascot {
  position: relative;
  isolation: isolate;
  display: grid;
  place-items: center;
}
.catalog-mascot::before {
  content: '';
  position: absolute;
  inset: 0 0 0 -12%;
  background:
    radial-gradient(#48251d45 1px, transparent 1.5px) 0 0 / 6px 6px,
    #ffce49;
  clip-path: polygon(28% 0, 100% 0, 100% 100%, 0 100%, 19% 63%, 9% 67%, 30% 31%, 17% 36%);
}
.mascot-number {
  position: absolute;
  right: 2%;
  color: transparent;
  -webkit-text-stroke: 2px #39231b75;
  font: 900 clamp(4.6rem, 14vw, 12rem) / 1 var(--font-display);
  transform: skewX(-10deg);
}
.catalog-mascot img {
  position: absolute;
  width: 96%;
  height: 96%;
  object-fit: contain;
  filter: drop-shadow(2px 2px 0 white) drop-shadow(4px 3px 0 #181419);
  transform: rotate(-6deg);
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
  font: 900 1.15rem/1 var(--font-display);
  text-transform: uppercase;
  transform: skewX(-5deg);
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

.shop-scene .catalog-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 880px) {
  .shop-scene .catalog-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .shop-scene .catalog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

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

  .shop-heading h1 {
    font-size: clamp(2.55rem, 10vw, 4rem);
  }

  .shop-intro {
    font-size: 0.85rem;
  }
}
</style>
