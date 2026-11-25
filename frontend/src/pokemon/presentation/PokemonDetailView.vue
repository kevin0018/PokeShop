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
import CatalogPurchase from '@/adventure/CatalogPurchase.vue'
import { useAdventureStore } from '@/adventure/store'
const route = useRoute()
const catalog = useCatalogStore()
const cart = useCartStore()
const game = useAdventureStore()
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
    <div class="detail-art pokemon-palette" :data-type="pokemon.types[0]">
      <StatsPopover :key="pokemon.id" :stats="pokemon.stats" />
      <span class="dex-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
    </div>
    <div class="detail-copy">
      <p class="eyebrow">{{ t('studio.spotlight') }}</p>
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
      <div class="detail-purchase">
        <template v-if="game.trainer">
          <CatalogPurchase :pokemon="pokemon" />
          <p v-if="game.error" role="alert">{{ t(`adventure.errors.${game.error}`) }}</p>
        </template>
        <template v-else>
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
        </template>
      </div>
    </div>
  </section>
  <RecommendationsPanel v-if="pokemon && !error" :ids="[pokemon.id]" />
  <div v-if="!loading && !error && !pokemon" class="state-box">
    <h1>{{ t('pokemonMissing') }}</h1>
    <p>{{ t('pokemonMissingBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('exploreCatalog') }}</RouterLink>
  </div>
</template>

<style>
.detail-layout {
  align-items: start;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: clamp(20px, 4vw, 58px);
}

.detail-art.pokemon-palette {
  display: grid;
  place-items: center;
  min-height: 0;
  aspect-ratio: 1.07;
  border-radius: var(--shop-radius);
  border: 1px solid var(--line);
  background:
    radial-gradient(
      circle closest-side,
      transparent 75%,
      var(--surface) 75.5% 76%,
      transparent 76.5% 91%,
      var(--surface) 91.5% 92%,
      transparent 92.5%
    ),
    radial-gradient(color-mix(in srgb, var(--pokemon-tint) 50%, transparent) 1px, transparent 1.2px)
      0 0 / 10px 10px,
    color-mix(in srgb, var(--pokemon-tint) 38%, var(--surface));
}

.detail-art::after {
  content: '';
  position: absolute;
  left: 25%;
  right: 25%;
  bottom: 9%;
  height: 8%;
  border-radius: 50%;
  background: color-mix(in srgb, var(--pokemon-tint) 50%, transparent);
  filter: blur(5px);
  pointer-events: none;
}
.detail-art img {
  position: relative;
  z-index: 1;
  width: 90%;
  height: 86%;
  object-fit: contain;
  filter: drop-shadow(0 16px 12px var(--shop-shadow));
}

.detail-art .stats-trigger {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 2;
  min-width: 44px;
  min-height: 44px;
  margin-top: 0;
}

.detail-art > .dex-number {
  z-index: 2;
  top: 16px;
  left: 16px;
  padding: 4px 8px;
  border-radius: 4px;
  background: var(--surface);
  color: var(--ink);
}

.detail-copy {
  min-width: 0;
}

.detail-copy h1 {
  margin: 8px 0 14px;
  line-height: 0.98;
}

.detail-copy .type-tag {
  padding: 4px 9px;
  font-size: 0.76rem;
}

.detail-copy .description {
  margin: 18px 0;
}

.detail-copy .pokemon-facts {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  border: 1px solid var(--line);
  border-radius: var(--shop-radius);
  padding: 0;
  overflow: clip;
  background: var(--surface);
}

.pokemon-facts > div {
  min-width: 0;
  padding: 12px;
}

.pokemon-facts > div:nth-child(odd) {
  border-right: 1px solid var(--line);
}

.pokemon-facts > div:nth-child(-n + 2) {
  border-bottom: 1px solid var(--line);
}

.pokemon-facts dd {
  margin-top: 4px;
  overflow-wrap: anywhere;
}

.detail-purchase {
  padding: 18px;
  border: 1px solid var(--line);
  border-top: 4px solid var(--purple);
  border-radius: var(--shop-radius);
  background: var(--surface);
}

.detail-price {
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.detail-purchase .stock-label {
  margin-bottom: 12px;
}

.detail-purchase .back-link {
  margin: 5px 0 0;
}

.detail-purchase .demo-note {
  padding-top: 12px;
  margin-top: 14px;
}

@media (max-width: 700px) {
  .detail-layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .detail-art.pokemon-palette {
    max-width: none;
    aspect-ratio: 1.3;
  }

  .detail-purchase .button {
    width: 100%;
  }
}
</style>
