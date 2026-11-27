<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
<template>
  <section class="state-box off-air">
    <p class="eyebrow">POKÉSHOP TV · 404</p>
    <h1>{{ t('notFound') }}</h1>
    <p>{{ t('notFoundBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('backCatalog') }}</RouterLink>
  </section>
</template>

<style>
.off-air {
  background: var(--sign);
  color: var(--sign-ink);
  border: 0;
  border-bottom: 5px solid var(--studio-yellow);
}
.off-air p,
.off-air .eyebrow {
  color: var(--sign-label);
}
.off-air h1 {
  font-size: clamp(2.5rem, 6vw, 5rem);
}
.off-air .primary {
  background: var(--studio-yellow);
  color: var(--studio-dark);
}
</style>
