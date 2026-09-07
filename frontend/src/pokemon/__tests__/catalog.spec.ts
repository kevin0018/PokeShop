import { describe, expect, it } from 'vitest'
import { filterCatalog } from '../application/filterCatalog'
import type { Pokemon } from '../domain/pokemon'

const items: Pokemon[] = [
  {
    id: 25,
    name: 'Pikachu',
    types: ['electrico'],
    price_cents: 2990,
    stock: 2,
    description: '',
    image_url: '',
  },
  {
    id: 7,
    name: 'Squirtle',
    types: ['agua'],
    price_cents: 2490,
    stock: 1,
    description: '',
    image_url: '',
  },
]
describe('catalog filters', () => {
  it('matches names and padded Pokédex numbers with combined type filters', () => {
    expect(filterCatalog(items, ' PIKA ', 'electrico', 'number').map((item) => item.id)).toEqual([
      25,
    ])
    expect(filterCatalog(items, '#025', '', 'number').map((item) => item.id)).toEqual([25])
    expect(filterCatalog(items, 'Pikachu', 'agua', 'number')).toEqual([])
  })
  it('sorts without mutating the repository result', () => {
    expect(filterCatalog(items, '', '', 'price_asc').map((item) => item.id)).toEqual([7, 25])
    expect(filterCatalog(items, '', '', 'price_desc').map((item) => item.id)).toEqual([25, 7])
    expect(items.map((item) => item.id)).toEqual([25, 7])
  })
})
