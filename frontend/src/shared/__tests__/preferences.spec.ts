import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'
import { createPinia, disposePinia, type Pinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import App from '@/App.vue'
import CatalogView from '@/pokemon/presentation/CatalogView.vue'
import CartView from '@/cart/presentation/CartView.vue'
import PokemonDetailView from '@/pokemon/presentation/PokemonDetailView.vue'
import { httpPokemonRepository } from '@/pokemon/infrastructure/httpPokemonRepository'
import { i18n, syncLocale } from '@/i18n'
import { initialLocale, initialTheme } from '../infrastructure/preferences'

let wrapper: VueWrapper
let pinia: Pinia
let stopLocale: () => void
let systemChange: (event: { matches: boolean }) => void
const pokemon = {
  id: 1,
  name: 'Bulbasaur',
  types: ['planta', 'veneno'],
  price_cents: 2490,
  stock: 2,
  description: 'Descripción de API',
  image_url: '',
}

beforeEach(() => {
  localStorage.clear()
  i18n.global.locale.value = 'es'
  systemChange = () => {}
  vi.stubGlobal('matchMedia', () => ({
    matches: false,
    addEventListener: (_event: string, handler: typeof systemChange) => {
      systemChange = handler
    },
    removeEventListener: vi.fn(),
  }))
  vi.spyOn(httpPokemonRepository, 'list').mockResolvedValue([pokemon])
})
afterEach(() => {
  wrapper?.unmount()
  if (pinia) disposePinia(pinia)
  stopLocale?.()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

async function start(path = '/') {
  pinia = createPinia()
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: CatalogView },
      { path: '/carrito', component: CartView },
      { path: '/pokemon/:id', component: PokemonDetailView },
    ],
  })
  await router.push(path)
  await router.isReady()
  stopLocale = syncLocale()
  wrapper = mount(App, { global: { plugins: [pinia, i18n, router] } })
  await flushPromises()
  return router
}

describe('appearance and language integration', () => {
  it('switches catalog, accessible labels, active notices and cart prices without losing the cart', async () => {
    const router = await start()
    await wrapper.get('.preferences-controls select').setValue('en')
    expect(wrapper.text()).toContain('Find your favorite')
    expect(wrapper.get('input[type="search"]').attributes('placeholder')).toBe(
      'Name or Pokédex number',
    )
    expect(wrapper.text()).toContain('Grass')
    await wrapper.get('button[aria-label="Add Bulbasaur to cart"]').trigger('click')
    expect(wrapper.get('.cart-notice').text()).toContain('Bulbasaur added to cart (1 unit).')
    await wrapper.get('.preferences-controls select').setValue('es')
    expect(wrapper.get('.cart-notice').text()).toContain('Bulbasaur añadido al carrito (1 unidad).')
    await router.push('/carrito')
    await flushPromises()
    expect(wrapper.get('.cart-line-total strong').text()).toMatch(/24,90\s*€/)
    await wrapper.get('.preferences-controls select').setValue('en')
    expect(wrapper.get('.cart-line-total strong').text()).toBe('€24.90')
    expect(wrapper.text()).toContain('Subtotal (1 unit)')
    expect(wrapper.text()).toContain('Orders and payments are not available yet.')
  })
  it('translates product descriptions and stock on the current detail page', async () => {
    await start('/pokemon/1')
    await wrapper.get('.preferences-controls select').setValue('en')
    expect(wrapper.get('.description').text()).toBe(
      'The perfect companion to start your collection. Its bulb grows alongside it.',
    )
    expect(wrapper.get('.stock-label').text()).toBe('2 units available')
    expect(wrapper.text()).not.toContain('Descripción de API')
  })
  it('translates an already visible API error and its retry control', async () => {
    vi.mocked(httpPokemonRepository.list).mockRejectedValue(new Error('offline'))
    await start()
    await wrapper.get('.preferences-controls select').setValue('en')
    expect(wrapper.get('[role="alert"]').text()).toContain('Check your connection and try again.')
    expect(wrapper.get('[role="alert"] button').text()).toBe('Try again')
  })
  it('persists locale/theme, updates document language, and follows system changes only in automatic mode', async () => {
    await start()
    const selects = wrapper.findAll('.preferences-controls select')
    await selects[0]!.setValue('en')
    await selects[1]!.setValue('dark')
    expect(initialLocale()).toBe('en')
    expect(initialTheme()).toBe('dark')
    expect(document.documentElement.lang).toBe('en')
    expect(document.title).toBe('PokeShop · Your Pokémon collection')
    systemChange({ matches: false })
    expect(document.documentElement.dataset.theme).toBe('dark')
    await selects[1]!.setValue('system')
    expect(document.documentElement.dataset.theme).toBe('light')
    systemChange({ matches: true })
    expect(document.documentElement.dataset.theme).toBe('dark')
  })
  it('keeps both controls usable when browser storage is blocked', async () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('blocked')
    })
    await start()
    const selects = wrapper.findAll('.preferences-controls select')
    await selects[0]!.setValue('en')
    await selects[1]!.setValue('dark')
    expect(wrapper.text()).toContain('Find your favorite')
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(initialLocale()).toBe('es')
    expect(initialTheme()).toBe('system')
  })
})
