import { createI18n } from 'vue-i18n'
import { watch } from 'vue'
import en from './en'
import es from './es'
import { initialLocale, LOCALE_KEY, savePreference } from '@/shared/infrastructure/preferences'

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: 'es',
  messages: { en, es },
  numberFormats: {
    es: { currency: { style: 'currency', currency: 'EUR' } },
    en: { currency: { style: 'currency', currency: 'EUR' } },
  },
})

export function syncLocale() {
  return watch(
    i18n.global.locale,
    (locale) => {
      document.documentElement.lang = locale
      document.title = i18n.global.t('pageTitle')
      document
        .querySelector('meta[name="description"]')
        ?.setAttribute('content', i18n.global.t('pageDescription'))
      savePreference(LOCALE_KEY, locale)
    },
    { immediate: true, flush: 'sync' },
  )
}
