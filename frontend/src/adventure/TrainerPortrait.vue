<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { UserRound } from 'lucide-vue-next'

const props = defineProps<{ gymId: number; leader: string }>()
const source = computed(() => `/studio/gyms/leader-${props.gymId}.png`)
const failed = ref(false)
watch(source, () => {
  failed.value = false
})
</script>

<template>
  <img
    v-if="source && !failed"
    class="trainer-portrait"
    :src="source"
    :alt="leader"
    width="96"
    height="96"
    decoding="async"
    @error="failed = true"
  />
  <UserRound v-else class="trainer-portrait portrait-fallback" :size="48" aria-hidden="true" />
</template>

<style>
.trainer-portrait {
  width: 112px;
  height: 112px;
  object-fit: contain;
  image-rendering: pixelated;
}
.portrait-fallback {
  padding: 30px;
  color: var(--muted-strong);
}
</style>
