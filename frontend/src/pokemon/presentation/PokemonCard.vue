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
  <article class="pokemon-card">
    <RouterLink
      :to="`/pokemon/${pokemon.id}`"
      class="card-art"
      :aria-label="t('viewPokemon', { name: pokemonName(pokemon) })"
    >
      <span class="dex-number">{{ number(pokemon.species_id ?? pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemonName(pokemon)" />
      <span v-if="!pokemon.stock" class="sold-out">{{ t('soldOut') }}</span>
    </RouterLink>
    <div class="card-body">
      <div class="type-list">
        <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
          typeName(type)
        }}</span>
      </div>
      <h3>
        <RouterLink :to="`/pokemon/${pokemon.id}`">{{ pokemonName(pokemon) }}</RouterLink>
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
          <Plus :size="18" />{{ t('add') }}
        </button>
      </div>
    </div>
  </article>
</template>
