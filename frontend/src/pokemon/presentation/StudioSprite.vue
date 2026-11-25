<script setup lang="ts">
import { computed } from 'vue'

// PokéAPI's Black/White poses, packed in rows of eight at 100 ms per frame.
const frames = { 6: 73, 25: 60, 94: 44 } as const
const props = defineProps<{ id: keyof typeof frames; tick: number }>()
const atlas = computed(() => {
  const columns = 8
  const count = frames[props.id]
  const rows = Math.ceil(count / columns)
  const frame = props.tick % count
  return {
    backgroundImage: `url(/studio/motion-${props.id}.png)`,
    backgroundSize: `${columns * 100}% ${rows * 100}%`,
    backgroundPosition: `${((frame % columns) / (columns - 1)) * 100}% ${(Math.floor(frame / columns) / (rows - 1)) * 100}%`,
  }
})
</script>
<template><span class="studio-sprite" :style="atlas" aria-hidden="true"></span></template>
<style scoped>
.studio-sprite {
  display: block;
  width: 100%;
  height: 100%;
  background-repeat: no-repeat;
  image-rendering: pixelated;
}
</style>
