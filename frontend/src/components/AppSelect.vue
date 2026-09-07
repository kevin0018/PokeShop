<script setup lang="ts">
import {
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectPortal,
  SelectContent,
  SelectViewport,
  SelectItem,
  SelectItemText,
  SelectItemIndicator,
  SelectIcon,
} from 'reka-ui'
import { Check, ChevronDown } from 'lucide-vue-next'
defineProps<{
  modelValue: string
  label: string
  options: { value: string; label: string; image?: string }[]
}>()
defineEmits<{ 'update:modelValue': [value: string] }>()
</script>
<template>
  <SelectRoot
    :model-value="modelValue || '__all'"
    @update:model-value="
      $emit('update:modelValue', String($event) === '__all' ? '' : String($event))
    "
  >
    <SelectTrigger class="custom-select" :aria-label="label" :title="label"
      ><slot /><SelectValue /><SelectIcon><ChevronDown :size="14" /></SelectIcon
    ></SelectTrigger>
    <SelectPortal
      ><SelectContent class="select-menu" position="popper" :side-offset="8"
        ><SelectViewport>
          <SelectItem
            v-for="option in options"
            :key="option.value"
            class="select-option"
            :value="option.value || '__all'"
            ><img
              v-if="option.image"
              :src="option.image"
              alt=""
              width="32"
              height="32" /><SelectItemText>{{ option.label }}</SelectItemText
            ><SelectItemIndicator><Check :size="16" /></SelectItemIndicator
          ></SelectItem> </SelectViewport></SelectContent
    ></SelectPortal>
  </SelectRoot>
</template>
