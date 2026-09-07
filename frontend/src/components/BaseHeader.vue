<script setup lang="ts">
import { ShoppingBag } from 'lucide-vue-next'
import { useCartStore } from '@/cart/application/cartStore'
const cart = useCartStore()
</script>
<template>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/" aria-label="PokeShop, inicio"
        ><span class="pokeball" aria-hidden="true"></span>poké<span>shop</span
        ><span class="brand-dot">.</span></RouterLink
      >
      <nav aria-label="Navegación principal">
        <RouterLink to="/" class="catalog-link">Catálogo</RouterLink
        ><RouterLink to="/carrito" class="cart-link"
          ><ShoppingBag :size="19" /><span>Mi carrito</span
          ><span class="cart-count">{{ cart.count }}</span></RouterLink
        >
      </nav>
    </div>
  </header>
</template>
