<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Languages, Moon, Sun, Monitor } from 'lucide-vue-next'
import { useThemeStore } from '@/shared/application/theme'
import type { Theme } from '@/shared/infrastructure/preferences'
import AppSelect from './AppSelect.vue'
import { ref } from 'vue'
const { t, locale } = useI18n({ useScope: 'global' })
const theme = useThemeStore()
const control = ref<HTMLElement>()
function change(value: string) {
  void theme.change(value as Theme, control.value?.getBoundingClientRect())
}
</script>
<template>
  <div class="preferences-controls">
    <div class="preference-control">
      <AppSelect
        v-model="locale"
        :label="t('language')"
        :options="[
          { value: 'es', label: 'ES' },
          { value: 'en', label: 'EN' },
        ]"
        ><Languages :size="16" aria-hidden="true" /></AppSelect
      ><span class="focus-hint">{{ t('language') }}</span>
    </div>
    <div ref="control" class="preference-control">
      <AppSelect
        :model-value="theme.preference"
        :label="t('theme')"
        :options="['system', 'light', 'dark'].map((value) => ({ value, label: t(value) }))"
        @update:model-value="change"
        ><Monitor v-if="theme.preference === 'system'" :size="16" aria-hidden="true" /><Moon
          v-else-if="theme.resolved === 'dark'"
          :size="16"
          aria-hidden="true" /><Sun v-else :size="16" aria-hidden="true" /></AppSelect
      ><span class="focus-hint">{{ t('theme') }}</span>
    </div>
  </div>
</template>
