import { parseCart, type CartEntry } from '../domain/cart'
const KEY = 'pokeshop.cart.v1'
export function readCart(): CartEntry[] {
  try {
    return parseCart(localStorage.getItem(KEY))
  } catch {
    return []
  }
}
export function saveCart(entries: CartEntry[], recentIds?: number[]): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(entries))
    if (recentIds) localStorage.setItem(`${KEY}.recent`, JSON.stringify(recentIds))
    return true
  } catch {
    return false
  }
}

export function readRecentIds(): number[] {
  try {
    const value: unknown = JSON.parse(localStorage.getItem(`${KEY}.recent`) ?? '[]')
    return Array.isArray(value)
      ? [...new Set(value.filter((id): id is number => Number.isSafeInteger(id) && id > 0))]
      : []
  } catch {
    return []
  }
}
