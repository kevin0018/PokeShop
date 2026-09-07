<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Plus, ArrowRight } from 'lucide-vue-next'
import { useCatalogStore } from '../application/catalogStore'
import { useCartStore } from '@/cart/application/cartStore'
import { money, number, typeName } from '@/shared/presentation/format'
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
  <RouterLink class="back-link" to="/"><ArrowLeft :size="16" /> Volver al catálogo</RouterLink>
  <p v-if="catalog.loading" class="state-box" role="status">Cargando Pokémon…</p>
  <div v-else-if="catalog.error" class="state-box" role="alert">
    <p>{{ catalog.error }}</p>
    <button class="button primary" @click="catalog.load">Volver a intentar</button>
  </div>
  <section v-else-if="pokemon" class="detail-layout">
    <div class="detail-art">
      <span class="dex-number">{{ number(pokemon.id) }}</span
      ><PokemonImage :src="pokemon.image_url" :name="pokemon.name" />
    </div>
    <div class="detail-copy">
      <p class="eyebrow">COLECCIÓN KANTO · {{ number(pokemon.id) }}</p>
      <h1>{{ pokemon.name }}</h1>
      <div class="type-list">
        <span v-for="type in pokemon.types" :key="type" class="type-tag" :data-type="type">{{
          typeName(type)
        }}</span>
      </div>
      <p class="description">{{ pokemon.description }}</p>
      <p class="detail-price">{{ money(pokemon.price_cents) }}</p>
      <p class="stock-label">
        {{ pokemon.stock ? `${pokemon.stock} unidades disponibles` : 'Agotado por ahora' }}
      </p>
      <button
        class="button primary"
        :disabled="inCart >= pokemon.stock"
        @click="cart.add(pokemon.id)"
      >
        <Plus :size="19" />
        {{
          !pokemon.stock
            ? 'Agotado'
            : inCart >= pokemon.stock
              ? 'Máximo disponible en el carrito'
              : 'Añadir al carrito'
        }}</button
      ><RouterLink v-if="inCart" class="back-link" to="/carrito"
        >Ver carrito ({{ inCart }}) <ArrowRight :size="16"
      /></RouterLink>
      <p class="demo-note">
        Catálogo de demostración. Los precios y la disponibilidad son ficticios. No se realizan
        compras reales.
      </p>
    </div>
  </section>
  <div v-else class="state-box">
    <h1>Pokémon no encontrado</h1>
    <p>Este Pokémon no está en nuestra colección.</p>
    <RouterLink class="button primary" to="/">Explorar el catálogo</RouterLink>
  </div>
</template>
