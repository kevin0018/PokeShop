<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()
import { computed, ref, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Plus, ArrowRight, Weight, Ruler } from 'lucide-vue-next'
import { useCatalogStore } from '../application/catalogStore'
import { useCartStore } from '@/cart/application/cartStore'
import {
  money,
  decimal,
  pokemonName,
  number,
  typeName,
  description,
} from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
import StatsPopover from './StatsPopover.vue'
import RecommendationsPanel from './RecommendationsPanel.vue'
import type { Pokemon } from '../domain/pokemon'
const route = useRoute()
const catalog = useCatalogStore()
const cart = useCartStore()
const pokemon = ref<Pokemon>()
const loading = ref(true),
  error = ref(false)
let controller: AbortController | undefined
async function load() {
  controller?.abort()
  controller = new AbortController()
  const current = controller
  loading.value = true
  error.value = false
  pokemon.value = undefined
  try {
    const response = await fetch('/api/v1/pokemon/' + route.params.id, {
      signal: AbortSignal.any([current.signal, AbortSignal.timeout(15000)]),
    })
    if (response.status === 404) return
    if (!response.ok) throw new Error('Request failed')
    const result: Pokemon = await response.json()
    if (!current.signal.aborted) {
      pokemon.value = result
      catalog.remember([result])
    }
  } catch {
    if (!current.signal.aborted) error.value = true
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}
watch(() => route.params.id, load, { immediate: true })
onUnmounted(() => controller?.abort())
const inCart = computed(
  () => cart.lines.find((line) => line.pokemon.id === pokemon.value?.id)?.quantity ?? 0,
)
</script>
<template>
  <RouterLink class="back-link" to="/catalogo"
    ><ArrowLeft :size="16" />{{ t('backCatalog') }}</RouterLink
  >
  <p v-if="loading" class="state-box" role="status">{{ t('loadingPokemon') }}</p>
  <div v-else-if="error" class="state-box" role="alert">
    <p>{{ t('catalogError') }}</p>
    <button class="button primary" @click="load">{{ t('retry') }}</button>
  </div>
  <section v-else-if="pokemon" class="detail-layout">
    <div class="detail-art">
      <span class="dex-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
    </div>
    <div class="detail-copy">
      <p class="eyebrow">{{ t('collection') }} · {{ number(pokemon.species_id ?? pokemon.id) }}</p>
      <h1>{{ pokemonName(pokemon) }}</h1>
      <div class="type-list">
        <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
          typeName(type)
        }}</span>
      </div>
      <p class="description">{{ description(pokemon) }}</p>
      <dl class="pokemon-facts">
        <div>
          <dt><Weight :size="18" />{{ t('weight') }}</dt>
          <dd>
            {{
              pokemon.weight_kg === undefined
                ? t('missingData')
                : decimal(pokemon.weight_kg) + ' kg'
            }}
          </dd>
        </div>
        <div>
          <dt><Ruler :size="18" />{{ t('height') }}</dt>
          <dd>
            {{
              pokemon.height_m === undefined ? t('missingData') : decimal(pokemon.height_m) + ' m'
            }}
          </dd>
        </div>
        <div>
          <dt>{{ t('generationLabel') }}</dt>
          <dd>{{ pokemon.generation ?? t('missingData') }}</dd>
        </div>
        <div>
          <dt>{{ t('region') }}</dt>
          <dd>{{ pokemon.region_names?.[locale] ?? pokemon.region ?? t('missingData') }}</dd>
        </div>
      </dl>
      <div class="abilities">
        <h2>{{ t('abilities') }}</h2>
        <span v-for="ability in pokemon.abilities" :key="ability.name"
          >{{ ability.names[locale] || ability.name }}
          <small v-if="ability.hidden">· {{ t('hiddenAbility') }}</small></span
        >
      </div>
      <StatsPopover :key="pokemon.id" :stats="pokemon.stats" />
      <p class="detail-price">{{ money(pokemon.price_cents) }}</p>
      <p class="stock-label">
        {{ pokemon.stock ? t('stock', pokemon.stock) : t('soldOutNow') }}
      </p>
      <button
        class="button primary"
        :disabled="inCart >= pokemon.stock"
        @click="cart.add(pokemon.id)"
      >
        <Plus :size="19" />
        {{
          !pokemon.stock ? t('soldOut') : inCart >= pokemon.stock ? t('stockMax') : t('addCart')
        }}</button
      ><RouterLink v-if="inCart" class="back-link" to="/carrito"
        >{{ t('viewCart', { count: inCart }) }} <ArrowRight :size="16"
      /></RouterLink>
      <p class="demo-note">{{ t('demoCatalog') }}</p>
    </div>
  </section>
  <RecommendationsPanel v-if="pokemon && !error" :ids="[pokemon.id]" />
  <div v-if="!loading && !error && !pokemon" class="state-box">
    <h1>{{ t('pokemonMissing') }}</h1>
    <p>{{ t('pokemonMissingBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('exploreCatalog') }}</RouterLink>
  </div>
</template>
