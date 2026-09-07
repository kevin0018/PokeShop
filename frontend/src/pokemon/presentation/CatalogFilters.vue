<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  DialogRoot,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from 'reka-ui'
import { SlidersHorizontal, X } from 'lucide-vue-next'
import AppSelect from '@/components/AppSelect.vue'
import { typeName } from '@/shared/presentation/format'
const props = defineProps<{
  metadata: {
    types: string[]
    generations: number[]
    regions?: { id: string; names: Record<string, string> }[]
  }
}>()
const { t, locale } = useI18n(),
  route = useRoute(),
  router = useRouter()
const open = ref(false),
  draft = ref<Record<string, string>>({})
const fields = computed(() => [
  {
    key: 'type',
    label: t('filterType'),
    options: [
      { value: '', label: t('allTypes') },
      ...props.metadata.types.map((v) => ({ value: v, label: typeName(v) })),
    ],
  },
  {
    key: 'region',
    label: t('region'),
    options: [
      { value: '', label: t('allRegions') },
      ...(props.metadata.regions ?? []).map((r) => ({
        value: r.id,
        label: r.names[locale.value] ?? r.id,
      })),
    ],
  },
  {
    key: 'generation',
    label: t('generationLabel'),
    options: [
      { value: '', label: t('allGenerations') },
      ...props.metadata.generations.map((g) => ({
        value: String(g),
        label: t('generationNumber', { n: g }),
      })),
    ],
  },
  {
    key: 'forms',
    label: t('forms'),
    options: [
      { value: '', label: t('allForms') },
      { value: 'default', label: t('defaultForms') },
      { value: 'alternative', label: t('alternativeForms') },
    ],
  },
  {
    key: 'sort',
    label: t('sort'),
    options: [
      'number',
      'price_asc',
      'price_desc',
      'name',
      'weight_asc',
      'weight_desc',
      'height_asc',
      'height_desc',
    ].map((v, i) => ({
      value: v,
      label: t(
        [
          'sortNumber',
          'sortLow',
          'sortHigh',
          'sortName',
          'weightLow',
          'weightHigh',
          'heightLow',
          'heightHigh',
        ][i]!,
      ),
    })),
  },
])
const active = computed(() =>
  fields.value.filter((f) => route.query[f.key] && route.query[f.key] !== 'number'),
)
function setOpen(value: boolean) {
  if (value)
    draft.value = Object.fromEntries(
      fields.value.map((f) => [
        f.key,
        String(route.query[f.key] ?? (f.key === 'sort' ? 'number' : '')),
      ]),
    )
  open.value = value
}
function apply() {
  void router.replace({
    query: {
      ...route.query,
      ...Object.fromEntries(Object.entries(draft.value).map(([k, v]) => [k, v || undefined])),
      page: undefined,
    },
  })
  open.value = false
}
function remove(key: string) {
  void router.replace({ query: { ...route.query, [key]: undefined, page: undefined } })
}
</script>
<template>
  <div class="filter-control">
    <DialogRoot :open="open" @update:open="setOpen">
      <DialogTrigger class="button secondary"
        ><SlidersHorizontal :size="18" />{{ t('filters')
        }}<span v-if="active.length">({{ active.length }})</span></DialogTrigger
      >
      <DialogPortal
        ><DialogOverlay class="filter-overlay" /><DialogContent class="filter-panel">
          <div class="filter-heading">
            <DialogTitle>{{ t('filters') }}</DialogTitle
            ><DialogClose class="icon-button" :aria-label="t('close')"><X /></DialogClose>
          </div>
          <DialogDescription>{{ t('catalogIntro') }}</DialogDescription>
          <div v-for="field in fields" :key="field.key" class="filter-field">
            <span>{{ field.label }}</span
            ><AppSelect
              :model-value="draft[field.key] ?? ''"
              :label="field.label"
              :options="field.options"
              @update:model-value="draft[field.key] = $event"
            />
          </div>
          <div class="filter-actions">
            <DialogClose class="button secondary">{{ t('cancel') }}</DialogClose
            ><button class="button primary" @click="apply">{{ t('apply') }}</button>
          </div>
        </DialogContent></DialogPortal
      ></DialogRoot
    >
    <div v-if="active.length" class="active-filters">
      <button
        v-for="field in active"
        :key="field.key"
        class="filter-chip"
        :aria-label="t('removeFilter') + ': ' + field.label"
        @click="remove(field.key)"
      >
        {{
          field.options.find((o) => o.value === route.query[field.key])?.label ??
          route.query[field.key]
        }}<X :size="13" />
      </button>
    </div>
  </div>
</template>
<style>
.filter-control {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.filter-overlay {
  position: fixed;
  inset: 0;
  background: #120c2488;
  z-index: 100;
}
.filter-panel {
  position: fixed;
  right: 0;
  top: 0;
  height: 100dvh;
  width: min(440px, 100vw);
  background: var(--surface);
  color: var(--ink);
  z-index: 110;
  padding: 32px;
  overflow: auto;
  box-shadow: -20px 0 80px #0002;
}
.filter-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-heading h2 {
  font-size: 2rem;
  margin: 0;
}
.filter-field {
  display: grid;
  gap: 9px;
  margin: 24px 0;
}
.filter-field > span {
  font-size: 0.85rem;
  font-weight: 700;
}
.filter-field .custom-select {
  width: 100%;
  justify-content: space-between;
}
.filter-actions {
  display: flex;
  gap: 12px;
  position: sticky;
  bottom: -32px;
  background: var(--surface);
  padding: 20px 0;
}
.filter-actions > * {
  flex: 1;
}
.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: inherit;
  border: 0;
  cursor: pointer;
  min-height: 44px;
  min-width: 44px;
}
.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.filter-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--line);
  background: var(--lavender);
  color: var(--ink);
  border-radius: 30px;
  padding: 8px 12px;
  cursor: pointer;
}
.select-menu {
  z-index: 130 !important;
}
@media (max-width: 540px) {
  .filter-panel {
    padding: 24px;
  }
  .filter-actions {
    bottom: -24px;
  }
}
</style>
