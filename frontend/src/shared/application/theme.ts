import { computed, nextTick, onScopeDispose, ref, watch } from 'vue'
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
    if (preference.value === 'system') {
      revision++
      transition?.skipTransition()
      animation?.cancel()
      document.documentElement.classList.remove('theme-colors')
    }
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
  let transition:
    | { skipTransition: () => void; finished: Promise<void>; ready: Promise<void> }
    | undefined
  let animation: Animation | undefined
  let revision = 0
  let fallbackTimer: ReturnType<typeof setTimeout> | undefined
  onScopeDispose(() => clearTimeout(fallbackTimer))
  async function change(value: Theme, origin?: DOMRect) {
    const token = ++revision
    transition?.skipTransition()
    animation?.cancel()
    clearTimeout(fallbackTimer)
    document.documentElement.classList.remove('theme-colors')
    if (transition) await transition.finished.catch(() => {})
    if (token !== revision) return
    const root = document.documentElement
    const next = value === 'system' ? (systemDark.value ? 'dark' : 'light') : value
    if (next === resolved.value || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      preference.value = value
      return
    }
    const doc = document as Document & {
      startViewTransition?: (update: () => Promise<void>) => NonNullable<typeof transition>
    }
    if (!doc.startViewTransition) {
      root.classList.add('theme-colors')
      void root.offsetWidth
      preference.value = value
      fallbackTimer = setTimeout(() => root.classList.remove('theme-colors'), 300)
      return
    }
    // Let Reka close its portal before capturing the old page.
    await nextTick()
    await new Promise<void>((resolve) =>
      requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
    )
    if (token !== revision) return
    const x = origin ? origin.x + origin.width / 2 : innerWidth / 2
    const y = origin ? origin.y + origin.height / 2 : 0
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y))
    const active = doc.startViewTransition(async () => {
      preference.value = value
      await nextTick()
    })
    transition = active
    try {
      await active.ready
      if (token !== revision) return
      animation = root.animate(
        { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`] },
        { duration: 700, easing: 'ease-in-out', pseudoElement: '::view-transition-new(root)' },
      )
      await animation.finished.catch(() => {})
    } catch {
      if (token === revision) preference.value = value
    } finally {
      if (transition === active) transition = undefined
    }
  }
  return { preference, resolved, change }
})
