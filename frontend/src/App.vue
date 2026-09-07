<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { RouterView, useRoute } from 'vue-router'
const route = useRoute()
import BaseHeader from './components/BaseHeader.vue'
import CartNotice from './cart/presentation/CartNotice.vue'
import BaseFooter from './components/BaseFooter.vue'
import { onMounted } from 'vue'

import { useCartStore } from './cart/application/cartStore'

const cart = useCartStore()
onMounted(() => {
  void cart.hydrate()
})
</script>

<template>
  <div class="app-shell">
    <a class="skip-link" href="#contenido">{{ t('skip') }}</a>
    <BaseHeader />
    <main id="contenido" class="main-content" :class="{ 'home-main': route.path === '/' }">
      <RouterView />
    </main>
    <CartNotice :message="cart.notice" :event="cart.noticeEvent" @dismiss="cart.dismissNotice" />
    <p v-if="cart.storageWarning" class="storage-warning" role="alert">{{ cart.storageWarning }}</p>
    <BaseFooter />
  </div>
</template>
