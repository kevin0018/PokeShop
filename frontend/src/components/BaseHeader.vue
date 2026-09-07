<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ShoppingBag } from 'lucide-vue-next'
import PreferencesControls from './PreferencesControls.vue'
import { useCartStore } from '@/cart/application/cartStore'
const cart = useCartStore()
</script>
<template>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/" :aria-label="t('home')"
        ><span class="pokeball" aria-hidden="true"></span>poké<span>shop</span
        ><span class="brand-dot">.</span></RouterLink
      >
      <nav :aria-label="t('navigation')">
        <RouterLink to="/" class="catalog-link">{{ t('homeNav') }}</RouterLink
        ><RouterLink to="/catalogo" class="catalog-link">{{ t('catalog') }}</RouterLink
        ><RouterLink to="/carrito" class="cart-link"
          ><ShoppingBag :size="19" /><span>{{ t('cart') }}</span
          ><span class="cart-count">{{ cart.count }}</span></RouterLink
        >
      </nav>
      <PreferencesControls />
    </div>
  </header>
</template>
