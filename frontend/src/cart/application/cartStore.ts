import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { useCatalogStore } from '@/pokemon/application/catalogStore'
import { readCart, saveCart } from '../infrastructure/cartStorage'

export const useCartStore = defineStore('cart', () => {
  const catalog = useCatalogStore()
  const entries = ref(readCart())
  const notice = ref('')
  const storageWarning = ref('')
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
    storageWarning.value = saveCart(entries.value)
      ? ''
      : 'El navegador no permite guardar el carrito. Se conservará solo mientras esta página siga abierta.'
  }
  watch(
    () => catalog.loaded,
    (loaded) => {
      if (!loaded) return
      const updated = lines.value.map((line) => ({ id: line.pokemon.id, quantity: line.quantity }))
      if (JSON.stringify(updated) !== JSON.stringify(entries.value)) {
        notice.value = 'Hemos ajustado el carrito a la disponibilidad del catálogo.'
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
      notice.value = `Ya tienes todas las unidades disponibles de ${item.name}.`
      return
    }
    if (entry) entry.quantity++
    else entries.value.push({ id, quantity: 1 })
    notice.value = `${item.name} añadido al carrito (${count.value} ${count.value === 1 ? 'unidad' : 'unidades'}).`
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
    notice.value = 'Pokémon eliminado del carrito.'
    persist()
  }
  return { lines, count, total, notice, storageWarning, add, setQuantity, remove }
})
