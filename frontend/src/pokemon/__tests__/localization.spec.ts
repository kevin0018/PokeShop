import { describe, expect, it } from 'vitest'
import { i18n } from '@/i18n'
import { description, pokemonName } from '@/shared/presentation/format'
const pokemon = {
  id: 10100,
  species_id: 26,
  name: 'Raichu · Alolan Form',
  names: { es: 'Raichu · Forma de Alola', en: 'Raichu · Alolan Form' },
  types: ['electrico'],
  price_cents: 2990,
  stock: 10,
  description: 'Do not leak untranslated prose',
  image_url: '',
  weight_kg: 21,
  height_m: 0.7,
}
describe('API localization fallback', () => {
  it('uses factual localized measurements when translated prose is absent', () => {
    i18n.global.locale.value = 'es'
    expect(description(pokemon)).toContain('Altura: 0,7 m')
    expect(pokemonName(pokemon)).toContain('Forma de Alola')
    i18n.global.locale.value = 'en'
    expect(description(pokemon)).toContain('Height: 0.7 m')
    expect(description(pokemon)).not.toContain('Do not leak')
  })
  it('prefers upstream localized descriptions', () => {
    i18n.global.locale.value = 'es'
    expect(description({ ...pokemon, descriptions: { es: 'Texto de PokéAPI' } })).toBe(
      'Texto de PokéAPI',
    )
  })
})
