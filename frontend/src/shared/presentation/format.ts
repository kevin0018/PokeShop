import { i18n } from '@/i18n'
import type { Pokemon } from '@/pokemon/domain/pokemon'
export const money = (cents: number) => i18n.global.n(cents / 100, 'currency')
export const number = (id: number) => `#${String(id).padStart(3, '0')}`
export const typeName = (type: string) =>
  i18n.global.te(`types.${type}`) ? i18n.global.t(`types.${type}`) : type
export const description = (pokemon: Pokemon) =>
  i18n.global.te(`descriptions.${pokemon.id}`)
    ? i18n.global.t(`descriptions.${pokemon.id}`)
    : pokemon.description
