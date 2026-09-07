<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { RouterView } from 'vue-router'
import BaseHeader from './components/BaseHeader.vue'
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
    <main id="contenido" class="main-content">
      <RouterView />
    </main>
    <p v-if="cart.notice" class="cart-notice" role="status">
      {{ cart.notice }}
      <button :aria-label="t('close')" @click="cart.dismissNotice()">×</button>
    </p>
    <p v-if="cart.storageWarning" class="storage-warning" role="alert">{{ cart.storageWarning }}</p>
    <BaseFooter />
  </div>
</template>
