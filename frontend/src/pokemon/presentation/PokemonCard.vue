<script setup lang="ts">
import { Plus } from 'lucide-vue-next'
import type { Pokemon } from '../domain/pokemon'
import { useCartStore } from '@/cart/application/cartStore'
import { money, number, typeName } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
defineProps<{ pokemon: Pokemon }>()
const cart = useCartStore()
</script>
<template>
  <article class="pokemon-card">
    <RouterLink :to="`/pokemon/${pokemon.id}`" class="card-art" :aria-label="`Ver ${pokemon.name}`">
      <span class="dex-number">{{ number(pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemon.name" />
      <span v-if="!pokemon.stock" class="sold-out">Agotado</span>
    </RouterLink>
    <div class="card-body">
      <div class="type-list">
        <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
          typeName(type)
        }}</span>
      </div>
      <h3>
        <RouterLink :to="`/pokemon/${pokemon.id}`">{{ pokemon.name }}</RouterLink>
      </h3>
      <div class="card-bottom">
        <strong>{{ money(pokemon.price_cents) }}</strong
        ><button
          class="add-button"
          :disabled="
            !pokemon.stock ||
            (cart.lines.find((line) => line.pokemon.id === pokemon.id)?.quantity ?? 0) >=
              pokemon.stock
          "
          :aria-label="`Añadir ${pokemon.name} al carrito`"
          @click="cart.add(pokemon.id)"
        >
          <Plus :size="18" /> Añadir
        </button>
      </div>
    </div>
  </article>
</template>
