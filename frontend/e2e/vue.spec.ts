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
  await page.getByRole('button', { name: /^Filtros/ }).click()
  await page.getByRole('combobox', { name: 'Generación', exact: true }).click()
  await page.getByRole('option', { name: 'Generación 7', exact: true }).click()
  await expect(page).toHaveURL(/page=2/)
  await page.getByRole('button', { name: 'Aplicar', exact: true }).click()
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
          ['home', '/', '.hero-pikachu', 1],
          ['catalog', '/catalogo', '.pokemon-card', 24],
          ['detail', '/pokemon/10100', '.stats-trigger', 1],
          ['cart', '/carrito', '.recommendations .pokemon-card', 4],
        ] as const) {
          await page.goto(path!)
          await expect(page.locator('h1')).toBeVisible()
          for (const pause of await page.locator('.scene-toggle').all()) await pause.click()
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

test('draft cancel, region apply, height order and stats interactions', async ({ page }) => {
  await page.goto('/catalogo?page=2')
  await page.getByRole('button', { name: /^Filtros/ }).click()
  await page.getByRole('combobox', { name: 'Región de origen', exact: true }).click()
  await page.getByRole('option', { name: 'Kanto', exact: true }).click()
  await page.getByRole('button', { name: 'Cancelar', exact: true }).click()
  await expect(page).toHaveURL(/page=2/)
  await expect(page).not.toHaveURL(/region=/)
  await page.getByRole('button', { name: /^Filtros/ }).click()
  await page.getByRole('combobox', { name: 'Región de origen', exact: true }).click()
  await page.getByRole('option', { name: 'Alola', exact: true }).click()
  await page.getByRole('combobox', { name: 'Ordenar Pokémon', exact: true }).click()
  await page.getByRole('option', { name: 'Altura: mayor primero', exact: true }).click()
  await page.getByRole('button', { name: 'Aplicar', exact: true }).click()
  await expect(page).toHaveURL(/region=alola/)
  await expect(page).toHaveURL(/sort=height_desc/)
  await expect(page).not.toHaveURL(/page=2/)
  const response = await page.request.get('/api/v1/pokemon?region=alola&sort=height_desc&limit=24')
  const { items } = await response.json()
  await expect(page.locator('.catalog-bento .pokemon-card')).toHaveCount(items.length)
  const ids = await page
    .locator('.catalog-bento .card-art')
    .evaluateAll((links) => links.map((l) => Number(l.getAttribute('href')?.split('/').pop())))
  expect(ids).toEqual(items.map((p: { id: number }) => p.id))
  await page.goto('/pokemon/3')
  const stats = page.getByRole('button', { name: 'Ver estadísticas', exact: true })
  await stats.hover()
  await expect(page.locator('meter')).toHaveCount(6)
  await stats.click()
  await page.locator('h1').hover()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(stats).toBeFocused()
  await page.getByRole('heading', { level: 1 }).click()
  await stats.focus()
  await expect(page.locator('meter')).toHaveCount(6)
  await page.keyboard.press('Escape')
  await page.setViewportSize({ width: 375, height: 800 })
  await stats.click()
  await expect(page.locator('meter')).toHaveCount(6)
  await page.getByRole('button', { name: 'Cerrar', exact: true }).click()
  await expect(stats).toBeFocused()
})

test('hero pause and reduced motion, theme transition duration and latest selection', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.locator('.pikachu-scene')).toHaveAttribute('data-running', 'true')
  await page.getByRole('button', { name: 'Pausar animación' }).click()
  await expect(page.locator('.pikachu-scene')).toHaveAttribute('data-running', 'false')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await expect(page.locator('.scene-toggle')).toHaveCount(0)
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.evaluate(() => {
    const original = document.documentElement.animate.bind(document.documentElement)
    ;(window as unknown as { durations: number[] }).durations = []
    document.documentElement.animate = (frames, options) => {
      if (typeof options === 'object')
        (window as unknown as { durations: number[] }).durations.push(Number(options.duration))
      return original(frames, options)
    }
  })
  await page.getByRole('combobox', { name: 'Apariencia', exact: true }).click()
  await page.getByRole('option', { name: 'Oscuro', exact: true }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await expect
    .poll(() => page.evaluate(() => (window as unknown as { durations: number[] }).durations))
    .toContain(700)
  await page.getByRole('combobox', { name: 'Apariencia', exact: true }).click()
  await page.getByRole('option', { name: 'Claro', exact: true }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
})

test('touch statistics and timed cart notice', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    isMobile: true,
    hasTouch: true,
  })
  const page = await context.newPage()
  await page.goto(`${process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173'}/pokemon/25`)
  const stats = page.getByRole('button', { name: 'Ver estadísticas', exact: true })
  await stats.tap()
  await expect(page.locator('meter')).toHaveCount(6)
  await page.getByRole('button', { name: 'Cerrar', exact: true }).tap()
  await expect(page.locator('meter')).toHaveCount(0)
  await page.clock.install()
  await page.getByRole('button', { name: 'Añadir al carrito', exact: true }).tap()
  await expect(page.locator('.cart-notice')).toBeVisible()
  await page.clock.fastForward(2000)
  await expect(page.locator('.cart-notice')).toBeVisible()
  await page.clock.fastForward(1000)
  await expect(page.locator('.cart-notice')).toHaveCount(0)
  await context.close()
})
