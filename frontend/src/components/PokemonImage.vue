<script setup lang="ts">
import { ref, watch } from 'vue'
const props = defineProps<{ src: string; name: string }>()
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
    :src="src"
    :alt="name"
    width="475"
    height="475"
    loading="lazy"
    @error="failed = true"
  />
  <span v-else class="image-fallback" role="img" :aria-label="name">Imagen no disponible</span>
</template>
