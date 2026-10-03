<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Check } from 'lucide-vue-next'
import type { Pokemon } from '@/pokemon/domain/pokemon'
import { pokemonName } from '@/shared/presentation/format'
import { useAdventureStore } from './store'
import { useCartStore } from '@/cart/application/cartStore'

const props = defineProps<{ pokemon: Pokemon; compact?: boolean }>()
const { t, n } = useI18n()
const game = useAdventureStore()
const cart = useCartStore()
const inCart = computed(() => cart.entries.some((item) => item.id === props.pokemon.id))
const offer = computed(() => game.shop.find((item) => item.id === props.pokemon.id))
const owned = computed(() => game.trainer?.collection.some((item) => item.id === props.pokemon.id))
const label = computed(() => {
  if (!offer.value) return t('adventure.notPlayable')
  if (owned.value) return t('adventure.owned')
  if (inCart.value) return t('adventure.inCart')
  return t('addPokemon', { name: pokemonName(props.pokemon) })
})
</script>

<template>
  <div class="catalog-purchase" :class="{ compact }">
    <strong v-if="offer">{{ t('adventure.credits', { amount: n(offer.price) }) }}</strong>
    <span v-else class="purchase-unavailable">{{ t('adventure.notPlayable') }}</span>
    <button
      v-if="offer"
      :class="compact ? 'add-button' : 'button primary'"
      :disabled="game.busy || owned || inCart"
      :aria-label="label"
      :title="label"
      @click="cart.add(pokemon.id)"
    >
      <Check v-if="owned || inCart" :size="18" /><Plus v-else :size="18" />
      <span :class="{ 'add-label': compact }">{{ label }}</span>
    </button>
  </div>
</template>

<style>
.catalog-purchase {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}
.catalog-purchase.compact {
  width: 100%;
  justify-content: space-between;
}
.purchase-unavailable {
  color: var(--muted-strong);
  font-size: 12px;
}
.catalog-purchase .add-button {
  min-height: 44px;
}
</style>
