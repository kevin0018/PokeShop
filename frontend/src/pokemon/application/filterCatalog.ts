import type { CatalogSort, Pokemon } from '../domain/pokemon'

export function filterCatalog(items: Pokemon[], search: string, type: string, sort: CatalogSort) {
  const query = search.trim().toLocaleLowerCase('es').replace(/^#/, '')
  return items
    .filter(
      (item) =>
        (!query ||
          item.name.toLocaleLowerCase('es').includes(query) ||
          (/^\d+$/.test(query) && Number(query) === item.id)) &&
        (!type || item.types.includes(type)),
    )
    .sort((a, b) => {
      if (sort === 'price_asc') return a.price_cents - b.price_cents || a.id - b.id
      if (sort === 'price_desc') return b.price_cents - a.price_cents || a.id - b.id
      if (sort === 'name') return a.name.localeCompare(b.name)
      return a.id - b.id
    })
}
