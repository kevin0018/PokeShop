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
  container-type: inline-size;
  border: 1px solid color-mix(in srgb, var(--pokemon-tint) 36%, #27242b);
  border-radius: 12px;
  background: #19171c;
  color: #fff8f1;
}
.catalog-grid .card-art {
  background:
    radial-gradient(
      ellipse at 50% -35%,
      oklch(from var(--pokemon-tint) 67% 0.17 h),
      transparent 82%
    ),
    linear-gradient(160deg, color-mix(in srgb, var(--pokemon-tint) 50%, #201923), #19171c 90%);
}
.catalog-grid .card-art img {
  z-index: 1;
  filter: drop-shadow(0 8px 7px #120d165c);
}
.catalog-grid .card-art .dex-number {
  top: auto;
  bottom: 0;
  left: 6px;
  font: 900 clamp(2.6rem, 17cqi, 7.4rem) / 0.9 var(--font-body);
  letter-spacing: -0.075em;
  padding: 0;
  background: transparent;
  color: #ffffff32;
  z-index: 0;
}
.catalog-grid .card-open {
  top: 9px;
  right: 9px;
  bottom: auto;
  color: white;
  background: #1c161d70;
  border: 1px solid #ffffff4a;
}
.catalog-grid .sold-out {
  z-index: 2;
}
.catalog-grid h3 {
  color: inherit;
  font-family: var(--font-body);
  font-weight: 800;
  letter-spacing: -0.045em;
  margin-block: 5px;
}
.catalog-grid .card-measures,
.catalog-grid .purchase-unavailable {
  color: #d4cbd1;
}
.catalog-grid .card-bottom {
  border-color: #ffffff29;
}
.catalog-grid .card-bottom strong {
  color: #fff8f1;
  font: 750 clamp(0.96rem, 1.5vw, 1.22rem) / 1.2 var(--font-body);
}
.catalog-grid .add-button {
  border-radius: 99px;
  background: var(--pokemon-tint);
  color: #18141b;
}
.catalog-grid .add-button:hover:not(:disabled) {
  background: color-mix(in srgb, var(--pokemon-tint) 78%, white);
}
.catalog-grid .image-fallback {
  color: white;
}
/* Wide tiles keep the artwork beside the offer, even when labels wrap. */
@container (min-width: 270px) {
  .catalog-grid .card-body h3 {
    font-size: clamp(1.5rem, 6cqi, 2.5rem);
  }
}
@media (min-width: 801px) {
  .bento-block[data-count='6'] > :first-child {
    grid-template-rows: minmax(200px, 1fr) auto auto;
  }
  .bento-block[data-count='6'] > :first-child .card-art {
    aspect-ratio: auto;
  }
  .bento-block[data-count='6'] > :first-child .card-art img {
    position: absolute;
    width: 85%;
    height: 92%;
  }
  .bento-block[data-count='6'] > :is(:nth-child(2), :nth-child(3)),
  .bento-block[data-count='1'] > article {
    grid-template-rows: auto 1fr;
    --art-ratio: auto;
    --art-rows: 2;
    --art-min-height: clamp(165px, 17vw, 214px);
    --tile-columns: minmax(0, 1fr) minmax(0, 1.15fr);
  }
}
@media (max-width: 800px) {
  .bento-block[data-count='6'] > :is(:first-child, :last-child),
  .bento-block:is([data-count='1'], [data-count='3'], [data-count='5']) > :first-child {
    grid-template-rows: auto 1fr;
    --art-ratio: auto;
    --art-rows: 2;
    --art-min-height: clamp(165px, 17vw, 214px);
    --tile-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  }
}
.bento-block .illustrated-card {
  grid-template-columns: var(--tile-columns, minmax(0, 1fr));
}
.bento-block .card-art {
  min-height: var(--art-min-height, 0);
  aspect-ratio: var(--art-ratio, 1.48);
  grid-row: 1 / span var(--art-rows, 1);
}
@media (prefers-reduced-motion: reduce) {
  .catalog-grid .card-art img {
    transition: none;
    transform: none;
  }
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
