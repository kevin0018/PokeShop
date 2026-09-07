<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
<template>
  <section class="state-box">
    <p class="eyebrow">404</p>
    <h1>{{ t('notFound') }}</h1>
    <p>{{ t('notFoundBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('backCatalog') }}</RouterLink>
  </section>
</template>
