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
  ArrowUpRight,
  Check,
} from 'lucide-vue-next'
import CatalogFilters from './CatalogFilters.vue'
import PokemonCard from './PokemonCard.vue'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import { useAdventureStore } from '@/adventure/store'
import { useCartStore } from '@/cart/application/cartStore'

import type { Pokemon } from '../domain/pokemon'
const habitats = [
  { key: 'forest', position: '0%', species: 10 },
  { key: 'sea', position: '50%', species: 131 },
  { key: 'cave', position: '100%', species: 41 },
] as const
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
  if (route.path === '/catalogo') catalog.catalogLocation = route.fullPath
  controller?.abort()
  controller = new AbortController()
  const current = controller
  loading.value = true
  error.value = false
  const params = new URLSearchParams({ limit: '24', offset: String((page.value - 1) * 24) })
  for (const key of ['q', 'habitat', 'type', 'region', 'generation', 'forms', 'sort'])
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
      <h1>{{ t('guide.title') }}</h1>
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

    <section class="habitats" aria-labelledby="habitat-title">
      <h2 id="habitat-title">{{ t('guide.explore') }}</h2>
      <div class="habitat-strip">
        <button
          v-for="habitat in habitats"
          :key="habitat.key"
          type="button"
          class="habitat-scene"
          :style="{ backgroundPosition: 'center ' + habitat.position }"
          :aria-pressed="value('habitat') === habitat.key"
          @click="change('habitat', value('habitat') === habitat.key ? '' : habitat.key)"
        >
          <img
            :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${habitat.species}.png`"
            alt=""
          />
          <span>{{ t(`guide.${habitat.key}`) }}</span>
          <Check v-if="value('habitat') === habitat.key" :size="18" />
          <ArrowUpRight v-else :size="18" />
        </button>
      </div>
    </section>

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
.app-shell:has(.shop-scene) .main-content {
  width: min(1290px, 92%);
  padding-top: 20px;
}
:root[data-theme='dark'] .app-shell:has(.shop-scene) {
  background: #142029;
}
.catalog-section.shop-scene {
  padding-top: 0;
}
.shop-front,
.shop-checkout-bar,
.catalog-trainer,
.shop-links,
.shop-links a,
.shop-playable label {
  display: flex;
  align-items: center;
  gap: 8px;
}
.shop-front,
.shop-checkout-bar {
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 12px;
}
.shop-front h1 {
  margin: 0;
  font:
    normal clamp(2.3rem, 4vw, 3.25rem) / 1.05 Georgia,
    serif;
  letter-spacing: -0.05em;
}
.catalog-trainer > div {
  display: grid;
}
.shop-links a,
.shop-playable label {
  min-height: 44px;
  font-size: 0.85rem;
}
.shop-links a:hover {
  text-decoration: underline;
}
.shop-cart span {
  font-weight: 700;
}
.catalog-section .catalog-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  margin: 18px 0;
}
.catalog-section .search-field {
  grid-column: 1;
  padding-inline: 14px;
  min-height: 48px;
  border: 1px solid var(--control-border);
  border-radius: 6px;
}
.habitats h2 {
  margin: 0 0 9px;
  font: 650 0.95rem/1.4 var(--font-body);
}
.habitat-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.habitat-scene {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: clamp(98px, 11vw, 136px);
  padding: 12px 16px;
  border: 0;
  border-radius: 5px;
  color: white;
  background-image: url('/studio/field-habitats.webp');
  background-size: 100% 300%;
  font:
    normal clamp(1.3rem, 2.4vw, 2rem) / 1 Georgia,
    serif;
}
.habitat-scene::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: linear-gradient(0deg, #071420ed, transparent 65%);
}
.habitat-scene img {
  position: absolute;
  z-index: -1;
  right: 18%;
  bottom: 12%;
  width: 23%;
  height: 55%;
  object-fit: contain;
  filter: drop-shadow(0 3px 2px #17252b90);
}
.habitat-scene[aria-pressed='true'] {
  box-shadow: inset 0 0 0 3px #fff3bc;
}
.habitat-scene:hover span {
  text-decoration: underline;
}
.catalog-section .results-bar {
  min-height: 38px;
  margin: 7px 0;
}
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 24px 18px;
}
@media (max-width: 950px) {
  .catalog-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 700px) {
  .catalog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px 8px;
  }
  .habitat-strip {
    gap: 5px;
  }
  .habitat-scene {
    padding: 8px;
    height: 86px;
  }
  .habitat-scene img {
    width: 38%;
    right: 9%;
    bottom: 23%;
  }
  .habitat-scene svg {
    width: 14px;
  }
}
</style>
