import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { parseCart } from '../domain/cart'
import { useCartStore } from '../application/cartStore'
import { useCatalogStore } from '@/pokemon/application/catalogStore'

const pokemon = {
  id: 25,
  name: 'Pikachu',
  types: ['electrico'],
  price_cents: 2990,
  stock: 2,
  description: '',
  image_url: '',
}
beforeEach(() => {
  localStorage.clear()
  setActivePinia(createPinia())
  vi.restoreAllMocks()
})
function loadCatalog() {
  const catalog = useCatalogStore()
  catalog.items = [{ ...pokemon }]
  catalog.loaded = true
}

describe('cart', () => {
  it('discards malformed storage, invalid quantities and duplicate IDs', () => {
    expect(parseCart('{broken')).toEqual([])
    expect(
      parseCart(
        JSON.stringify([
          { id: 25, quantity: 2, price_cents: 1 },
          { id: 25, quantity: 1 },
          { id: 7, quantity: -1 },
          null,
        ]),
      ),
    ).toEqual([{ id: 25, quantity: 2 }])
  })
  it('adds, totals in cents and enforces available stock', () => {
    loadCatalog()
    const cart = useCartStore()
    cart.add(25)
    cart.add(25)
    cart.add(25)
    expect(cart.count).toBe(2)
    expect(cart.total).toBe(5980)
    cart.setQuantity(25, 1)
    expect(cart.total).toBe(2990)
    cart.setQuantity(25, -1)
    expect(cart.count).toBe(1)
    cart.remove(25)
    expect(cart.count).toBe(0)
  })
  it('restores IDs and quantities but takes prices and stock from the catalog', async () => {
    localStorage.setItem(
      'pokeshop.cart.v1',
      JSON.stringify([
        { id: 25, quantity: 80 },
        { id: 999, quantity: 1 },
      ]),
    )
    const cart = useCartStore()
    loadCatalog()
    vi.spyOn(useCatalogStore(), 'hydrate').mockResolvedValue([pokemon])
    await cart.hydrate()
    expect(cart.count).toBe(2)
    expect(cart.total).toBe(5980)
    expect(JSON.parse(localStorage.getItem('pokeshop.cart.v1')!)).toEqual([{ id: 25, quantity: 2 }])
  })
  it('keeps the cart usable when storage is unavailable', () => {
    loadCatalog()
    const cart = useCartStore()
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('Quota exceeded')
    })
    cart.add(25)
    expect(cart.count).toBe(1)
    expect(cart.storageWarning).not.toBe('')
  })
  it('does not add sold out or unknown products', () => {
    loadCatalog()
    useCatalogStore().items[0]!.stock = 0
    const cart = useCartStore()
    cart.add(25)
    cart.add(999)
    expect(cart.count).toBe(0)
  })
  it('retains stored entries on network failure and on unrelated catalog pages', async () => {
    loadCatalog()
    const cart = useCartStore()
    cart.add(25)
    const catalog = useCatalogStore()
    catalog.remember([{ ...pokemon, id: 150 }])
    expect(cart.lines[0]!.pokemon.id).toBe(25)
    vi.spyOn(catalog, 'hydrate').mockRejectedValue(new Error('offline'))
    await cart.hydrate()
    expect(cart.error).toBe(true)
    expect(cart.entries).toEqual([{ id: 25, quantity: 1 }])
    expect(JSON.parse(localStorage.getItem('pokeshop.cart.v1')!)).toEqual([{ id: 25, quantity: 1 }])
  })
  it('keeps the badge count while stored products cannot be fetched', async () => {
    localStorage.setItem('pokeshop.cart.v1', JSON.stringify([{ id: 10100, quantity: 2 }]))
    const cart = useCartStore()
    vi.spyOn(useCatalogStore(), 'hydrate').mockRejectedValue(new Error('offline'))
    await cart.hydrate()
    expect(cart.count).toBe(2)
    expect(cart.entries).toEqual([{ id: 10100, quantity: 2 }])
  })
})

describe('cart preview and clearing', () => {
  it('tracks recent distinct additions without moving cart lines and survives reload', () => {
    const catalog = useCatalogStore()
    catalog.items = [1, 2, 3, 4].map((id) => ({ ...pokemon, id, stock: 10 }))
    const cart = useCartStore()
    for (const id of [1, 2, 3, 4, 1]) cart.add(id)
    expect(cart.entries.map((entry) => entry.id)).toEqual([1, 2, 3, 4])
    expect(cart.recentLines.map((line) => line.pokemon.id)).toEqual([1, 4, 3])
    cart.setQuantity(2, 3)
    expect(cart.recentLines.map((line) => line.pokemon.id)).toEqual([1, 4, 3])
    setActivePinia(createPinia())
    useCatalogStore().items = catalog.items
    const restored = useCartStore()
    expect(restored.recentLines.map((line) => line.pokemon.id)).toEqual([1, 4, 3])
    restored.remove(1)
    expect(restored.recentLines.map((line) => line.pokemon.id)).toEqual([4, 3, 2])
    restored.clear()
    expect(restored.entries).toEqual([])
    expect(restored.recentLines).toEqual([])
    expect(restored.total).toBe(0)
    expect(restored.count).toBe(0)
    expect(JSON.parse(localStorage.getItem('pokeshop.cart.v1')!)).toEqual([])
    expect(JSON.parse(localStorage.getItem('pokeshop.cart.v1.recent')!)).toEqual([])
  })
})
