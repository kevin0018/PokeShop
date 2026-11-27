<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
<template>
  <footer class="site-footer">
    <div>
      <strong>PokéShop TV</strong>
      <p>{{ t('studio.channel') }}</p>
    </div>
    <p>
      {{ t('footerDemo') }}<br />{{ t('attribution') }}&nbsp;<a
        href="https://github.com/PokeAPI/sprites"
        target="_blank"
        rel="noopener noreferrer"
        >PokéAPI</a
      >.
    </p>
  </footer>
</template>
