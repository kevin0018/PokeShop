<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Languages } from 'lucide-vue-next'
import { ref } from 'vue'
import { useThemeStore } from '@/shared/application/theme'
import AppSelect from './AppSelect.vue'
const { t, locale } = useI18n({ useScope: 'global' }),
  theme = useThemeStore(),
  control = ref<HTMLElement>()
function toggle() {
  void theme.change(
    theme.resolved === 'dark' ? 'light' : 'dark',
    control.value?.getBoundingClientRect(),
  )
}
function automatic() {
  void theme.change(
    theme.preference === 'system' ? theme.resolved : 'system',
    control.value?.getBoundingClientRect(),
  )
}
</script>
<template>
  <div class="preferences-controls">
    <div class="preference-control">
      <AppSelect
        v-model="locale"
        :label="t('language')"
        :options="[
          { value: 'es', label: 'ES' },
          { value: 'en', label: 'EN' },
        ]"
        ><Languages :size="16" aria-hidden="true" /></AppSelect
      ><span class="focus-hint">{{ t('language') }}</span>
    </div>
    <div ref="control" class="theme-controls">
      <button
        type="button"
        class="pokemon-switch"
        role="switch"
        :aria-checked="theme.resolved === 'dark'"
        :aria-label="t('dark')"
        :title="t('theme') + ': ' + t(theme.resolved)"
        :data-theme="theme.resolved"
        @click="toggle"
      >
        <span class="switch-thumb" aria-hidden="true" /><img
          class="switch-espeon"
          src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/196.png"
          alt=""
          width="40"
          height="40"
        /><img
          class="switch-umbreon"
          src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/197.png"
          alt=""
          width="40"
          height="40"
        /></button
      ><button
        class="theme-auto"
        :aria-pressed="theme.preference === 'system'"
        :aria-label="t('automaticTheme')"
        :title="t('automaticTheme')"
        @click="automatic"
      >
        Auto</button
      ><span class="focus-hint">{{ t(theme.resolved) }}</span>
    </div>
  </div>
</template>
<style>
.theme-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  position: relative;
}
.pokemon-switch {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-around;
  width: 88px;
  height: 44px;
  padding: 2px;
  border: 1px solid var(--control-border);
  border-radius: 28px;
  background: var(--control-surface);
  cursor: pointer;
  isolation: isolate;
}
.pokemon-switch img {
  position: relative;
  object-fit: contain;
  z-index: 1;
  image-rendering: auto;
  transition:
    transform 0.35s,
    opacity 0.35s;
}
.switch-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #efdcff;
  box-shadow: 0 2px 8px #0002;
  transition:
    transform 0.35s cubic-bezier(0.4, 0, 0.2, 1),
    background-color 0.35s;
}
.pokemon-switch[data-theme='dark'] .switch-thumb {
  transform: translateX(44px);
  background: #a793c1;
}
.pokemon-switch[data-theme='dark'] .switch-espeon,
.pokemon-switch[data-theme='light'] .switch-umbreon {
  opacity: 0.4;
  transform: scale(0.85);
}
.theme-auto {
  border: 1px solid var(--control-border);
  border-radius: 10px;
  background: var(--control-surface);
  color: var(--muted-strong);
  font-size: 0.65rem;
  min-height: 44px;
  padding: 0 7px;
  cursor: pointer;
}
.theme-auto[aria-pressed='true'] {
  color: var(--purple);
  border-color: var(--purple);
  background: var(--lavender);
}
.theme-controls:focus-within .focus-hint {
  opacity: 1;
  visibility: visible;
}
@media (max-width: 400px) {
  .pokemon-switch {
    width: 72px;
  }
  .pokemon-switch img {
    width: 32px;
  }
  .switch-thumb {
    width: 30px;
    height: 30px;
    top: 6px;
  }
  .pokemon-switch[data-theme='dark'] .switch-thumb {
    transform: translateX(34px);
  }
  .theme-auto {
    padding: 0 5px;
    font-size: 0.6rem;
  }
  .theme-controls {
    gap: 4px;
  }
  .preferences-controls {
    gap: 5px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .switch-thumb,
  .pokemon-switch img {
    transition: none;
  }
}
</style>
