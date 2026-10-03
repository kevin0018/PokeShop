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
import { useAdventureStore } from './adventure/store'

const cart = useCartStore()
const game = useAdventureStore()
onMounted(() => {
  void cart.hydrate()
  void game.load()
})
</script>

<template>
  <div class="app-shell" :class="{ 'battle-focused': game.battleFocused }">
    <a class="skip-link" href="#contenido">{{ t('skip') }}</a>
    <BaseHeader v-if="!game.battleFocused" />
    <main id="contenido" class="main-content" :class="{ 'home-main': route.path === '/' }">
      <RouterView />
    </main>
    <CartNotice
      v-if="!game.battleFocused"
      :message="cart.notice"
      :event="cart.noticeEvent"
      @dismiss="cart.dismissNotice"
    />
    <p v-if="cart.storageWarning && !game.battleFocused" class="storage-warning" role="alert">
      {{ cart.storageWarning }}
    </p>
    <BaseFooter v-if="!game.battleFocused" />
  </div>
</template>
