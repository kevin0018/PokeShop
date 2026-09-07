<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { Plus } from 'lucide-vue-next'
import type { Pokemon } from '../domain/pokemon'
import { useCartStore } from '@/cart/application/cartStore'
import { money, pokemonName, number, typeName, decimal } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
defineProps<{ pokemon: Pokemon; bento?: boolean }>()
const cart = useCartStore()
</script>
<template>
  <article
    class="pokemon-card illustrated-card pokemon-palette"
    :class="{ 'bento-card': bento }"
    :data-type="pokemon.types[0]"
  >
    <RouterLink
      :to="`/pokemon/${pokemon.id}`"
      class="card-art"
      :aria-label="t('viewPokemon', { name: pokemonName(pokemon) })"
    >
      <span class="dex-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
      <span v-if="!pokemon.stock" class="sold-out">{{ t('soldOut') }}</span>
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
      <p v-if="bento" class="card-measures">
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
      </div>
    </div>
  </article>
</template>

<style>
.illustrated-card.pokemon-card {
  position: relative;
  isolation: isolate;
  height: 300px;
  border-radius: 20px;
  overflow: hidden;
  background:
    radial-gradient(
      ellipse at 70% 20%,
      color-mix(in srgb, var(--pokemon-tint) 26%, transparent),
      transparent 70%
    ),
    var(--surface);
  border: 1px solid var(--line);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.illustrated-card .card-art {
  position: absolute;
  inset: 0;
  height: 100%;
  background: none;
  z-index: 0;
}
.illustrated-card .card-art:before {
  content: '';
  position: absolute;
  width: 180px;
  height: 180px;
  border: 1px solid color-mix(in srgb, var(--pokemon-tint) 25%, transparent);
  border-radius: 50%;
  right: 10%;
  top: 2%;
  transform: rotate(-20deg);
}
.illustrated-card .card-art img {
  position: absolute;
  width: 85%;
  height: 66%;
  left: 7.5%;
  top: 0;
  object-fit: contain;
  filter: drop-shadow(0 10px 7px #0002);
  transition: transform 0.25s;
}
.illustrated-card .card-art:hover img {
  transform: translateY(-3px) scale(1.03);
}
.illustrated-card .card-art .dex-number {
  left: auto;
  right: 14px;
  top: 12px;
  z-index: 2;
}
.illustrated-card .sold-out {
  top: 35px;
  bottom: auto;
  right: 12px;
}
.illustrated-card .card-body {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 16px;
  pointer-events: none;
  background: linear-gradient(transparent, color-mix(in srgb, var(--surface) 94%, transparent) 48%);
  z-index: 1;
}
.illustrated-card .card-body a,
.illustrated-card .card-body button {
  pointer-events: auto;
}
.illustrated-card h3 {
  font-size: 1.05rem;
  line-height: 1.2;
  margin: 6px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.illustrated-card .type-list {
  gap: 4px;
}
.illustrated-card .type-tag {
  font-size: 9px;
  padding: 2px 5px;
}
.illustrated-card .card-bottom {
  margin-top: 8px;
  gap: 8px;
}
.illustrated-card .card-bottom strong {
  font-size: 0.95rem;
}
.illustrated-card .add-button {
  min-width: 44px;
  min-height: 44px;
  padding: 6px 9px;
  border-radius: 50%;
  gap: 0;
}
.illustrated-card .add-label {
  display: none;
}
.illustrated-card .card-measures {
  font-size: 0.65rem;
  color: var(--muted-strong);
  display: flex;
  flex-wrap: wrap;
  gap: 2px 10px;
  margin: 6px 0 0;
  line-height: 1.3;
}
.bento-block .illustrated-card {
  height: auto;
  min-height: 0;
}
.bento-block .illustrated-card .card-art img {
  height: 82%;
  width: 72%;
  left: 24%;
  top: 0;
}
.bento-block .illustrated-card .card-body {
  padding: 14px 18px;
}
.bento-block .illustrated-card .type-list {
  position: absolute;
  bottom: calc(100% + 38px);
  left: 18px;
  max-width: 90px;
}
.bento-block .illustrated-card .card-body {
  background: linear-gradient(transparent, color-mix(in srgb, var(--surface) 96%, transparent) 50%);
}
@media (max-width: 900px) {
  .bento-block .illustrated-card .card-art img {
    width: 85%;
    height: 73%;
    left: 12%;
    top: 0;
  }
  .bento-block .illustrated-card .type-list {
    bottom: calc(100% + 55px);
  }
}
@media (prefers-reduced-motion: reduce) {
  .illustrated-card .card-art img {
    transition: none;
  }
  .illustrated-card .card-art:hover img {
    transform: none;
  }
}

.illustrated-card > .type-list,
.bento-block .illustrated-card > .type-list {
  position: absolute;
  top: 14px;
  left: 18px;
  bottom: auto;
  z-index: 2;
  max-width: calc(100% - 76px);
}
@media (min-width: 901px) {
  .bento-block[data-count='6'] > .pokemon-card:nth-child(2) .card-body,
  .bento-block[data-count='6'] > .pokemon-card:nth-child(3) .card-body {
    background: none;
  }
}
</style>
