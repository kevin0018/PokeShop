<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ArrowLeft, Minus, Plus, Trash2, ShoppingBag } from 'lucide-vue-next'
import { useCartStore } from '../application/cartStore'
import { useCatalogStore } from '@/pokemon/application/catalogStore'
import { money, number } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
const cart = useCartStore()
const catalog = useCatalogStore()
</script>
<template>
  <RouterLink class="back-link" to="/"><ArrowLeft :size="16" />{{ t('keepExploring') }}</RouterLink>
  <div class="section-heading">
    <div>
      <p class="eyebrow">{{ t('selection') }}</p>
      <h1>{{ t('cart') }}</h1>
    </div>
    <span>{{ t('units', cart.count) }}</span>
  </div>
  <p v-if="catalog.loading" role="status" class="state-box">{{ t('loadingCart') }}</p>
  <div v-else-if="catalog.error" role="alert" class="state-box">
    <p>{{ t(catalog.error) }}</p>
    <button class="button primary" @click="catalog.load">{{ t('retry') }}</button>
  </div>
  <div v-else-if="!cart.lines.length" class="state-box empty-cart">
    <ShoppingBag :size="44" />
    <h2>{{ t('emptyCart') }}</h2>
    <p>{{ t('emptyCartBody') }}</p>
    <RouterLink class="button primary" to="/">{{ t('explore') }}</RouterLink>
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
          <p>{{ t('perUnit', { price: money(line.pokemon.price_cents) }) }}</p>
          <div class="quantity-control">
            <button
              :aria-label="t('decrease', { name: line.pokemon.name })"
              :disabled="line.quantity === 1"
              @click="cart.setQuantity(line.pokemon.id, line.quantity - 1)"
            >
              <Minus :size="15" /></button
            ><span :aria-label="t('quantity', { name: line.pokemon.name })">{{
              line.quantity
            }}</span
            ><button
              :aria-label="t('increase', { name: line.pokemon.name })"
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
            :aria-label="t('removePokemon', { name: line.pokemon.name })"
            @click="cart.remove(line.pokemon.id)"
          >
            <Trash2 :size="16" />{{ t('remove') }}
          </button>
        </div>
      </article>
    </div>
    <aside class="cart-summary">
      <h2>{{ t('summary') }}</h2>
      <div>
        <span>{{ t('subtotal', { units: t('units', cart.count) }) }}</span
        ><strong>{{ money(cart.total) }}</strong>
      </div>
      <div class="summary-total">
        <span>{{ t('total') }}</span
        ><strong>{{ money(cart.total) }}</strong>
      </div>
      <p>{{ t('cartSaved') }}</p>
      <p class="demo-note">{{ t('demoCart') }}</p>
      <RouterLink class="button secondary" to="/">{{ t('keepExploring') }}</RouterLink>
    </aside>
  </div>
</template>
