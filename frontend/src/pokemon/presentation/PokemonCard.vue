<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Plus } from 'lucide-vue-next'
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
  aspect-ratio: 1.35;
  background:
    radial-gradient(circle closest-side, var(--surface) 0 73%, transparent 74%),
    color-mix(in srgb, var(--pokemon-tint) 30%, var(--surface));
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
  font-size: clamp(0.98rem, 1.7vw, 1.28rem);
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
}

.illustrated-card .card-bottom {
  margin-top: auto;
  padding-top: 10px;
}

.illustrated-card .card-bottom strong {
  font-size: clamp(0.85rem, 1.3vw, 1rem);
}

.illustrated-card .add-button {
  width: auto;
  min-width: 44px;
  min-height: 44px;
  padding: 5px 8px;
  border-radius: 8px;
}

.illustrated-card .catalog-purchase .add-label {
  overflow-wrap: anywhere;
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
