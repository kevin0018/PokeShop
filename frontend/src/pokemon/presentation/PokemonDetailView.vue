<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Plus, ArrowRight } from 'lucide-vue-next'
import { useCatalogStore } from '../application/catalogStore'
import { useCartStore } from '@/cart/application/cartStore'
import { money, number, typeName, description } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
const route = useRoute()
const catalog = useCatalogStore()
const cart = useCartStore()
const pokemon = computed(() => catalog.items.find((item) => item.id === Number(route.params.id)))
const inCart = computed(
  () => cart.lines.find((line) => line.pokemon.id === pokemon.value?.id)?.quantity ?? 0,
)
</script>
<template>
  <RouterLink class="back-link" to="/"><ArrowLeft :size="16" />{{ t('backCatalog') }}</RouterLink>
  <p v-if="catalog.loading" class="state-box" role="status">{{ t('loadingPokemon') }}</p>
  <div v-else-if="catalog.error" class="state-box" role="alert">
    <p>{{ t(catalog.error) }}</p>
    <button class="button primary" @click="catalog.load">{{ t('retry') }}</button>
  </div>
  <section v-else-if="pokemon" class="detail-layout">
    <div class="detail-art">
      <span class="dex-number">{{ number(pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemon.name" />
    </div>
    <div class="detail-copy">
      <p class="eyebrow">{{ t('collection') }} · {{ number(pokemon.id) }}</p>
      <h1>{{ pokemon.name }}</h1>
      <div class="type-list">
        <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
          typeName(type)
        }}</span>
      </div>
      <p class="description">{{ description(pokemon) }}</p>
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
    </div>
  </section>
  <div v-else class="state-box">
    <h1>{{ t('pokemonMissing') }}</h1>
    <p>{{ t('pokemonMissingBody') }}</p>
    <RouterLink class="button primary" to="/">{{ t('exploreCatalog') }}</RouterLink>
  </div>
</template>
