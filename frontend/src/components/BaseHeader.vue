<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Gamepad2, House, Store, TvMinimalPlay } from 'lucide-vue-next'
import CartPreview from '@/cart/presentation/CartPreview.vue'
import PreferencesControls from './PreferencesControls.vue'
import UserMenu from './UserMenu.vue'
const { t } = useI18n()
</script>
<template>
  <header class="site-header station-header">
    <div class="header-inner">
      <RouterLink class="station-brand" to="/" :aria-label="t('home')">
        <TvMinimalPlay class="channel-logo" :size="35" :stroke-width="2.5" aria-hidden="true" />
        <span>PokéShop</span><b>TV</b>
      </RouterLink>
      <nav :aria-label="t('navigation')">
        <RouterLink to="/" class="catalog-link"><House :size="15" />{{ t('homeNav') }}</RouterLink>
        <RouterLink to="/catalogo" class="catalog-link"
          ><Store :size="15" />{{ t('catalog') }}</RouterLink
        >
        <RouterLink to="/aventura" class="catalog-link"
          ><Gamepad2 :size="16" />{{ t('adventure.nav') }}</RouterLink
        >
      </nav>
      <div class="station-tools"><PreferencesControls /><UserMenu /><CartPreview /></div>
    </div>
  </header>
</template>
