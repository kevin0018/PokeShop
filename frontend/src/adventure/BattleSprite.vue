<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  id: number
  back?: boolean
  src: string
  fallback?: string
  name: string
}>()
// Atlas cell, front silhouette height and back silhouette height in native pixels.
const frames: Record<number, [number, number, number]> = {
  1: [0, 33, 32],
  2: [1, 42, 43],
  3: [2, 54, 44],
  4: [3, 39, 43],
  5: [4, 47, 49],
  6: [5, 62, 56],
  7: [6, 36, 33],
  8: [7, 46, 44],
  9: [8, 53, 44],
  16: [9, 37, 48],
  25: [10, 49, 49],
  26: [11, 60, 48],
  37: [12, 39, 46],
  43: [13, 36, 47],
  54: [14, 45, 50],
  63: [15, 40, 39],
  65: [16, 61, 52],
  66: [17, 42, 40],
  74: [18, 26, 41],
  92: [19, 51, 36],
  94: [20, 45, 44],
  95: [21, 59, 63],
  100: [22, 25, 36],
  110: [23, 54, 40],
  114: [24, 47, 35],
  121: [25, 47, 36],
  133: [26, 40, 43],
  134: [27, 53, 43],
  135: [28, 42, 51],
  136: [29, 44, 53],
  147: [30, 35, 46],
  149: [31, 64, 52],
}
const frame = computed(() => frames[props.id])
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
  <span
    class="fighter-figure"
    :data-height="frame ? frame[back ? 2 : 1] / 64 : 0.7"
    :data-view="back ? 'back' : 'front'"
  >
    <span
      v-if="frame"
      class="fighter-pixels"
      role="img"
      :aria-label="name"
      :style="{
        backgroundImage: `url('/studio/gyms/party-${back ? 'back' : 'front'}.png')`,
        backgroundPosition: `${((frame[0] % 8) / 7) * 100}% ${(Math.floor(frame[0] / 8) / 3) * 100}%`,
      }"
    ></span>
    <img v-else-if="!failed" :src="useFallback ? fallback : src" :alt="name" @error="recover" />
    <span v-else class="battle-image-fallback" role="img" :aria-label="name"
      >{{ name }}<small>{{ t('imageMissing') }}</small></span
    >
  </span>
</template>
<style scoped>
.fighter-figure > * {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center bottom;
  image-rendering: pixelated;
  transform-origin: center bottom;
}
.fighter-pixels {
  background-size: 800% 400%;
  background-repeat: no-repeat;
}
</style>
