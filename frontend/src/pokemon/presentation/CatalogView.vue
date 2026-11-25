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
          <p class="shop-intro">
            {{ game.trainer ? t('adventure.catalogHelp') : t('catalogIntro') }}
          </p>
        </div>
      </div>
      <ShopCounter />
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
.shop-scene {
  padding-top: 0;
}

.shop-front {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  position: relative;
  overflow: clip;
  margin-bottom: 20px;
  border-radius: var(--shop-radius);
  background: var(--sign);
  color: var(--sign-ink);
}

.shop-awning {
  grid-column: 1 / -1;
  height: 9px;
  background: repeating-linear-gradient(
    90deg,
    var(--sign-accent) 0 36px,
    var(--sign-ink) 36px 72px
  );
}

.shop-front .shop-heading {
  margin: 0;
  padding: clamp(16px, 2.8vw, 36px);
  align-items: center;
}

.shop-heading .eyebrow,
.shop-intro {
  color: var(--sign-label);
}

.shop-heading h1 {
  font-size: clamp(2.6rem, 6vw, 5.5rem);
  line-height: 0.94;
}

.shop-intro {
  margin-top: 12px;
  max-width: 52ch;
  line-height: 1.5;
}

.shop-counter-art {
  align-self: center;
  width: clamp(90px, 23vw, 232px);
  margin: 8px clamp(12px, 3.5vw, 44px) 8px 0;
  height: auto;
}

.shop-checkout-bar {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 6px clamp(14px, 3.5vw, 44px);
  border-top: 1px solid var(--sign-label);
}

.shop-checkout-bar a,
.shop-checkout-bar a:hover {
  color: var(--sign-ink);
}

.shop-checkout-bar :focus-visible {
  outline-color: var(--sign-ink);
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
  border-color: var(--control-border);
}

.catalog-section .search-field input {
  font-size: 1rem;
}

.catalog-section .results-bar {
  margin-block: 10px;
  min-height: 44px;
  border-bottom: 1px solid var(--line);
}

.catalog-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 880px) {
  .catalog-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .catalog-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .catalog-section .catalog-tools .button {
    padding-inline: 10px;
    gap: 5px;
  }

  .shop-heading h1 {
    font-size: clamp(2rem, 9vw, 3.5rem);
  }

  .shop-intro {
    font-size: 0.85rem;
  }
}
</style>
