const currency = new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })
export const money = (cents: number) => currency.format(cents / 100)
export const number = (id: number) => `#${String(id).padStart(3, '0')}`
const labels: Record<string, string> = {
  electrico: 'Eléctrico',
  psiquico: 'Psíquico',
  dragon: 'Dragón',
}
export const typeName = (type: string) =>
  labels[type] ?? type.charAt(0).toUpperCase() + type.slice(1)
