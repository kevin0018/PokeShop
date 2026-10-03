import { expect, test, type Page } from '@playwright/test'

async function checkBattleWidths(page: Page) {
  for (const width of [320, 375, 414, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    for (const button of await page.locator('.battle-moves button').all()) {
      const box = await button.boundingBox()
      expect(box!.height).toBeGreaterThanOrEqual(44)
    }
  }
}

test('invited trainer buys a team, resumes a battle and earns the first badge', async ({
  page,
}, testInfo) => {
  // Only run registration against an explicitly configured disposable database.
  // eslint-disable-next-line playwright/no-skipped-test
  test.skip(
    !process.env.PLAYWRIGHT_ADVENTURE_CODE,
    'Requires an invitation from a disposable adventure preview database',
  )
  test.setTimeout(180000)
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'light' })
  await page.setViewportSize({ width: 375, height: 900 })
  await page.goto('/aventura')
  await expect(page.getByRole('heading', { name: 'Tu equipo', exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Crear entrenador', exact: true }).first().click()
  const username = `trainer_${Date.now()}`
  await page.getByLabel('Nombre de entrenador', { exact: true }).fill(username)
  await page.getByLabel('Contraseña', { exact: true }).fill('adventure-test-password')
  await page.getByLabel('Código de invitación', { exact: true }).fill('invalid-invitation-code')
  await page.getByRole('button', { name: 'Crear entrenador', exact: true }).last().click()
  await expect(page.getByRole('alert')).toContainText('invitación')
  await page
    .getByLabel('Código de invitación', { exact: true })
    .fill(process.env.PLAYWRIGHT_ADVENTURE_CODE!)
  await page.getByRole('button', { name: 'Crear entrenador', exact: true }).last().click()
  await expect(page.locator('.trainer-strip')).toContainText('1000 créditos')
  await page.locator('.adventure-empty').getByRole('link', { name: 'Catálogo' }).click()
  await expect(page).toHaveURL(/\/catalogo/)
  await expect(page.locator('.catalog-trainer')).toContainText('1000 créditos')
  await expect(page.locator('.results-bar')).toContainText('26 Pokémon')
  for (const width of [320, 375, 414, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    for (const button of await page.locator('.catalog-purchase button').all()) {
      const box = await button.boundingBox()
      expect(box!.height).toBeGreaterThanOrEqual(44)
    }
  }
  await page.goto('/catalogo?sort=price_asc')
  await expect(page.locator('.catalog-purchase strong').first()).toHaveText('100 créditos')
  await page.goto('/catalogo?sort=price_desc')
  await expect(page.locator('.catalog-purchase strong').first()).toHaveText('800 créditos')
  await page.goto('/catalogo')
  await page.getByRole('checkbox', { name: 'Solo Pokémon disponibles para combatir' }).uncheck()
  await expect(page.locator('.results-bar')).toContainText('1351 Pokémon')
  await expect(page.getByText('Todavía no disponible para combatir').first()).toBeVisible()
  await page.getByRole('checkbox', { name: 'Solo Pokémon disponibles para combatir' }).check()
  for (const name of ['Bulbasaur', 'Squirtle']) {
    await page.getByRole('button', { name: `Comprar a ${name}`, exact: true }).click()
    await expect(
      page
        .locator('.pokemon-card')
        .filter({ has: page.getByRole('heading', { name, exact: true }) })
        .getByRole('button'),
    ).toHaveAccessibleName('En tu colección')
  }
  await page.getByRole('link', { name: 'Charmander', exact: true }).click()
  await expect(page.locator('.detail-copy .catalog-purchase strong')).toHaveText('220 créditos')
  await expect(page.locator('.detail-price')).toHaveCount(0)
  await page.getByRole('button', { name: 'Comprar a Charmander', exact: true }).click()
  await expect(page.getByRole('button', { name: 'En tu colección', exact: true })).toBeDisabled()
  await page.getByRole('link', { name: 'Volver al catálogo', exact: true }).click()
  await page.reload()
  await expect(page.locator('.catalog-trainer')).toContainText('310 créditos')
  await page.setViewportSize({ width: 1280, height: 900 })
  await page.addStyleTag({ content: '#vue-devtools__anchor { display: none !important; }' })
  await page.screenshot({ path: testInfo.outputPath('catalog-trainer.png'), fullPage: true })
  await page.getByRole('link', { name: 'Mi equipo', exact: true }).click()
  for (const name of ['Bulbasaur', 'Squirtle', 'Charmander'])
    await page.getByRole('button', { name: `Seleccionar a ${name}`, exact: true }).click()
  await page.getByRole('button', { name: 'Guardar equipo', exact: true }).click()
  await expect(page.getByText('Equipo guardado', { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.locator('.team-slot.occupied')).toHaveCount(3)
  await page.getByRole('button', { name: 'Gimnasios', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Retar a Brock', exact: true })).toBeEnabled()
  await expect(page.locator('.gym-stop').nth(1).getByRole('button')).toBeDisabled()
  await page.getByRole('button', { name: 'Retar a Brock', exact: true }).click()
  await expect(page.locator('.battle-arena')).toBeVisible()
  await expect(page.locator('.player-sprite')).toHaveAttribute('src', /\/back\/1.png$/)
  await page.reload()
  await expect(page.locator('.battle-arena')).toBeVisible()
  await checkBattleWidths(page)
  await page.getByRole('combobox', { name: 'Idioma', exact: true }).click()
  await page.getByRole('option', { name: 'EN', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Use Vine whip', exact: true })).toBeVisible()
  await checkBattleWidths(page)
  await page.getByRole('combobox', { name: 'Language', exact: true }).click()
  await page.getByRole('option', { name: 'ES', exact: true }).click()
  await page.setViewportSize({ width: 375, height: 900 })
  await page.addStyleTag({ content: '#vue-devtools__anchor { display: none !important; }' })
  await page.locator('h1').click()
  await page.screenshot({ path: testInfo.outputPath('battle-mobile.png'), fullPage: true })
  await page.setViewportSize({ width: 1280, height: 900 })
  await page.screenshot({ path: testInfo.outputPath('battle-desktop.png'), fullPage: true })
  await page.emulateMedia({ colorScheme: 'dark' })
  await page.setViewportSize({ width: 1280, height: 900 })
  await page.screenshot({ path: testInfo.outputPath('battle-dark.png'), fullPage: true })
  // Commit a real turn, then lose only its HTTP response. Recovery must not replay it.
  await page.route(
    '**/api/v1/adventure/battles/*/turns',
    async (route) => {
      await route.fetch()
      await route.abort()
    },
    { times: 1 },
  )
  await page.getByRole('button', { name: 'Usar Látigo cepa', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('recuperado tu progreso')
  await expect(page.locator('.gym-intro')).toContainText('Turno 2')
  const me = await (await page.request.get('/api/v1/adventure/me')).json()
  const replay = await page.request.post(`/api/v1/adventure/battles/${me.battle_id}/turns`, {
    headers: { 'X-CSRF-Token': me.csrf_token },
    data: { revision: 0, kind: 'move', move: 'vine-whip' },
  })
  expect(replay.status()).toBe(409)
  await page.getByRole('button', { name: 'Volver a intentar', exact: true }).click()
  await expect(page.locator('.gym-intro')).toContainText('Turno 2')
  await page.emulateMedia({ reducedMotion: 'no-preference' })
  const move = page.getByRole('button', { name: 'Usar Látigo cepa', exact: true })
  await expect(move).toBeEnabled()
  await move.click()
  await expect(page.locator('.battle-arena')).toHaveAttribute('aria-busy', 'false')
  await expect(
    page.getByRole('heading', { name: '¡Medalla conseguida!', exact: true }),
  ).toBeVisible()
  await expect(page.getByText('Has ganado 150 créditos.', { exact: true })).toBeVisible()
  await expect(page.locator('.trainer-strip')).toContainText('1 / 6 medallas')
  await page.getByRole('button', { name: 'Volver a los gimnasios', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Retar a Misty', exact: true })).toBeEnabled()
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await expect(page.locator('.trainer-form')).toBeVisible()
  await page.getByLabel('Nombre de entrenador', { exact: true }).fill(username)
  await page.getByLabel('Contraseña', { exact: true }).fill('adventure-test-password')
  await page.getByRole('button', { name: 'Entrar', exact: true }).last().click()
  await expect(page.locator('.trainer-strip')).toContainText('1 / 6 medallas')
  expect(errors).toEqual([])
})
