<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { UserRound, LogOut, UsersRound, Award, LogIn, UserPlus } from 'lucide-vue-next'
import {
  DropdownMenuRoot,
  DropdownMenuTrigger,
  DropdownMenuPortal,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
} from 'reka-ui'
import { useAdventureStore } from '@/adventure/store'
const game = useAdventureStore()
const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const open = ref(false)
watch(
  () => route.fullPath,
  () => {
    open.value = false
  },
)
async function logout() {
  if (await game.mutate('/logout', 'POST')) await router.push('/aventura?mode=login')
}
</script>

<template>
  <DropdownMenuRoot v-model:open="open">
    <DropdownMenuTrigger
      class="user-link"
      :class="{ 'is-signed-in': game.trainer }"
      :aria-label="t('adventure.account')"
    >
      <UserRound :size="20" aria-hidden="true" />
      <span v-if="game.trainer" class="user-status" aria-hidden="true"></span>
    </DropdownMenuTrigger>
    <DropdownMenuPortal>
      <DropdownMenuContent class="user-menu" align="end" :side-offset="10" :collision-padding="16">
        <template v-if="game.trainer">
          <DropdownMenuLabel class="user-summary">
            <strong>{{ game.trainer.username }}</strong>
            <span>{{ t('adventure.credits', { amount: game.trainer.credits }) }}</span>
            <span>{{ t('adventure.medals', { count: game.trainer.medals.length }) }}</span>
          </DropdownMenuLabel>
          <DropdownMenuSeparator class="user-divider" />
          <DropdownMenuItem as-child
            ><RouterLink to="/aventura?tab=team" class="user-menu-item"
              ><UsersRound :size="18" aria-hidden="true" />{{ t('adventure.teamTab') }}</RouterLink
            ></DropdownMenuItem
          >
          <DropdownMenuItem as-child
            ><RouterLink to="/aventura?tab=gyms" class="user-menu-item"
              ><Award :size="18" aria-hidden="true" />{{ t('adventure.gymsTab') }}</RouterLink
            ></DropdownMenuItem
          >
          <DropdownMenuSeparator class="user-divider" />
          <DropdownMenuItem
            class="user-menu-item"
            :disabled="game.busy || game.loading"
            @select="logout"
            ><LogOut :size="18" aria-hidden="true" />{{ t('adventure.logout') }}</DropdownMenuItem
          >
        </template>
        <template v-else>
          <DropdownMenuItem as-child
            ><RouterLink to="/aventura?mode=login" class="user-menu-item"
              ><LogIn :size="18" aria-hidden="true" />{{ t('adventure.login') }}</RouterLink
            ></DropdownMenuItem
          >
          <DropdownMenuItem as-child
            ><RouterLink to="/aventura?mode=register" class="user-menu-item"
              ><UserPlus :size="18" aria-hidden="true" />{{ t('adventure.register') }}</RouterLink
            ></DropdownMenuItem
          >
        </template>
      </DropdownMenuContent>
    </DropdownMenuPortal>
  </DropdownMenuRoot>
</template>

<style>
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
  cursor: pointer;
}
.user-link:hover,
.user-link:focus-visible,
.user-link[data-state='open'],
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
.user-menu {
  z-index: 100;
  width: min(260px, calc(100vw - 32px));
  max-height: var(--reka-dropdown-menu-content-available-height);
  overflow-y: auto;
  padding: 6px;
  border: 1px solid var(--line);
  border-radius: 16px;
  background: var(--surface);
  color: var(--ink);
  box-shadow: 0 12px 32px #0002;
}
.user-summary {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  font-size: 12px;
  color: var(--muted-strong);
}
.user-summary strong {
  color: var(--ink);
  font-size: 14px;
  overflow-wrap: anywhere;
}
.user-menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 13px;
  cursor: pointer;
  outline: none;
}
.user-menu-item[data-highlighted] {
  background: var(--feature);
  color: var(--purple);
}
.user-menu-item[data-disabled] {
  opacity: 0.5;
  cursor: default;
}
.user-divider {
  height: 1px;
  margin: 4px 6px;
  background: var(--line);
}
</style>
