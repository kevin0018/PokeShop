import { test, expect } from '@playwright/test'
test('catalog pages, forms, cart reload and network recovery', async ({ page }) => {
  await page.goto('/catalogo?forms=default')
  await page.getByRole('searchbox').fill('#025')
  await expect(page.getByRole('article')).toHaveCount(1)
  await page.getByRole('button', { name: 'Añadir Pikachu al carrito', exact: true }).click()
  await page.getByRole('searchbox').fill('')
  await expect(page.getByRole('article')).toHaveCount(24)
  await page.getByRole('button', { name: 'Siguiente', exact: true }).click()
  await expect(page).toHaveURL(/page=2/)
  await page.getByRole('combobox', { name: 'Generación', exact: true }).click()
  await page.getByRole('option', { name: 'Generación 7', exact: true }).click()
  await expect(page).not.toHaveURL(/page=2/)
  await page.goto('/carrito')
  await expect(page.getByLabel('Cantidad de Pikachu', { exact: true })).toHaveText('1')
  await page.getByRole('button', { name: 'Aumentar cantidad de Pikachu' }).click()
  await page.reload()
  await expect(page.getByLabel('Cantidad de Pikachu', { exact: true })).toHaveText('2')
  await page.route('**/api/v1/pokemon/batch?**', (route) => route.abort())
  await page.reload()
  await expect(page.getByRole('alert')).toContainText('conexión')
  expect(await page.evaluate(() => JSON.parse(localStorage.getItem('pokeshop.cart.v1')!))).toEqual([
    { id: 25, quantity: 2 },
  ])
  await page.unroute('**/api/v1/pokemon/batch?**')
  await page.getByRole('button', { name: 'Volver a intentar', exact: true }).click()
  await expect(page.getByLabel('Cantidad de Pikachu', { exact: true })).toHaveText('2')
})
test('select keyboard, Escape, theme and locale persistence', async ({ page }) => {
  await page.goto('/')
  const language = page.getByRole('combobox', { name: 'Idioma', exact: true })
  await language.press('ArrowDown')
  await expect(page.getByRole('listbox')).toBeVisible()
  await expect(page.getByRole('option', { name: 'ES', exact: true })).toBeFocused()
  await page.keyboard.press('ArrowDown')
  await expect(page.getByRole('option', { name: 'EN', exact: true })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('combobox', { name: 'Language', exact: true })).toContainText('EN')
  const appearance = page.getByRole('combobox', { name: 'Appearance', exact: true })
  await appearance.click()
  await page.getByRole('option', { name: 'Dark', exact: true }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await appearance.click()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('listbox')).toHaveCount(0)
  await expect(appearance).toBeFocused()
})
for (const locale of ['es', 'en'])
  for (const theme of ['light', 'dark'])
    for (const width of [320, 375, 414, 768, 1280]) {
      test(`responsive ${locale} ${theme} ${width}`, async ({ page }, testInfo) => {
        await page.addInitScript(
          ({ locale, theme }) => {
            localStorage.setItem('pokeshop.locale', locale)
            localStorage.setItem('pokeshop.theme', theme)
          },
          { locale, theme },
        )
        await page.setViewportSize({ width, height: 900 })
        for (const [name, path, selector, count] of [
          ['home', '/', '.bento-pokemon', 6],
          ['catalog', '/catalogo', '.pokemon-card', 24],
          ['detail', '/pokemon/10100', 'meter', 6],
          ['cart', '/carrito', '.recommendations .pokemon-card', 4],
        ] as const) {
          await page.goto(path!)
          await expect(page.locator('h1')).toBeVisible()
          await expect(page.locator(selector)).toHaveCount(count)
          await expect(page.locator('[role=alert]')).toHaveCount(0)
          expect(
            await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth),
          ).toBe(true)
          // Scroll through real lazy images before capturing the full page.
          for (const image of await page.locator('main img').all()) {
            await image.scrollIntoViewIfNeeded()
            await expect(image).toHaveJSProperty('complete', true)
          }
          await page.locator('h1').scrollIntoViewIfNeeded()
          await page.screenshot({
            path: testInfo.outputPath(`${name}.png`),
            fullPage: true,
            animations: 'disabled',
          })
        }
      })
    }
