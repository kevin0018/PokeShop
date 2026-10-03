<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ src: string; fallback?: string; name: string }>()
const { t } = useI18n()
const useFallback = ref(false)
const failed = ref(false)
watch(
  () => props.src,
  () => {
    useFallback.value = false
    failed.value = false
  },
)
function recover() {
  if (!useFallback.value && props.fallback && props.fallback !== props.src) useFallback.value = true
  else failed.value = true
}
</script>

<template>
  <img v-if="!failed" :src="useFallback ? fallback : src" :alt="name" @error="recover" />
  <span v-else class="battle-image-fallback" role="img" :aria-label="name"
    >{{ name }}<small>{{ t('imageMissing') }}</small></span
  >
</template>
