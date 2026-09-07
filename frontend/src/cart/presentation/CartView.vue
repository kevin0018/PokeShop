<script setup lang="ts">
import { ArrowLeft, Minus, Plus, Trash2, ShoppingBag } from 'lucide-vue-next'
import { useCartStore } from '../application/cartStore'
import { useCatalogStore } from '@/pokemon/application/catalogStore'
import { money, number } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
const cart = useCartStore()
const catalog = useCatalogStore()
</script>
<template>
  <RouterLink class="back-link" to="/"><ArrowLeft :size="16" /> Seguir explorando</RouterLink>
  <div class="section-heading">
    <div>
      <p class="eyebrow">TU SELECCIÓN</p>
      <h1>Mi carrito</h1>
    </div>
    <span>{{ cart.count }} {{ cart.count === 1 ? 'unidad' : 'unidades' }}</span>
  </div>
  <p v-if="catalog.loading" role="status" class="state-box">Cargando tu selección…</p>
  <div v-else-if="catalog.error" role="alert" class="state-box">
    <p>{{ catalog.error }}</p>
    <button class="button primary" @click="catalog.load">Volver a intentar</button>
  </div>
  <div v-else-if="!cart.lines.length" class="state-box empty-cart">
    <ShoppingBag :size="44" />
    <h2>Tu equipo está por descubrir</h2>
    <p>Añade tus favoritos del catálogo y los guardaremos aquí.</p>
    <RouterLink class="button primary" to="/">Explorar Pokémon</RouterLink>
  </div>
  <div v-else class="cart-layout">
    <div class="cart-lines">
      <article v-for="line in cart.lines" :key="line.pokemon.id" class="cart-line">
        <RouterLink :to="`/pokemon/${line.pokemon.id}`" class="cart-art"
          ><PokemonImage :src="line.pokemon.image_url" :name="line.pokemon.name"
        /></RouterLink>
        <div class="cart-item-copy">
          <span class="dex-number">{{ number(line.pokemon.id) }}</span>
          <h2>
            <RouterLink :to="`/pokemon/${line.pokemon.id}`">{{ line.pokemon.name }}</RouterLink>
          </h2>
          <p>{{ money(line.pokemon.price_cents) }} / unidad</p>
          <div class="quantity-control">
            <button
              :aria-label="`Reducir cantidad de ${line.pokemon.name}`"
              :disabled="line.quantity === 1"
              @click="cart.setQuantity(line.pokemon.id, line.quantity - 1)"
            >
              <Minus :size="15" /></button
            ><span :aria-label="`Cantidad de ${line.pokemon.name}`">{{ line.quantity }}</span
            ><button
              :aria-label="`Aumentar cantidad de ${line.pokemon.name}`"
              :disabled="line.quantity >= line.pokemon.stock"
              @click="cart.setQuantity(line.pokemon.id, line.quantity + 1)"
            >
              <Plus :size="15" />
            </button>
          </div>
        </div>
        <div class="cart-line-total">
          <strong>{{ money(line.pokemon.price_cents * line.quantity) }}</strong
          ><button
            class="text-button"
            :aria-label="`Eliminar ${line.pokemon.name}`"
            @click="cart.remove(line.pokemon.id)"
          >
            <Trash2 :size="16" /> Eliminar
          </button>
        </div>
      </article>
    </div>
    <aside class="cart-summary">
      <h2>Tu selección, de un vistazo</h2>
      <div>
        <span>Subtotal ({{ cart.count }} {{ cart.count === 1 ? 'unidad' : 'unidades' }})</span
        ><strong>{{ money(cart.total) }}</strong>
      </div>
      <div class="summary-total">
        <span>Total</span><strong>{{ money(cart.total) }}</strong>
      </div>
      <p>
        Tu carrito se guarda en este navegador para que puedas seguir explorando cuando quieras.
      </p>
      <p class="demo-note">
        Esta es una tienda de demostración. Los pedidos y pagos todavía no están disponibles.
      </p>
      <RouterLink class="button secondary" to="/">Seguir explorando</RouterLink>
    </aside>
  </div>
</template>
