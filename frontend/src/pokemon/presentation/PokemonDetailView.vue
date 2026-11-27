<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t, locale } = useI18n()
import { computed, ref, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, ShoppingBag, ArrowRight, Weight, Ruler } from 'lucide-vue-next'
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
  try {
    const response = await fetch('/api/v1/pokemon/' + route.params.id, {
      signal: AbortSignal.any([current.signal, AbortSignal.timeout(15000)]),
    })
    if (response.status === 404) {
      if (!current.signal.aborted) pokemon.value = undefined
      return
    }
    if (!response.ok) throw new Error('Request failed')
    const result: Pokemon = await response.json()
    if (!current.signal.aborted) {
      pokemon.value = result
      catalog.remember([result])
    }
  } catch {
    if (!current.signal.aborted) {
      pokemon.value = undefined
      error.value = true
    }
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
  <RouterLink v-if="!pokemon" class="back-link" to="/catalogo"
    ><ArrowLeft :size="16" />{{ t('backCatalog') }}</RouterLink
  >
  <p v-if="loading && !pokemon" class="state-box" role="status">{{ t('loadingPokemon') }}</p>
  <div v-else-if="error" class="state-box" role="alert">
    <p>{{ t('catalogError') }}</p>
    <button class="button primary" @click="load">{{ t('retry') }}</button>
  </div>
  <section
    v-else-if="pokemon"
    :aria-busy="loading"
    class="pokemon-profile pokemon-palette"
    :data-type="pokemon.types[0]"
  >
    <div class="profile-stage">
      <RouterLink class="scene-back" to="/catalogo"
        ><ArrowLeft :size="14" />{{ t('backCatalog') }}</RouterLink
      >
      <nav
        v-if="pokemon.evolution_family && pokemon.evolution_family.length > 1"
        class="evolution-rail"
        :aria-label="t('evolutionFamily')"
      >
        <RouterLink
          v-for="member in pokemon.evolution_family"
          :key="member.id"
          :to="'/pokemon/' + member.id"
          :aria-current="member.id === pokemon.id ? 'page' : undefined"
          :title="pokemonName(member)"
          :aria-label="pokemonName(member)"
        >
          <PokemonImage :src="member.image_url" :name="pokemonName(member)" />
          <span>{{ number(member.id) }}</span>
        </RouterLink>
      </nav>
      <span class="profile-spine" aria-hidden="true">{{ typeName(pokemon.types[0]) }}</span>
      <header class="profile-heading">
        <small class="profile-index">Pokédex {{ number(pokemon.species_id ?? pokemon.id) }}</small>
        <h1>{{ pokemonName(pokemon) }}</h1>
        <div class="type-list">
          <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
            typeName(type)
          }}</span>
        </div>
        <p class="description profile-description">{{ description(pokemon) }}</p>
      </header>
      <div class="profile-stats">
        <StatsPopover :key="pokemon.id" :stats="pokemon.stats" :type="pokemon.types[0]" />
      </div>
      <span class="profile-number" aria-hidden="true">{{
        number(pokemon.species_id ?? pokemon.id)
      }}</span>
      <div class="profile-art">
        <PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" loading="eager" />
      </div>
      <div class="detail-purchase" :inert="loading">
        <template v-if="game.trainer">
          <small class="trainer-price-label">{{ t('studio.price') }}</small>
          <CatalogPurchase :pokemon="pokemon" />
          <p class="trainer-balance">
            {{
              t('trainerBalance', {
                balance: t('adventure.credits', {
                  amount: game.trainer.credits.toLocaleString(locale),
                }),
              })
            }}
          </p>
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
        <section v-if="pokemon.abilities?.length" class="profile-abilities">
          <h2>{{ t('abilities') }}</h2>
          <ul>
            <li v-for="ability in pokemon.abilities" :key="ability.name">
              {{ ability.names[locale] || ability.name }}
              <small v-if="ability.hidden">{{ t('hiddenAbility') }}</small>
            </li>
          </ul>
        </section>
      </div>
      <div class="profile-record">
        <dl class="pokemon-facts">
          <div>
            <dt><Weight :size="18" />{{ t('weight') }}</dt>
            <dd>
              {{
                pokemon.weight_kg == null ? t('missingData') : decimal(pokemon.weight_kg) + ' kg'
              }}
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
      <RecommendationsPanel :ids="[pokemon.id]" thumbnails />
    </div>
  </section>
  <div v-if="!loading && !error && !pokemon" class="state-box">
    <h1>{{ t('pokemonMissing') }}</h1>
    <p>{{ t('pokemonMissingBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('exploreCatalog') }}</RouterLink>
  </div>
</template>

<style>
.profile-stage {
  --profile-bg: #111116;
  --profile-ink: #fffaf4;
  --profile-muted: #e0d4ce;
  --accent: color-mix(in oklch, var(--pokemon-tint), #fff 4%);
  --spotlight: oklch(from var(--pokemon-tint) 64% 0.21 h);
  display: grid;
  position: relative;
  isolation: isolate;
  container-type: inline-size;
  overflow: hidden;
  grid-template-columns: minmax(45px, 0.32fr) minmax(0, 1.05fr) minmax(0, 2.2fr) minmax(0, 1.22fr);
  grid-template-areas: 'spine heading art buy' 'spine heading art recommendations';
  grid-template-rows: 1fr auto;
  padding: clamp(22px, 3vw, 48px);
  gap: 20px;
  min-height: clamp(490px, 46vw, 660px);
  border-radius: 12px;
  color: var(--profile-ink);
  background:
    radial-gradient(ellipse at 49% -25%, var(--spotlight), transparent 74%),
    linear-gradient(
      165deg,
      color-mix(in srgb, var(--spotlight) 78%, #131016),
      #1e181c 55%,
      #0c0d12 90%
    );
}
.profile-spine {
  grid-area: spine;
  writing-mode: vertical-rl;
  justify-self: center;
  align-self: center;
  text-transform: uppercase;
  font: 900 clamp(3rem, 7vw, 7.5rem) / 0.85 var(--font-display);
  letter-spacing: -0.04em;
}
.profile-heading,
.detail-purchase,
.recommendation-thumbnails {
  z-index: 1;
  min-width: 0;
}
.profile-heading {
  grid-area: heading;
  align-self: center;
}
.profile-index {
  font: 750 0.72rem/1.6 var(--font-mono);
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
.profile-heading h1 {
  margin: 0.18em 0 0.32em;
  font: 900 clamp(2rem, 4.5cqw, 4.2rem) / 0.96 var(--font-display);
  letter-spacing: -0.035em;
  text-transform: uppercase;
  overflow-wrap: anywhere;
}
.profile-description {
  font-size: 0.94rem;
  line-height: 1.55;
  margin: 1.25em 0;
}
.profile-stats {
  grid-area: stats;
  align-self: center;
  z-index: 1;
}
.profile-stats .stats-trigger {
  margin: 0;
  min-height: 44px;
  padding: 6px 10px;
  background: #100e1280;
  border: 1px solid #ffffff58;
  color: var(--profile-ink);
}
.profile-art {
  grid-area: art;
  display: grid;
  place-items: center;
  position: relative;
  min-width: 0;
}
.profile-number {
  grid-area: art;
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  color: #ffffff0e;
  font: 900 clamp(9rem, 23cqw, 23rem) / 0.8 var(--font-display);
  letter-spacing: -0.06em;
  pointer-events: none;
}
.profile-art > img {
  position: absolute;
  width: 123%;
  max-width: none;
  height: 111%;
  object-fit: contain;
  filter: drop-shadow(0 24px 14px #09070ab0);
}
.detail-purchase {
  grid-area: buy;
  align-self: center;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
  padding-block: 15px;
}
.detail-purchase .catalog-purchase {
  flex-direction: column;
  align-items: flex-start;
}
.price-slip small {
  color: var(--profile-muted);
  text-transform: uppercase;
  font: 750 0.72rem/1 var(--font-mono);
  letter-spacing: 0.1em;
}
.price-slip .detail-price,
.detail-purchase .catalog-purchase strong {
  margin: 3px 0 0;
  font: 900 clamp(2.1rem, 4vw, 3.5rem) / 1 var(--font-display);
}
.price-slip .stock-label {
  margin: 6px 0 0;
  color: var(--profile-muted);
}
.detail-purchase .button.primary {
  min-height: 48px;
  max-width: 100%;
  padding: 10px 20px;
  color: #151218;
  background: var(--accent);
  border: 1px solid transparent;
  border-radius: 999px;
  box-shadow: none;
}
.detail-purchase .button.primary:hover:not(:disabled) {
  background: color-mix(in srgb, var(--pokemon-tint) 78%, white);
}
.detail-purchase .back-link {
  margin: 0;
  color: var(--profile-ink);
}
.detail-purchase .purchase-unavailable,
.detail-purchase .demo-note {
  margin: 0;
  padding: 0;
  color: var(--profile-muted);
  border: 0;
}
.profile-stage .recommendation-thumbnails {
  grid-area: recommendations;
  justify-self: end;
  min-width: 0;
  width: 100%;
  max-width: 370px;
}
.profile-record {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
  align-items: center;
  padding-block: 22px;
  border-bottom: 2px solid var(--ink);
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
.evolution-rail {
  grid-area: family;
  align-self: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 390px;
  overflow: auto;
  scrollbar-width: thin;
  padding: 4px;
  min-width: 0;
}
.evolution-rail a {
  flex: none;
  display: grid;
  place-items: center;
  gap: 2px;
  border: 1px solid #ffffff42;
  border-radius: 6px;
  padding: 4px 2px;
  color: var(--profile-ink);
  text-decoration: none;
  background: #19151985;
  text-align: center;
  font: 650 0.72rem/1.2 var(--font-display);
  overflow-wrap: anywhere;
}
.evolution-rail img {
  width: 100%;
  height: 44px;
  object-fit: contain;
}
.evolution-rail a[aria-current='page'],
.evolution-rail a:hover {
  border-color: var(--accent);
  background: #161318d9;
}
.evolution-rail a:focus-visible {
  outline: 2px solid white;
  outline-offset: 1px;
}
.evolution-rail .image-fallback {
  min-height: 44px;
  font-size: 0.65rem;
  padding: 0;
}
@media (min-width: 901px) {
  .profile-stage:has(.evolution-rail) {
    grid-template-columns: 76px minmax(36px, 0.25fr) minmax(0, 1.05fr) minmax(0, 2.2fr) minmax(
        0,
        1.22fr
      );
    grid-template-areas: 'family spine heading art buy' 'family spine heading art recommendations';
    column-gap: clamp(9px, 1vw, 18px);
  }
}
@media (prefers-reduced-motion: no-preference) {
  .profile-art > img {
    animation: profile-enter 360ms ease-out both;
  }
  @keyframes profile-enter {
    from {
      opacity: 0;
      transform: translateY(8px) scale(0.96);
    }
  }
}
@media (max-width: 900px) {
  .profile-stage {
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    grid-template-areas: 'heading art' 'buy recommendations';
    gap: 18px;
  }
  .profile-stage:has(.evolution-rail) {
    grid-template-areas: 'heading art' 'family family' 'buy recommendations';
  }
  .evolution-rail {
    flex-direction: row;
  }
  .evolution-rail a {
    width: 76px;
  }
  .profile-spine {
    display: none;
  }
  .profile-art > img {
    width: 110%;
    height: 105%;
  }
  .profile-stage .recommendation-thumbnails {
    align-self: end;
  }
}
@media (max-width: 600px) {
  .profile-stage {
    grid-template-columns: minmax(0, 1fr);
    grid-template-areas: 'heading' 'art' 'buy' 'recommendations';
    gap: 12px;
    padding: 20px;
  }
  .profile-stage:has(.evolution-rail) {
    grid-template-areas: 'heading' 'art' 'family' 'buy' 'recommendations';
  }
  .profile-heading h1 {
    font-size: clamp(2.5rem, 12vw, 4rem);
  }
  .profile-description {
    margin: 10px 0;
  }
  .profile-art {
    min-height: clamp(215px, 62vw, 320px);
  }
  .profile-art > img {
    width: 100%;
    height: 100%;
  }
  .profile-number {
    font-size: clamp(7rem, 34vw, 12rem);
  }
  .profile-stage .recommendation-thumbnails {
    max-width: none;
  }
  .profile-record .pokemon-facts {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

/* Keep the product navigation, information and controls on the same lit set. */
.main-content:has(.pokemon-profile) {
  width: 100%;
  padding: 0;
}
.pokemon-profile {
  --scene-light: oklch(from var(--pokemon-tint) 68% 0.19 h);
  --scene-hot: oklch(from var(--pokemon-tint) 76% 0.19 h);
}
.pokemon-profile[data-type='fuego'] {
  --scene-light: #d8500c;
  --scene-hot: #ff801b;
}
.profile-stage {
  --accent: var(--scene-hot);
  border-radius: 0;
  background:
    radial-gradient(
      ellipse at 52% 91%,
      color-mix(in srgb, var(--scene-hot) 24%, transparent),
      transparent 26%
    ),
    radial-gradient(ellipse at 52% -18%, var(--scene-hot) 4%, transparent 66%),
    linear-gradient(
      175deg,
      var(--scene-light) 0%,
      color-mix(in srgb, var(--scene-light) 56%, #221723) 32%,
      #171419 68%,
      #0b0c10 96%
    );
}
.scene-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #fff4e8;
  font-size: 0.72rem;
  min-height: 32px;
  text-decoration: none;
  grid-area: back;
}
.profile-number {
  left: -52%;
  bottom: -2%;
  transform: none;
  font-family: system-ui, sans-serif;
  font-size: clamp(12rem, 30cqw, 32rem);
  font-weight: 950;
  color: #ffffff09;
}
.profile-record {
  grid-area: facts;
  align-self: start;
  padding: 12px 0;
  border: 0;
  z-index: 1;
}
.profile-record .pokemon-facts {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.profile-record dt,
.profile-record dd {
  color: #f7e8de;
  font-size: 0.72rem;
  margin: 0;
}
.profile-record dt {
  opacity: 0.78;
}
.profile-record dt svg {
  width: 13px;
  height: 13px;
}
.detail-purchase {
  align-self: start;
  padding: 0;
}
.price-slip .detail-price,
.detail-purchase .catalog-purchase strong {
  font: 750 clamp(1.55rem, 2.8vw, 2.8rem) / 1.08 var(--font-body);
  letter-spacing: -0.055em;
}
.profile-heading h1 {
  font-family: var(--font-body);
  font-weight: 900;
  font-size: clamp(1.65rem, 3cqw, 3.5rem);
  letter-spacing: -0.055em;
}
.profile-description {
  color: #fff0e4;
  font-size: clamp(0.79rem, 1.03vw, 1rem);
  line-height: 1.52;
}
.profile-stats .stats-trigger {
  border-radius: 24px;
  font-size: 0.76rem;
}
.profile-art > img {
  filter: drop-shadow(0 25px 20px #08070ec0) drop-shadow(0 0 16px #ffdfaf20);
}
.evolution-rail {
  z-index: 1;
  gap: 14px;
}
.evolution-rail a {
  position: relative;
  border-radius: 5px;
}
.evolution-rail a span {
  font: 600 0.65rem/1.2 var(--font-body);
}
@media (min-width: 901px) {
  .app-shell:has(.pokemon-profile) > .site-header {
    position: absolute;
    inset: 0 0 auto;
    z-index: 5;
    background: transparent;
    border: 0;
    box-shadow: none;
  }
  .app-shell:has(.pokemon-profile) .header-inner {
    width: min(1470px, 90%);
    height: 80px;
  }
  .app-shell:has(.pokemon-profile) .station-brand,
  .app-shell:has(.pokemon-profile) .channel-logo,
  .app-shell:has(.pokemon-profile) .catalog-link {
    color: white;
  }
  .profile-stage,
  .profile-stage:has(.evolution-rail) {
    min-height: 580px;
    padding: 96px max(3.2vw, calc((100vw - 1500px) / 2)) 5vh;
    /* Equal side tracks keep every species on the viewport centerline. */
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.9fr) minmax(0, 1fr);
    grid-template-rows: auto 1fr auto auto;
    grid-template-areas: 'back heading stats' 'family art buy' 'number art recommendations' 'facts art recommendations';
    column-gap: clamp(9px, 1.4vw, 26px);
    row-gap: 12px;
  }
  .scene-back {
    align-self: start;
  }
  .profile-spine {
    grid-area: family;
    justify-self: end;
    margin-inline-end: 6%;
    font:
      950 clamp(4.6rem, 8.8vw, 10rem) / 0.82 system-ui,
      sans-serif;
    letter-spacing: -0.09em;
  }
  .profile-heading {
    text-align: center;
    justify-self: center;
    width: min(100%, 60ch);
  }
  .profile-heading .profile-description {
    margin: 12px auto;
    text-wrap: pretty;
  }
  .profile-stats .stats-trigger {
    margin-top: 0;
  }
  .profile-heading .type-list {
    justify-content: center;
    margin-top: 8px;
  }
  .evolution-rail {
    justify-self: start;
    width: clamp(58px, 5.5vw, 82px);
    align-self: center;
    padding: 2px;
  }
  .evolution-rail img {
    height: clamp(42px, 5vw, 76px);
  }
  .profile-art > img {
    width: 100%;
    height: 100%;
    max-height: 90svh;
    object-position: center;
  }
  .profile-number {
    grid-area: number;
    position: static;
    justify-self: start;
    align-self: end;
    transform: none;
    font-size: clamp(3rem, 8cqw, 8rem);
    color: #ffffff30;
  }
  .detail-purchase {
    align-self: center;
    margin-bottom: 8px;
  }
  .profile-record {
    align-self: end;
    border-top: 1px solid #ffffff38;
    padding-block: 16px 0;
  }
  .profile-record .pokemon-facts {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
  .profile-record dd {
    font-size: clamp(0.85rem, 1.2vw, 1.2rem);
  }
  .profile-stage .recommendation-thumbnails {
    max-width: none;
  }
}
@media (min-width: 601px) and (max-width: 900px) {
  .profile-stage {
    grid-template-areas: 'back back' 'heading art' 'stats art' 'buy facts' 'recommendations recommendations';
  }
  .profile-stage:has(.evolution-rail) {
    grid-template-areas: 'back back' 'heading art' 'stats art' 'family family' 'buy facts' 'recommendations recommendations';
  }
}
@media (max-width: 600px) {
  .profile-stage {
    grid-template-areas: 'back' 'heading' 'stats' 'art' 'buy' 'facts' 'recommendations';
  }
  .profile-stage:has(.evolution-rail) {
    grid-template-areas: 'back' 'heading' 'stats' 'art' 'family' 'buy' 'facts' 'recommendations';
  }
  .profile-number {
    left: 0;
    font-size: 35cqw;
  }
  .profile-heading h1 {
    font-size: 2.5rem;
  }
}

.app-shell:has(.pokemon-profile) {
  background: #0b0c10;
}
.app-shell:has(.pokemon-profile) .main-content {
  flex: 1 0 auto;
  display: grid;
}
.main-content > .pokemon-profile {
  display: grid;
}
.app-shell:has(.pokemon-profile) .site-footer {
  width: 100%;
  margin: 0;
  padding: 16px max(3.2vw, calc((100vw - 1500px) / 2));
  background: #0b0c10;
  color: #d1c8c4;
  border: 0;
  align-items: center;
}
.app-shell:has(.pokemon-profile) .site-footer :is(strong, p, a) {
  color: inherit;
  margin: 0;
}
.app-shell:has(.pokemon-profile) .site-footer strong {
  font-size: 1.05rem;
}
.app-shell:has(.pokemon-profile)
  .station-tools
  :is(.custom-select, .pokemon-switch, .user-link, .cart-preview-trigger, .cart-count) {
  background: transparent;
  box-shadow: none;
  border-color: currentColor;
  color: inherit;
}
.app-shell:has(.pokemon-profile) .station-tools .switch-thumb {
  background: #ffffff38;
  box-shadow: inset 0 0 0 1px currentColor;
}
@media (min-width: 901px) {
  .app-shell:has(.pokemon-profile) .station-tools {
    color: white;
  }
  .app-shell:has(.pokemon-profile)
    .station-tools
    :is(.custom-select, .user-link, .cart-preview-trigger) {
    border-color: transparent;
  }
  .profile-art {
    min-height: 370px;
  }
}
.profile-abilities {
  width: 100%;
  border-top: 1px solid #ffffff38;
  padding-top: 14px;
  margin-top: 8px;
}
.profile-abilities h2 {
  margin: 0;
  color: var(--profile-muted);
  font: 750 0.72rem/1.4 var(--font-mono);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.profile-abilities ul {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  display: grid;
  gap: 6px;
}
.profile-abilities li {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 8px;
  font-weight: 650;
}
.profile-abilities small {
  color: var(--profile-muted);
  font-size: 0.72rem;
  font-weight: 400;
}
.trainer-price-label {
  font: 750 0.72rem/1 var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.trainer-balance {
  margin: 0;
  color: var(--profile-muted);
  font-size: 0.8rem;
}
</style>
