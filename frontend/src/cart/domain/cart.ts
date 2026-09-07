export interface CartEntry {
  id: number
  quantity: number
}

export function parseCart(raw: string | null): CartEntry[] {
  try {
    const data: unknown = JSON.parse(raw ?? '[]')
    if (!Array.isArray(data)) return []
    const seen = new Set<number>()
    return data
      .filter((entry): entry is CartEntry => {
        if (
          !entry ||
          !Number.isSafeInteger(entry.id) ||
          entry.id <= 0 ||
          !Number.isSafeInteger(entry.quantity) ||
          entry.quantity <= 0 ||
          seen.has(entry.id)
        )
          return false
        seen.add(entry.id)
        return true
      })
      .slice(0, 100)
      .map(({ id, quantity }) => ({ id, quantity: Math.min(quantity, 99) }))
  } catch {
    return []
  }
}
