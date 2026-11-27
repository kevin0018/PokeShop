<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { computed, ref, watch } from 'vue'
const props = withDefaults(
  defineProps<{ src: string; name: string; loading?: 'lazy' | 'eager' }>(),
  { loading: 'lazy' },
)
// Use the Dream World illustration for Charmeleon across the profile and its previews.
const artwork = computed(() =>
  props.src.endsWith('/official-artwork/5.png') ? '/artwork/charmeleon.png' : props.src,
)
const failed = ref(false)
watch(
  () => props.src,
  () => {
    failed.value = false
  },
)
</script>
<template>
  <img
    v-if="!failed"
    :src="artwork"
    :alt="name"
    width="475"
    height="475"
    :loading="loading"
    @error="failed = true"
  />
  <span v-else class="image-fallback" role="img" :aria-label="name">{{ t('imageMissing') }}</span>
</template>
