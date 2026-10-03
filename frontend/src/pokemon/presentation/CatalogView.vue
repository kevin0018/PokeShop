<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search, ArrowLeft, ArrowRight, Coins, ShoppingBag, UsersRound } from 'lucide-vue-next'
import CatalogFilters from './CatalogFilters.vue'
import PokemonCard from './PokemonCard.vue'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import { useAdventureStore } from '@/adventure/store'
import { useCartStore } from '@/cart/application/cartStore'
import ShopCounter from './ShopCounter.vue'

import type { Pokemon } from '../domain/pokemon'
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
      <div class="shop-awning" aria-hidden="true"></div>
      <div class="section-heading shop-heading">
        <div>
          <p class="eyebrow">{{ t('shopLabel') }}</p>
          <h1>{{ t('catalog') }}</h1>
        </div>
        <ShopCounter />
      </div>
      <p class="shop-intro">{{ game.trainer ? t('adventure.catalogHelp') : t('catalogIntro') }}</p>
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
.shop-scene {
  --shop-blue: #5a8da8;
  padding-top: 8px;
  position: relative;
  isolation: isolate;
}
.shop-scene::before {
  content: '';
  position: absolute;
  inset: 0 -12px;
  z-index: -1;
  pointer-events: none;
  background-image:
    linear-gradient(color-mix(in srgb, var(--shop-blue) 7%, transparent) 1px, transparent 1px),
    linear-gradient(
      90deg,
      color-mix(in srgb, var(--shop-blue) 7%, transparent) 1px,
      transparent 1px
    );
  background-size: 48px 48px;
  mask-image: linear-gradient(#000, #000 70%, transparent);
}
:root[data-theme='dark'] .shop-scene {
  --shop-blue: #81b6d2;
}
.shop-front {
  overflow: hidden;
  margin-bottom: 14px;
  position: relative;
  border: 1px solid color-mix(in srgb, var(--shop-blue) 45%, var(--line));
  border-radius: 20px;
  background: var(--surface);
  box-shadow: 0 5px 0 color-mix(in srgb, var(--shop-blue) 16%, var(--surface));
}
.shop-awning {
  height: 22px;
  background: repeating-linear-gradient(
    90deg,
    var(--shop-blue) 0 42px,
    color-mix(in srgb, var(--shop-blue) 22%, var(--surface)) 42px 84px
  );
  border-bottom: 4px solid color-mix(in srgb, var(--shop-blue) 45%, var(--surface));
}
.shop-front .shop-heading {
  padding: 20px 280px 8px 24px;
  margin: 0;
  align-items: center;
}
.shop-heading .eyebrow {
  color: var(--purple);
}
.shop-heading h1 {
  font-size: clamp(26px, 3vw, 34px);
}
.shop-counter-art {
  position: absolute;
  right: 24px;
  top: 28px;
  width: 216px;
  height: 134px;
  flex-shrink: 0;
  image-rendering: pixelated;
}
.shop-intro {
  padding: 0 280px 18px 24px;
  min-height: 50px;
  color: var(--muted-strong);
  font-size: 14px;
  line-height: 1.6;
}
.shop-checkout-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  padding: 10px 24px;
  border-top: 1px solid var(--line);
  background: color-mix(in srgb, var(--shop-blue) 9%, var(--surface));
}
.catalog-trainer {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--purple);
}
.catalog-trainer > div {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.catalog-trainer small {
  font-size: 11px;
  color: var(--muted-strong);
}
.catalog-trainer strong {
  font-size: 18px;
  font-variant-numeric: tabular-nums;
}
.shop-links {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-left: auto;
}
.shop-links a {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  font-size: 13px;
}
.shop-cart {
  padding: 8px 14px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface);
}
.shop-cart > span {
  display: grid;
  place-items: center;
  min-width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--badge);
  color: var(--purple);
  font-size: 12px;
}
.shop-playable {
  margin: 0 0 6px;
  font-size: 13px;
  color: var(--muted-strong);
}
.shop-playable label {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  min-height: 44px;
  cursor: pointer;
}
.shop-playable input {
  width: 16px;
  height: 16px;
  accent-color: var(--purple);
}
.catalog-section .catalog-tools {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--surface);
}
.catalog-section .search-field {
  flex: 1 1 260px;
}
@media (max-width: 700px) {
  .shop-front .shop-heading {
    padding: 16px 140px 8px 16px;
    flex-wrap: nowrap;
    gap: 10px;
  }
  .shop-counter-art {
    right: 12px;
    top: 28px;
    width: 120px;
    height: 75px;
  }
  .shop-intro {
    padding: 0 16px 14px;
    padding-top: 20px;
    font-size: 13px;
  }
  .shop-checkout-bar {
    padding: 12px 16px;
    gap: 8px;
  }
  .shop-links {
    gap: 12px;
  }
  .shop-links a {
    font-size: 12px;
  }
  .catalog-section .search-field {
    flex-basis: 180px;
    min-width: 0;
  }
}
@media (max-width: 350px) {
  .shop-counter-art {
    width: 96px;
    height: 60px;
  }
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
    width: 100%;
    top: 0;
    bottom: 0;
    transform: none;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
  }
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-body > h3,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-body > h3,
  .bento-block[data-count='1'] .card-body > h3,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-measures,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-measures,
  .bento-block[data-count='1'] .card-measures {
    max-width: 42%;
  }
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-bottom,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-bottom,
  .bento-block[data-count='1'] .card-bottom {
    min-height: 44px;
  }
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .add-button,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .add-button,
  .bento-block[data-count='1'] .add-button {
    position: absolute;
    right: 18px;
    bottom: 14px;
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
  .catalog-bento .bento-block > .pokemon-card:nth-child(n) {
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
  .catalog-bento .bento-block > .pokemon-card:nth-child(n) {
    grid-column: span 1;
    grid-row: span 1;
  }
}
</style>
