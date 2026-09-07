import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { useCatalogStore } from '@/pokemon/application/catalogStore'
import { readCart, saveCart } from '../infrastructure/cartStorage'
import { i18n } from '@/i18n'
import { pokemonName } from '@/shared/presentation/format'

export const useCartStore = defineStore('cart', () => {
  const catalog = useCatalogStore()
  const entries = ref(readCart())
  const noticeEvent = ref<{
    key: 'adjusted' | 'maximum' | 'added' | 'removed'
    name?: string
    id?: number
    count?: number
  } | null>(null)
  const notice = computed(() =>
    noticeEvent.value
      ? i18n.global.t(noticeEvent.value.key, {
          name: catalog.items.find((p) => p.id === noticeEvent.value?.id)
            ? pokemonName(catalog.items.find((p) => p.id === noticeEvent.value?.id)!)
            : (noticeEvent.value.name ?? ''),
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
  const count = computed(() =>
    entries.value.reduce((sum, entry) => {
      const product = catalog.items.find((p) => p.id === entry.id)
      return sum + Math.min(entry.quantity, product?.stock ?? entry.quantity)
    }, 0),
  )
  const total = computed(() =>
    lines.value.reduce((sum, line) => sum + line.quantity * line.pokemon.price_cents, 0),
  )
  function persist() {
    storageFailed.value = !saveCart(entries.value)
  }
  const loading = ref(false)
  const error = ref(false)
  async function hydrate() {
    loading.value = true
    error.value = false
    try {
      const requested = new Set(entries.value.map((e) => e.id))
      const fresh = await catalog.hydrate([...requested])
      const updated = entries.value.flatMap((entry) => {
        if (!requested.has(entry.id)) return [entry]
        const product = fresh.find((p) => p.id === entry.id)
        return product && product.stock > 0
          ? [{ id: entry.id, quantity: Math.min(entry.quantity, product.stock) }]
          : []
      })
      if (JSON.stringify(updated) !== JSON.stringify(entries.value)) {
        entries.value = updated
        noticeEvent.value = { key: 'adjusted' }
        persist()
      }
    } catch {
      error.value = true
    } finally {
      loading.value = false
    }
  }
  function add(id: number) {
    const item = catalog.items.find((item) => item.id === id)
    if (!item || item.stock === 0) return
    const entry = entries.value.find((entry) => entry.id === id)
    if (entry && entry.quantity >= item.stock) {
      noticeEvent.value = { key: 'maximum', id, name: item.name }
      return
    }
    if (entry) entry.quantity++
    else entries.value.push({ id, quantity: 1 })
    noticeEvent.value = { key: 'added', id, name: item.name, count: count.value }
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
  return {
    entries,
    loading,
    error,
    hydrate,
    lines,
    count,
    total,
    notice,
    storageWarning,
    dismissNotice,
    add,
    setQuantity,
    remove,
  }
})
