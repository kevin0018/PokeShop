<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Plus, ArrowUpRight } from 'lucide-vue-next'
import type { Pokemon } from '../domain/pokemon'
import { useCartStore } from '@/cart/application/cartStore'
import { money, pokemonName, number, typeName, decimal } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
import CatalogPurchase from '@/adventure/CatalogPurchase.vue'
import { useAdventureStore } from '@/adventure/store'
defineProps<{ pokemon: Pokemon; showMeasures?: boolean }>()
const cart = useCartStore()
const game = useAdventureStore()
</script>
<template>
  <article class="pokemon-card illustrated-card pokemon-palette" :data-type="pokemon.types[0]">
    <RouterLink
      :to="`/pokemon/${pokemon.id}`"
      class="card-art"
      :aria-label="t('viewPokemon', { name: pokemonName(pokemon) })"
    >
      <span class="dex-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
      <ArrowUpRight class="card-open" :size="18" aria-hidden="true" />
      <span v-if="!game.trainer && !pokemon.stock" class="sold-out">{{ t('soldOut') }}</span>
    </RouterLink>
    <div class="type-list">
      <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
        typeName(type)
      }}</span>
    </div>
    <div class="card-body">
      <h3>
        <RouterLink :to="`/pokemon/${pokemon.id}`" :title="pokemonName(pokemon)">{{
          pokemonName(pokemon)
        }}</RouterLink>
      </h3>
      <p v-if="showMeasures" class="card-measures">
        <span
          >{{ t('height') }}:
          {{ pokemon.height_m == null ? t('missingData') : decimal(pokemon.height_m) + ' m' }}</span
        ><span
          >{{ t('weight') }}:
          {{
            pokemon.weight_kg == null ? t('missingData') : decimal(pokemon.weight_kg) + ' kg'
          }}</span
        >
      </p>
      <div class="card-bottom">
        <CatalogPurchase v-if="game.trainer" :pokemon="pokemon" compact />
        <template v-else>
          <strong>{{ money(pokemon.price_cents) }}</strong
          ><button
            class="add-button"
            :disabled="
              !pokemon.stock ||
              (cart.lines.find((line) => line.pokemon.id === pokemon.id)?.quantity ?? 0) >=
                pokemon.stock
            "
            :aria-label="t('addPokemon', { name: pokemonName(pokemon) })"
            @click="cart.add(pokemon.id)"
          >
            <Plus :size="18" /><span class="add-label">{{ t('add') }}</span>
          </button>
        </template>
      </div>
    </div>
  </article>
</template>

<style>
.illustrated-card.pokemon-card {
  display: grid;
  grid-template-rows: auto auto 1fr;
  min-width: 0;
  border-radius: var(--shop-radius);
  overflow: clip;
}

.illustrated-card .card-art {
  position: relative;
  isolation: isolate;
  height: auto;
  aspect-ratio: 1.48;
  background:
    radial-gradient(
      circle at center,
      transparent 35%,
      color-mix(in srgb, var(--surface) 65%, transparent) 35.5% 36%,
      transparent 36.5% 43%,
      color-mix(in srgb, var(--surface) 65%, transparent) 43.5% 44%,
      transparent 44.5%
    ),
    radial-gradient(color-mix(in srgb, var(--pokemon-tint) 48%, transparent) 1px, transparent 1px) 0
      0 / 8px 8px,
    color-mix(in srgb, var(--pokemon-tint) 47%, var(--surface));
}

.card-open {
  position: absolute;
  bottom: 9px;
  right: 9px;
  color: var(--ink);
  background: var(--surface);
  border-radius: 50%;
  padding: 4px;
  width: 25px;
  height: 25px;
}
.illustrated-card .card-art:focus-visible {
  outline-offset: -4px;
}

.illustrated-card .card-art img {
  width: 68%;
  height: 85%;
  object-fit: contain;
  filter: drop-shadow(0 8px 7px var(--shop-shadow));
}

.illustrated-card .dex-number,
.illustrated-card .sold-out {
  z-index: 1;
  border-radius: 4px;
  padding: 2px 5px;
  color: var(--ink);
  background: var(--surface);
}

.illustrated-card .card-art .dex-number {
  left: 8px;
  top: 8px;
}

.illustrated-card .sold-out {
  right: 8px;
  bottom: 8px;
}

.illustrated-card > .type-list {
  align-content: start;
  gap: 4px;
  padding: 12px var(--card-inset) 0;
}

.illustrated-card .card-body {
  display: flex;
  flex-direction: column;
  padding: 0 var(--card-inset) var(--card-inset);
}

.illustrated-card h3 {
  font: 900 clamp(1.4rem, 2.1vw, 1.9rem) / 1.12 var(--font-display);
  line-height: 1.16;
  margin: 8px 0 6px;
  overflow-wrap: anywhere;
}

.illustrated-card .card-measures {
  display: flex;
  flex-wrap: wrap;
  gap: 3px 10px;
  color: var(--muted-strong);
  font-size: 0.69rem;
  line-height: 1.45;
  margin-bottom: 8px;
}

.illustrated-card .card-bottom {
  margin-top: auto;
  border-top: 1px solid var(--line);
  padding-top: 8px;
}

.illustrated-card .card-bottom strong {
  font-size: clamp(0.95rem, 1.4vw, 1.16rem);
}

.illustrated-card .add-button {
  width: auto;
  min-width: 44px;
  min-height: 44px;
  padding: 5px 10px;
  background: var(--purple);
  color: var(--on-accent);
  border-color: transparent;
  border-radius: 8px;
}

.illustrated-card .add-button:hover:not(:disabled) {
  background: var(--button-hover);
}
.illustrated-card .catalog-purchase .add-label {
  overflow-wrap: anywhere;
}

.catalog-grid .illustrated-card {
  --specimen-ink: #23372e;
  display: flex;
  flex-direction: column;
  padding: 12px clamp(9px, 1.3vw, 17px) 0;
  border: 0;
  border-top: 5px solid var(--pokemon-tint);
  border-radius: 3px 10px 3px 3px;
  color: var(--specimen-ink);
  background: linear-gradient(115deg, #f5eedc, #dfd9c8);
  box-shadow: 0 5px 12px #09151b44;
}
.catalog-grid .card-body {
  display: contents;
}
.catalog-grid .card-body h3 {
  order: 0;
  margin: 0 0 3px;
  color: inherit;
  font:
    italic clamp(1.35rem, 2.6vw, 2.15rem) / 1.12 Georgia,
    serif;
  letter-spacing: -0.055em;
}
.catalog-grid .type-list {
  order: 1;
  padding: 0 0 10px;
}
.catalog-grid .type-tag {
  padding: 0;
  background: transparent;
  color: var(--specimen-ink);
  font: 700 0.65rem/1.3 var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.catalog-grid .type-tag + .type-tag::before {
  content: '/ ';
}
.catalog-grid .card-art {
  order: 2;
  height: clamp(120px, 17vw, 180px);
  aspect-ratio: auto;
  background:
    radial-gradient(
      ellipse at 49% 60%,
      color-mix(in srgb, var(--pokemon-tint) 35%, transparent),
      transparent 66%
    ),
    repeating-linear-gradient(0deg, transparent 0 17px, #3f503015 17px 18px),
    repeating-linear-gradient(90deg, transparent 0 17px, #3f503015 17px 18px);
}
.catalog-grid .card-art img {
  z-index: 1;
  width: 88%;
  height: 100%;
  filter: drop-shadow(1px 4px 1px #342d202e);
}
.catalog-grid .card-art::after {
  content: '';
  position: absolute;
  right: 0;
  inset-block: 18px 15px;
  width: 7px;
  border-right: 1px solid #687664;
  background: repeating-linear-gradient(to bottom, #687664 0 1px, transparent 1px 12px);
}
.catalog-grid .card-art .dex-number {
  inset: 0 auto auto 0;
  z-index: 0;
  padding: 0;
  background: transparent;
  color: #4b58444d;
  font:
    italic clamp(2.5rem, 5vw, 4.25rem) / 0.95 Georgia,
    serif;
  letter-spacing: -0.08em;
}
.catalog-grid .card-open {
  display: none;
}
.catalog-grid .card-art .sold-out {
  z-index: 2;
}
.catalog-grid .card-measures {
  order: 3;
  justify-content: space-between;
  margin: 0;
  padding: 7px 0;
  color: #45554e;
  font: 0.7rem/1.4 var(--font-mono);
}
.catalog-grid .card-bottom {
  order: 4;
  margin: auto calc(-1 * clamp(9px, 1.3vw, 17px)) 0;
  padding: 6px clamp(9px, 1.3vw, 17px);
  border: 0;
  background: #23332f;
  color: #fff8ee;
  flex-wrap: wrap;
}
.catalog-grid .card-bottom strong,
.catalog-grid .purchase-unavailable {
  color: inherit;
}
.catalog-grid .add-button {
  color: #fff9ec;
  border: 1px solid #83948a;
  border-radius: 5px;
  background: transparent;
}
.catalog-grid .add-button:hover:not(:disabled) {
  background: #40584e;
}
.catalog-grid .card-art:focus-visible {
  outline-color: #324f43;
}
@media (max-width: 700px) {
  .illustrated-card .card-bottom > .add-button .add-label,
  .illustrated-card .catalog-purchase .add-button:not(:disabled) .add-label {
    display: none;
  }

  .illustrated-card .catalog-purchase .add-button:disabled {
    padding-inline: 5px;
    font-size: 0.65rem;
  }

  .illustrated-card .card-bottom {
    gap: 4px;
  }
}
</style>
