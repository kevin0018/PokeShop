import { i18n } from '@/i18n'
import type { Pokemon } from '@/pokemon/domain/pokemon'
export const money = (cents: number) => i18n.global.n(cents / 100, 'currency')
export const number = (id: number) => `#${String(id).padStart(3, '0')}`
export const decimal = (value: number) =>
  new Intl.NumberFormat(i18n.global.locale.value, { maximumFractionDigits: 1 }).format(value)
export const pokemonName = (p: Pokemon) => p.names?.[i18n.global.locale.value] || p.name
export const typeName = (type: string) =>
  i18n.global.te(`types.${type}`) ? i18n.global.t(`types.${type}`) : type
export const description = (p: Pokemon) =>
  p.descriptions?.[i18n.global.locale.value] ||
  i18n.global.t('factualDescription', {
    name: pokemonName(p),
    types: p.types.map(typeName).join(' / '),
    weight: p.weight_kg === undefined ? '—' : decimal(p.weight_kg),
    height: p.height_m === undefined ? '—' : decimal(p.height_m),
  })
