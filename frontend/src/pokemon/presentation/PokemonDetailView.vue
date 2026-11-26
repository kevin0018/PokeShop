<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()
import { computed, ref, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ShoppingBag, ArrowRight, Weight, Ruler, Radio } from 'lucide-vue-next'
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
  <section
    v-else-if="pokemon"
    :key="pokemon.id"
    class="pokemon-profile pokemon-palette"
    :data-type="pokemon.types[0]"
  >
    <div class="profile-stage">
      <header class="profile-heading">
        <p class="program-label"><Radio :size="16" />{{ t('studio.spotlight') }}</p>
        <h1>{{ pokemonName(pokemon) }}</h1>
        <div class="type-list">
          <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
            typeName(type)
          }}</span>
        </div>
      </header>
      <div class="profile-art">
        <span class="profile-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span>
        <PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
        <StatsPopover :key="pokemon.id" :stats="pokemon.stats" />
      </div>
      <div class="detail-purchase">
        <template v-if="game.trainer">
          <CatalogPurchase :pokemon="pokemon" />
          <p v-if="game.error" role="alert">{{ t(`adventure.errors.${game.error}`) }}</p>
        </template>
        <template v-else>
          <div class="price-slip">
            <small>{{ t('studio.price') }}</small>
            <p class="detail-price">{{ money(pokemon.price_cents) }}</p>
            <p class="stock-label">
              {{ pokemon.stock ? t('stock', pokemon.stock) : t('soldOutNow') }}
            </p>
          </div>
          <button
            class="button primary"
            :disabled="inCart >= pokemon.stock"
            @click="cart.add(pokemon.id)"
          >
            <ShoppingBag :size="19" />
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
    <div class="profile-record">
      <p class="description">{{ description(pokemon) }}</p>
      <dl class="pokemon-facts">
        <div>
          <dt><Weight :size="18" />{{ t('weight') }}</dt>
          <dd>
            {{ pokemon.weight_kg == null ? t('missingData') : decimal(pokemon.weight_kg) + ' kg' }}
          </dd>
        </div>
        <div>
          <dt><Ruler :size="18" />{{ t('height') }}</dt>
          <dd>
            {{ pokemon.height_m == null ? t('missingData') : decimal(pokemon.height_m) + ' m' }}
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
.pokemon-profile {
  --profile-black: #171419;
  --profile-paper: #fff5e7;
  --profile-red: #bd1833;
}
.profile-stage {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  grid-template-areas: 'art heading' 'art buy';
  background: var(--profile-black);
  color: var(--profile-paper);
  border: 3px solid var(--profile-black);
}
.profile-heading,
.detail-purchase {
  padding-inline: clamp(20px, 3.5vw, 52px);
  min-width: 0;
}
.profile-heading {
  grid-area: heading;
  align-self: end;
  padding-block: 32px 14px;
}
.program-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid #ff3956;
  font: 750 0.73rem/1.9 var(--font-mono);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  transform: rotate(-2deg);
}
.profile-heading h1 {
  margin: 0.16em 0 0.23em;
  font: 900 clamp(3.4rem, 6.5vw, 6rem) / 0.95 var(--font-display);
  letter-spacing: -0.035em;
  text-transform: uppercase;
  overflow-wrap: anywhere;
  transform: skewX(-6deg);
  text-shadow: 3px 4px 0 var(--profile-red);
}
.profile-heading .type-tag {
  border-radius: 0;
  font: 700 0.76rem/1.6 var(--font-mono);
  transform: skewX(-5deg);
}
.profile-art {
  grid-area: art;
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: clamp(330px, 32vw, 470px);
  display: grid;
  place-items: center;
  background:
    linear-gradient(
      148deg,
      transparent 55%,
      #fff9 55% 58%,
      transparent 58% 60%,
      #fff9 60% 67%,
      transparent 67%
    ),
    radial-gradient(#21172540 1px, transparent 1.6px) 0 0/6px 6px,
    var(--pokemon-tint);
}
.profile-art::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 26%;
  z-index: -1;
  background: var(--profile-black);
  clip-path: polygon(0 70%, 65% 28%, 54% 55%, 100% 0, 100% 100%, 0 100%);
}
.profile-number {
  position: absolute;
  top: 4%;
  left: 3%;
  color: transparent;
  -webkit-text-stroke: 2px #2018257a;
  font: 900 clamp(5rem, 12vw, 12rem) / 0.9 var(--font-display);
  transform: skewX(-8deg);
}
.profile-art img {
  position: absolute;
  width: 80%;
  height: 80%;
  object-fit: contain;
  filter: drop-shadow(2px 2px 0 white) drop-shadow(4px 5px 0 #171419);
}
.profile-art .image-fallback {
  color: var(--profile-black);
}
.profile-art .stats-trigger {
  position: absolute;
  right: 12px;
  bottom: 12px;
  min-height: 44px;
  border: 2px solid var(--profile-paper);
  border-radius: 0;
  background: var(--profile-black);
  color: var(--profile-paper);
  transform: rotate(-2deg);
}
.detail-purchase {
  grid-area: buy;
  align-self: start;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 14px;
  padding-block: 12px 24px;
}
.price-slip,
.detail-purchase .catalog-purchase strong {
  background: var(--profile-paper);
  color: var(--profile-black);
  padding: 8px 15px;
  transform: rotate(-2deg);
}
.price-slip small {
  text-transform: uppercase;
  font: 750 0.66rem/1 var(--font-mono);
  letter-spacing: 0.12em;
}
.price-slip .detail-price,
.detail-purchase .catalog-purchase strong {
  margin: 0;
  font: 900 clamp(1.9rem, 3.3vw, 3rem) / 1 var(--font-display);
}
.price-slip .stock-label {
  margin: 4px 0 0;
  color: inherit;
  font: 700 0.66rem/1.25 var(--font-mono);
}
.detail-purchase .button.primary {
  min-height: 48px;
  max-width: 100%;
  padding: 10px 15px;
  color: white;
  background: var(--profile-red);
  border: 2px solid var(--profile-paper);
  border-radius: 0;
  box-shadow: 3px 3px 0 #ea5268;
  font: 900 1.25rem/1.05 var(--font-display);
  text-transform: uppercase;
  transform: rotate(-2deg);
}
.detail-purchase .button.primary:hover:not(:disabled) {
  background: #941a30;
}
.detail-purchase .back-link,
.detail-purchase .purchase-unavailable {
  margin: 0;
  color: var(--profile-paper);
}
.detail-purchase .demo-note {
  width: 100%;
  margin: 4px 0 0;
  padding: 0;
  color: #d5cbd0;
  border: 0;
}
.profile-record {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  align-items: center;
  padding-block: 22px;
  border-bottom: 2px solid var(--ink);
}
.profile-record .description {
  color: var(--ink);
  margin: 0;
  font-size: clamp(1rem, 1.5vw, 1.2rem);
  line-height: 1.5;
  max-width: 53ch;
}
.profile-record .pokemon-facts {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: 0;
  padding: 0;
  border: 0;
  gap: 10px;
}
.profile-record dt {
  min-height: 22px;
}
.profile-record dd {
  font-weight: 700;
  overflow-wrap: anywhere;
}
@media (prefers-reduced-motion: no-preference) {
  .profile-art img {
    animation: profile-enter 360ms ease-out both;
  }
  .price-slip,
  .detail-purchase .button.primary {
    animation: offer-enter 280ms 100ms ease-out backwards;
  }
  @keyframes profile-enter {
    from {
      opacity: 0;
      transform: translateX(-14px) scale(0.94);
    }
  }
  @keyframes offer-enter {
    from {
      opacity: 0;
      translate: 8px 0;
    }
  }
}
@media (max-width: 740px) {
  .profile-stage {
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas: 'heading' 'art' 'buy';
  }
  .profile-heading {
    padding: 16px 16px 14px;
  }
  .profile-heading h1 {
    font-size: clamp(2.65rem, 10vw, 4.3rem);
  }
  .profile-art {
    min-height: clamp(215px, 50vw, 295px);
  }
  .profile-art img {
    top: 4px;
    height: calc(100% - 53px);
  }
  .profile-art .stats-trigger {
    bottom: 5px;
  }
  .detail-purchase {
    gap: 12px;
    padding: 16px 12px;
  }
  .detail-purchase .button.primary {
    flex: 1;
  }
  .profile-record {
    grid-template-columns: minmax(0, 1fr);
    gap: 16px;
  }
  .profile-record .pokemon-facts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
