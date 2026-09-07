<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import CartPreview from '@/cart/presentation/CartPreview.vue'
import PreferencesControls from './PreferencesControls.vue'
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
        ><CartPreview />
      </nav>
      <PreferencesControls />
    </div>
  </header>
</template>
