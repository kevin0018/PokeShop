import { computed, onScopeDispose, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { initialTheme, savePreference, THEME_KEY, type Theme } from '../infrastructure/preferences'

export const useThemeStore = defineStore('theme', () => {
  const preference = ref<Theme>(initialTheme())
  const media = window.matchMedia('(prefers-color-scheme: dark)')
  const systemDark = ref(media.matches)
  const resolved = computed(() =>
    preference.value === 'system' ? (systemDark.value ? 'dark' : 'light') : preference.value,
  )
  const onChange = (event: MediaQueryListEvent) => {
    systemDark.value = event.matches
  }
  media.addEventListener('change', onChange)
  onScopeDispose(() => media.removeEventListener('change', onChange))
  watch(
    resolved,
    (theme) => {
      document.documentElement.dataset.theme = theme
    },
    { immediate: true, flush: 'sync' },
  )
  watch(preference, (theme) => savePreference(THEME_KEY, theme), { flush: 'sync' })
  return { preference, resolved }
})
