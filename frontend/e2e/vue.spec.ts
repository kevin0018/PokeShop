import { test, expect, type Page } from '@playwright/test'
const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173'
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
  await page.emulateMedia({ colorScheme: 'dark' })
  await page.goto('/')
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.emulateMedia({ colorScheme: 'light' })
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'light')
  await page.getByRole('button', { name: 'Saltar intro' }).press('Enter')
  const language = page.getByRole('combobox', { name: 'Idioma', exact: true })
  await language.press('ArrowDown')
  await expect(page.getByRole('listbox')).toBeVisible()
  await expect(page.getByRole('option', { name: 'ES', exact: true })).toBeFocused()
  await page.keyboard.press('ArrowDown')
  await expect(page.getByRole('option', { name: 'EN', exact: true })).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.getByRole('combobox', { name: 'Language', exact: true })).toContainText('EN')
  const appearance = page.getByRole('switch', { name: 'Dark', exact: true })
  await appearance.click()

  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await page.reload()
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await appearance.press('Space')
  await expect(appearance).toHaveAttribute('aria-checked', 'false')
  await expect(page.locator('.theme-auto')).toHaveCount(0)
})
for (const locale of ['es', 'en'])
  for (const theme of ['light', 'dark'])
    for (const width of [320, 375, 414, 768, 1280]) {
      test(`responsive ${locale} ${theme} ${width}`, async ({ page }, testInfo) => {
        await page.addInitScript(
          ({ locale, theme }) => {
            localStorage.setItem('pokeshop.capture.v2', 'seen')
            localStorage.setItem('pokeshop.locale', locale)
            localStorage.setItem('pokeshop.theme', theme)
            localStorage.setItem(
              'pokeshop.cart.v1',
              JSON.stringify(Array.from({ length: 7 }, (_, i) => ({ id: i + 1, quantity: 1 }))),
            )
          },
          { locale, theme },
        )
        await page.setViewportSize({ width, height: 900 })
        for (const [name, path, selector, count] of [
          ['home', '/', '.hero-starter img', 3],
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
          const themeToggle = await page.getByRole('switch').boundingBox()
          expect(themeToggle).not.toBeNull()
          expect(themeToggle!.x + themeToggle!.width).toBeLessThanOrEqual(width)
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
  await expect(page.locator('.catalog-grid .pokemon-card')).toHaveCount(items.length)
  const ids = await page
    .locator('.catalog-grid .card-art')
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
  await expect(page.locator('.starter-scene')).toHaveAttribute('data-running', 'true')
  await page.getByRole('button', { name: 'Pausar animación' }).click()
  await expect(page.locator('.starter-scene')).toHaveAttribute('data-running', 'false')
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
  await page.getByRole('switch', { name: 'Oscuro', exact: true }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await expect
    .poll(() => page.evaluate(() => (window as unknown as { durations: number[] }).durations))
    .toContain(700)
  await page.getByRole('switch', { name: 'Oscuro', exact: true }).click()
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

test('catalog grids of different sizes keep order without overlapping cards', async ({ page }) => {
  const response = await page.request.get('/api/v1/pokemon?limit=7')
  const { items } = await response.json()
  for (const width of [320, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 })
    for (const count of [1, 2, 3, 4, 5, 6, 7]) {
      await page.route('**/api/v1/pokemon?**', (r) =>
        r.fulfill({ json: { items: items.slice(0, count), total: count } }),
      )
      await page.goto('/catalogo')
      await expect(page.locator('.catalog-grid .pokemon-card')).toHaveCount(count)
      const ids = await page
        .locator('.catalog-grid .card-art')
        .evaluateAll((links) => links.map((l) => Number(l.getAttribute('href')?.split('/').pop())))
      expect(ids).toEqual(items.slice(0, count).map((p: { id: number }) => p.id))
      const rects = await page.locator('.catalog-grid .pokemon-card').evaluateAll((cards) =>
        cards.map((c) => {
          const r = c.getBoundingClientRect()
          return { x: r.x, y: r.y, right: r.right, bottom: r.bottom, height: r.height }
        }),
      )
      for (let i = 0; i < rects.length; i++) {
        expect(rects[i]!.height).toBeLessThanOrEqual(417)
        for (let j = i + 1; j < rects.length; j++)
          expect(
            rects[i]!.right <= rects[j]!.x ||
              rects[j]!.right <= rects[i]!.x ||
              rects[i]!.bottom <= rects[j]!.y ||
              rects[j]!.bottom <= rects[i]!.y,
          ).toBe(true)
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
        true,
      )
      await page.unroute('**/api/v1/pokemon?**')
    }
  }
})

async function seedCart(page: Page, count: number) {
  const response = await page.request.get('/api/v1/pokemon?limit=25')
  const { items } = await response.json()
  await page.goto('/catalogo')
  const entries = items.slice(0, count).map((p: { id: number }) => ({ id: p.id, quantity: 1 }))
  await page.evaluate(
    (entries) => localStorage.setItem('pokeshop.cart.v1', JSON.stringify(entries)),
    entries,
  )
  await page.goto('/carrito')
  return items
    .slice(0, count)
    .reduce((sum: number, p: { price_cents: number }) => sum + p.price_cents, 0)
}
test('empty cart keeps Chansey and recommendations', async ({ page }) => {
  await seedCart(page, 0)
  await expect(page.locator('.empty-cart')).toBeVisible()
  await expect(page.locator('.cart-line')).toHaveCount(0)
  await expect(page.locator('.chansey-empty')).toBeVisible()
})
for (const count of [1, 6, 7, 25])
  test(`cart of ${count} products shows six at most and the global total`, async ({ page }) => {
    const total = await seedCart(page, count)
    await expect(page.locator('.cart-line')).toHaveCount(Math.min(count, 6))
    await expect(page.locator('.summary-total strong')).toHaveText(
      new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(total / 100),
    )
  })
test('cart removal clamps pages and quantity changes stay on the current page', async ({
  page,
}) => {
  await seedCart(page, 7)
  await page.getByRole('button', { name: 'Siguiente', exact: true }).click()
  await expect(page.locator('.cart-line')).toHaveCount(1)
  await page.locator('.cart-line .text-button').click()
  await expect(page.locator('.cart-line')).toHaveCount(6)
  await expect(page.locator('.cart-pagination')).toHaveCount(0)
  const total = await seedCart(page, 25)
  await page.getByRole('button', { name: 'Siguiente', exact: true }).click()
  await expect(page.locator('.cart-line')).toHaveCount(6)
  await expect(page.locator('.summary-total strong')).toHaveText(
    new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(total / 100),
  )
  await page.locator('.quantity-control button').nth(1).click()
  await expect(page.locator('.cart-pagination')).toContainText('2')
  expect(
    await page.evaluate(() => JSON.parse(localStorage.getItem('pokeshop.cart.v1')!).length),
  ).toBe(25)
})

test('cart preview shows latest three and global total, opens by hover and click, and clears all', async ({
  page,
  browser,
}) => {
  await page.addInitScript(() => {
    localStorage.setItem(
      'pokeshop.cart.v1',
      JSON.stringify([1, 2, 3, 4].map((id) => ({ id, quantity: 1 }))),
    )
    localStorage.setItem('pokeshop.cart.v1.recent', JSON.stringify([2, 4, 1, 3]))
  })
  await page.goto('/catalogo')
  const trigger = page.locator('.cart-preview-trigger')
  await trigger.hover()
  const preview = page.getByRole('dialog', { name: 'Últimos añadidos' })
  await expect(preview).toBeVisible()
  await expect(preview.locator('.cart-preview-lines li')).toHaveCount(3)
  expect(
    await preview
      .locator('.cart-preview-lines a')
      .evaluateAll((links) => links.map((link) => link.getAttribute('href'))),
  ).toEqual(['/pokemon/2', '/pokemon/4', '/pokemon/1'])
  await expect(preview.locator('.cart-preview-total')).toContainText('4 unidades')
  const total = await preview.locator('.cart-preview-total strong').textContent()
  await preview.hover()
  await expect(preview).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(preview).toBeHidden()
  await expect(trigger).toBeFocused()
  await page.setViewportSize({ width: 320, height: 800 })
  await trigger.click()
  await expect(preview).toBeVisible()
  const bounds = await preview.boundingBox()
  expect(bounds!.x).toBeGreaterThanOrEqual(0)
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(320)
  await page.screenshot({ path: 'test-results/cart-preview-mobile.png' })
  await page.setViewportSize({ width: 1280, height: 800 })
  await page.emulateMedia({ colorScheme: 'dark' })
  await expect(page.getByRole('switch')).toHaveAttribute('aria-checked', 'true')
  await page.screenshot({ path: 'test-results/cart-preview-desktop.png' })
  await preview.getByRole('link', { name: 'Ver carrito completo' }).click()
  await expect(page).toHaveURL(/carrito/)
  await expect(page.locator('.summary-total strong')).toHaveText(total!)
  await page.getByRole('button', { name: 'Vaciar carrito', exact: true }).click()
  await expect(page.locator('.empty-cart')).toBeVisible()
  await expect(page.locator('.cart-count')).toHaveText('0')
  expect(await page.evaluate(() => localStorage.getItem('pokeshop.cart.v1'))).toBe('[]')
  const touch = await browser.newContext({
    hasTouch: true,
    isMobile: true,
    viewport: { width: 375, height: 812 },
    baseURL,
  })
  try {
    await touch.addInitScript(() => localStorage.setItem('pokeshop.locale', 'en'))
    const mobile = await touch.newPage()
    await mobile.goto('/catalogo')
    await mobile.locator('.cart-preview-trigger').tap()
    const panel = mobile.getByRole('dialog', { name: 'Recently added' })
    await expect(panel).toBeVisible()
    await mobile.locator('.cart-preview-trigger').tap()
    await expect(panel).toBeHidden()
    await mobile.locator('.cart-preview-trigger').tap()
    await expect(panel).toBeVisible()
    await expect(panel.locator('.cart-preview-total')).toContainText('€0.00')
    await panel.getByRole('link', { name: 'View full cart' }).tap()
    await expect(mobile).toHaveURL(/carrito/)
    await expect(panel).toBeHidden()
  } finally {
    await touch.close()
  }
})

test('switches the studio feature and browses a type shelf', async ({ page }) => {
  await page.goto('/')
  const feature = page.getByRole('link', { name: 'Ver ficha', exact: true })
  await expect(feature).toHaveAttribute('href', '/pokemon/6')
  await page.getByRole('button', { name: 'Siguiente Pokémon destacado' }).click()
  await expect(feature).toHaveAttribute('href', '/pokemon/25')
  await page.getByRole('button', { name: 'Pokémon destacado anterior' }).click()
  await page.getByRole('button', { name: 'Pokémon destacado anterior' }).click()
  await feature.click()
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Gengar')
  await page.getByRole('link', { name: 'Volver al catálogo' }).click()
  const fire = page.getByRole('button', { name: 'Fuego', exact: true })
  await fire.click()
  await expect(fire).toHaveAttribute('aria-pressed', 'true')
  await expect(page).toHaveURL(/type=fuego/)
  await expect(page.locator('.catalog-grid .pokemon-card').first()).toContainText('Fuego')
  await fire.click()
  await expect(page).not.toHaveURL(/type=fuego/)
})

test('plays the capture once and lets the visitor replay or skip it', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  await page.goto('/')
  const intro = page.getByRole('dialog', { name: 'Repetir captura' })
  await expect(intro).toBeVisible()
  await expect(intro).toBeHidden({ timeout: 7000 })
  await expect(page.getByRole('heading', { name: 'Charizard' })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('button', { name: 'Repetir captura' })).toBeVisible()
  await expect(intro).toHaveCount(0)
  await page.getByRole('button', { name: 'Repetir captura' }).click()
  await expect(intro).toBeVisible()
  await page.getByRole('button', { name: 'Saltar intro' }).click()
  await expect(intro).toHaveCount(0)
  const commands = page.getByRole('group', { name: 'Charizard' })
  const buy = commands.getByRole('button', { name: 'Añadir al carrito' })
  await buy.press('ArrowDown')
  await expect(commands.getByRole('link', { name: 'Catálogo' })).toBeFocused()
  await page.keyboard.press('ArrowUp')
  await expect(buy).toBeFocused()
  await page.keyboard.press('Enter')
  await expect(page.locator('.cart-count')).toHaveText('1')
})

test('opens directly on a still Pokémon when reduced motion is requested', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Charizard' })).toBeVisible()
  await expect(page.locator('.capture-intro')).toHaveCount(0)
  await expect(page.locator('.feature-actor .studio-sprite')).toHaveCSS(
    'background-position',
    '0% 0%',
  )
  await expect(page.getByRole('button', { name: 'Repetir captura' })).toHaveCount(0)
})

test('detail thumbnails navigate with the keyboard in the localized, still layout', async ({
  page,
}) => {
  await page.addInitScript(() => localStorage.setItem('pokeshop.locale', 'en'))
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.setViewportSize({ width: 320, height: 800 })
  await page.route('**/official-artwork/25.png', (route) =>
    route.fulfill({ path: 'public/studio/25.webp' }),
  )
  await page.goto('/pokemon/25')

  const recommendations = page.locator('.profile-stage').getByRole('region', {
    name: 'Recommended Pokémon',
  })
  await expect(recommendations.getByRole('link')).toHaveCount(4)
  await expect(page.locator('.profile-art img')).toHaveCSS('animation-name', 'none')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  const thumbnail = recommendations.getByRole('link').first()
  const destination = await thumbnail.getAttribute('href')
  const name = await thumbnail.getAttribute('aria-label')
  await expect(thumbnail).not.toHaveAttribute('href', '/pokemon/25')
  await expect(thumbnail).toHaveAttribute('aria-label', /\S/)
  await thumbnail.press('Enter')
  await expect(page).toHaveURL(destination!)
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(name!)
  await expect(recommendations.getByRole('link')).toHaveCount(4)
  await expect(recommendations.locator(`a[href="${destination}"]`)).toHaveCount(0)

  await page.goBack()
  await expect(page.getByRole('heading', { name: 'Pikachu', exact: true })).toBeVisible()
})
