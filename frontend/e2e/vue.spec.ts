import { test, expect } from '@playwright/test'

// See here how to get started:
// https://playwright.dev/docs/intro
test('finds a Pokemon and persists the cart after a reload', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('searchbox', { name: 'Buscar Pokémon' }).fill('#025')
  await expect(page.getByRole('article')).toHaveCount(1)
  await page.getByRole('button', { name: 'Añadir Pikachu al carrito' }).click()
  await page.getByRole('link', { name: 'Mi carrito 1' }).click()
  await expect(page.getByRole('heading', { name: 'Mi carrito', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Aumentar cantidad de Pikachu' }).click()
  await page.reload()
  await expect(page.getByLabel('Cantidad de Pikachu', { exact: true })).toHaveText('2')
  await page.getByRole('button', { name: 'Eliminar Pikachu' }).click()
  await expect(page.getByRole('heading', { name: 'Tu equipo está por descubrir' })).toBeVisible()
})
