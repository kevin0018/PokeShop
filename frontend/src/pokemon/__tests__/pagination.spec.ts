import { mount, flushPromises } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { afterEach, expect, it, vi } from 'vitest'
import CatalogView from '../presentation/CatalogView.vue'
import { i18n } from '@/i18n'
import CatalogFilters from '../presentation/CatalogFilters.vue'
import { DialogRoot } from 'reka-ui'
import AppSelect from '@/components/AppSelect.vue'
afterEach(() => vi.unstubAllGlobals())
it('stores filters and pagination in the URL and aborts stale requests', async () => {
  const signals: AbortSignal[] = []
  vi.stubGlobal(
    'fetch',
    vi.fn(async (url: string, init?: RequestInit) => {
      if (init?.signal) signals.push(init.signal)
      return {
        ok: true,
        json: async () =>
          url.includes('metadata')
            ? { types: ['agua'], generations: [1, 2] }
            : { items: [], total: 100 },
      }
    }),
  )
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/catalogo', component: CatalogView }],
  })
  await router.push('/catalogo?page=3')
  await router.isReady()
  const wrapper = mount(CatalogView, { global: { plugins: [createPinia(), i18n, router] } })
  await flushPromises()
  const previous = signals[0]!
  await wrapper.get('input').setValue('Pika')
  await flushPromises()
  expect(router.currentRoute.value.query).toMatchObject({ q: 'Pika' })
  expect(router.currentRoute.value.query.page).toBeUndefined()
  expect(previous.aborted).toBe(true)
  wrapper.getComponent(CatalogFilters).getComponent(DialogRoot).vm.$emit('update:open', true)
  await flushPromises()
  wrapper.findAllComponents(AppSelect)[2]!.vm.$emit('update:modelValue', '2')
  await flushPromises()
  expect(router.currentRoute.value.query.generation).toBeUndefined()
  const apply = document.querySelector('.filter-actions .primary') as HTMLButtonElement
  apply.click()
  await flushPromises()
  expect(router.currentRoute.value.query).toMatchObject({ q: 'Pika', generation: '2' })
  wrapper.unmount()
})
