<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import CartPreview from '@/cart/presentation/CartPreview.vue'
import PreferencesControls from './PreferencesControls.vue'
import { UserRound } from 'lucide-vue-next'
import { useAdventureStore } from '@/adventure/store'
const game = useAdventureStore()
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
        ><RouterLink to="/aventura" class="catalog-link">{{ t('adventure.nav') }}</RouterLink
        ><CartPreview />
        <RouterLink
          to="/aventura"
          class="user-link"
          :class="{ 'is-signed-in': game.trainer }"
          :aria-label="game.trainer ? t('adventure.account') : t('adventure.login')"
          :title="
            game.trainer
              ? `${t('adventure.account')}: ${game.trainer.username}`
              : t('adventure.login')
          "
        >
          <UserRound :size="20" aria-hidden="true" />
          <span v-if="game.trainer" class="user-status" aria-hidden="true"></span>
        </RouterLink>
      </nav>
      <PreferencesControls />
    </div>
  </header>
</template>

<style scoped>
.user-link {
  position: relative;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--surface);
  color: var(--purple);
}
.user-link:hover,
.user-link:focus-visible,
.user-link.is-signed-in {
  background: var(--feature);
  border-color: var(--purple);
}
.user-status {
  position: absolute;
  right: 3px;
  bottom: 3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--purple);
  box-shadow: 0 0 0 2px var(--surface);
}
</style>
