import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { useCatalogStore } from '@/pokemon/application/catalogStore'
import { readCart, saveCart } from '../infrastructure/cartStorage'
import { i18n } from '@/i18n'

export const useCartStore = defineStore('cart', () => {
  const catalog = useCatalogStore()
  const entries = ref(readCart())
  const noticeEvent = ref<{
    key: 'adjusted' | 'maximum' | 'added' | 'removed'
    name?: string
    count?: number
  } | null>(null)
  const notice = computed(() =>
    noticeEvent.value
      ? i18n.global.t(noticeEvent.value.key, {
          name: noticeEvent.value.name ?? '',
          units: i18n.global.t('units', noticeEvent.value.count ?? 0),
        })
      : '',
  )
  const storageFailed = ref(false)
  const storageWarning = computed(() =>
    storageFailed.value ? i18n.global.t('storageWarning') : '',
  )
  function dismissNotice() {
    noticeEvent.value = null
  }
  const lines = computed(() =>
    entries.value.flatMap((entry) => {
      const pokemon = catalog.items.find((item) => item.id === entry.id)
      if (!pokemon || pokemon.stock === 0) return []
      return [{ pokemon, quantity: Math.min(entry.quantity, pokemon.stock) }]
    }),
  )
  const count = computed(() => lines.value.reduce((sum, line) => sum + line.quantity, 0))
  const total = computed(() =>
    lines.value.reduce((sum, line) => sum + line.quantity * line.pokemon.price_cents, 0),
  )
  function persist() {
    storageFailed.value = !saveCart(entries.value)
  }
  watch(
    () => catalog.loaded,
    (loaded) => {
      if (!loaded) return
      const updated = lines.value.map((line) => ({ id: line.pokemon.id, quantity: line.quantity }))
      if (JSON.stringify(updated) !== JSON.stringify(entries.value)) {
        noticeEvent.value = { key: 'adjusted' }
        entries.value = updated
        persist()
      }
    },
    { immediate: true },
  )
  function add(id: number) {
    const item = catalog.items.find((item) => item.id === id)
    if (!item || item.stock === 0) return
    const entry = entries.value.find((entry) => entry.id === id)
    if (entry && entry.quantity >= item.stock) {
      noticeEvent.value = { key: 'maximum', name: item.name }
      return
    }
    if (entry) entry.quantity++
    else entries.value.push({ id, quantity: 1 })
    noticeEvent.value = { key: 'added', name: item.name, count: count.value }
    persist()
  }
  function setQuantity(id: number, quantity: number) {
    if (!Number.isSafeInteger(quantity) || quantity < 1) return
    const item = catalog.items.find((item) => item.id === id)
    const entry = entries.value.find((entry) => entry.id === id)
    if (!item || !entry) return
    entry.quantity = Math.min(quantity, item.stock)
    persist()
  }
  function remove(id: number) {
    entries.value = entries.value.filter((entry) => entry.id !== id)
    noticeEvent.value = { key: 'removed' }
    persist()
  }
  return { lines, count, total, notice, storageWarning, dismissNotice, add, setQuantity, remove }
})
