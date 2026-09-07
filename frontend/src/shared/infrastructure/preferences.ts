export type Locale = 'es' | 'en'
export type Theme = 'system' | 'light' | 'dark'
export const LOCALE_KEY = 'pokeshop.locale'
export const THEME_KEY = 'pokeshop.theme'
export function readPreference(key: string): string | null {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}
export function savePreference(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    /* Preferences still work in memory. */
  }
}
export function initialLocale(): Locale {
  return readPreference(LOCALE_KEY) === 'en' ? 'en' : 'es'
}
export function initialTheme(): Theme {
  const saved = readPreference(THEME_KEY)
  return saved === 'dark' || saved === 'light' ? saved : 'system'
}
