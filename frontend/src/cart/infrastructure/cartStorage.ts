import { parseCart, type CartEntry } from '../domain/cart'
const KEY = 'pokeshop.cart.v1'
export function readCart(): CartEntry[] {
  try {
    return parseCart(localStorage.getItem(KEY))
  } catch {
    return []
  }
}
export function saveCart(entries: CartEntry[]): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(entries))
    return true
  } catch {
    return false
  }
}
