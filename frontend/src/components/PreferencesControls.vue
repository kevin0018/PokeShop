<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Languages, Moon, Sun } from 'lucide-vue-next'
import { useThemeStore } from '@/shared/application/theme'
const { t, locale } = useI18n({ useScope: 'global' })
const theme = useThemeStore()
</script>
<template>
  <div class="preferences-controls">
    <label class="preference-field"
      ><Languages :size="16" aria-hidden="true" /><span class="sr-only">{{ t('language') }}</span>
      <select v-model="locale">
        <option value="es" lang="es">Español</option>
        <option value="en" lang="en">English</option>
      </select>
    </label>
    <label class="preference-field"
      ><Moon v-if="theme.resolved === 'dark'" :size="16" aria-hidden="true" /><Sun
        v-else
        :size="16"
        aria-hidden="true"
      /><span class="sr-only">{{ t('theme') }}</span>
      <select v-model="theme.preference">
        <option value="system">{{ t('system') }}</option>
        <option value="light">{{ t('light') }}</option>
        <option value="dark">{{ t('dark') }}</option>
      </select>
    </label>
  </div>
</template>
