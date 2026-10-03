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
  <section class="catalog-section">
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
.catalog-section {
  --shop-blue: #719acb;
}
.shop-front {
  overflow: hidden;
  margin-bottom: 24px;
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
  padding: 24px 28px 0;
  margin: 0;
  align-items: center;
}
.shop-heading .eyebrow {
  color: var(--purple);
}
.shop-heading h1 {
  font-size: clamp(28px, 4vw, 40px);
}
.shop-counter-art {
  width: 180px;
  height: 112px;
  flex-shrink: 0;
  image-rendering: pixelated;
}
.shop-intro {
  padding: 0 28px 24px;
  max-width: 820px;
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
  padding: 16px 28px;
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
  margin: 0 0 18px;
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
.catalog-bento {
  display: grid;
  gap: 20px;
}
.catalog-section .bento-block {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}
.catalog-section .bento-block > .pokemon-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  border-radius: 16px;
  background: var(--surface);
}
.catalog-section .bento-block .illustrated-card .card-art {
  position: relative;
  inset: auto;
  display: block;
  height: 220px;
  flex-shrink: 0;
  background: radial-gradient(
    ellipse at 50% 60%,
    color-mix(in srgb, var(--pokemon-tint) 30%, var(--surface)),
    color-mix(in srgb, var(--pokemon-tint) 8%, var(--surface))
  );
  border-bottom: 1px solid var(--line);
}
.catalog-section .bento-block .illustrated-card .card-art::before {
  width: 150px;
  height: 150px;
  left: calc(50% - 75px);
  right: auto;
  top: 40px;
  border-color: color-mix(in srgb, var(--pokemon-tint) 40%, transparent);
}
.catalog-section .bento-block .illustrated-card .card-art img {
  width: 78%;
  height: 84%;
  left: 11%;
  right: auto;
  top: 24px;
}
.catalog-section .bento-block .illustrated-card > .type-list {
  top: 14px;
  left: 14px;
  bottom: auto;
  max-width: calc(100% - 74px);
}
.catalog-section .bento-block .illustrated-card .card-body {
  position: relative;
  inset: auto;
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  padding: 16px;
  background: var(--surface);
}
.catalog-section .illustrated-card h3 {
  font-size: 18px;
  margin: 0 0 8px;
}
.catalog-section .illustrated-card .card-measures {
  margin: 0;
  font-size: 11px;
}
.catalog-section .illustrated-card .card-bottom {
  margin-top: auto;
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 12px;
}
.catalog-section .illustrated-card .catalog-purchase.compact {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 12px;
}
.catalog-section .illustrated-card .card-bottom strong {
  font-size: 18px;
}
.catalog-section .illustrated-card .add-button {
  position: static;
  width: 100%;
  min-height: 44px;
  border-radius: 10px;
  gap: 8px;
  font-size: 13px;
}
.catalog-section .illustrated-card .add-label {
  display: inline;
}
@media (max-width: 900px) {
  .catalog-section .bento-block {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
  }
}
@media (max-width: 700px) {
  .shop-front .shop-heading {
    padding: 18px 16px 8px;
    flex-wrap: nowrap;
    gap: 10px;
  }
  .shop-counter-art {
    width: 120px;
    height: 75px;
  }
  .shop-intro {
    padding: 0 16px 18px;
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
  .catalog-section .bento-block {
    gap: 12px;
  }
  .catalog-bento {
    gap: 12px;
  }
  .catalog-section .bento-block .illustrated-card .card-art {
    height: 160px;
  }
  .catalog-section .bento-block .illustrated-card .card-art::before {
    width: 110px;
    height: 110px;
    left: calc(50% - 55px);
    top: 35px;
  }
  .catalog-section .bento-block .illustrated-card .card-art img {
    width: 92%;
    height: 78%;
    left: 4%;
    top: 30px;
  }
  .catalog-section .bento-block .illustrated-card .card-body {
    padding: 12px;
  }
  .catalog-section .illustrated-card h3 {
    font-size: 15px;
  }
  .catalog-section .illustrated-card .card-bottom strong {
    font-size: 14px;
  }
  .catalog-section .illustrated-card .add-button {
    font-size: 11px;
    padding-inline: 5px;
  }
  .catalog-section .illustrated-card .card-measures {
    font-size: 9px;
  }
}
@media (max-width: 350px) {
  .catalog-section .bento-block {
    grid-template-columns: minmax(0, 1fr);
  }
  .shop-counter-art {
    width: 96px;
    height: 60px;
  }
}
</style>
