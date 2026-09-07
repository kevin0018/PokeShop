<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Clock3, X } from 'lucide-vue-next'
const props = defineProps<{ message: string; event: object | null }>()
const emit = defineEmits<{ dismiss: [] }>(),
  { t } = useI18n()
const hovering = ref(false),
  focused = ref(false),
  paused = computed(() => hovering.value || focused.value),
  sequence = ref(0)
let remaining = 3000,
  started = 0,
  timer: ReturnType<typeof setTimeout> | undefined
function start() {
  started = Date.now()
  timer = setTimeout(() => emit('dismiss'), remaining)
}
watch(
  () => props.event,
  () => {
    clearTimeout(timer)
    remaining = 3000
    sequence.value++
    if (props.message && !paused.value) start()
  },
  { immediate: true },
)
watch(
  () => props.message,
  (value) => {
    if (!value) {
      clearTimeout(timer)
      hovering.value = false
      focused.value = false
    }
  },
)
watch(paused, (value) => {
  if (value) {
    clearTimeout(timer)
    remaining = Math.max(0, remaining - (Date.now() - started))
  } else if (props.message) start()
})
onUnmounted(() => clearTimeout(timer))
function blur(event: FocusEvent) {
  if (!(event.currentTarget as HTMLElement).contains(event.relatedTarget as Node))
    focused.value = false
}
</script>
<template>
  <div
    v-if="message"
    class="cart-notice"
    role="status"
    @mouseenter="hovering = true"
    @mouseleave="hovering = false"
    @focusin="focused = true"
    @focusout="blur"
  >
    <span class="notice-clock" aria-hidden="true"
      ><Clock3 :size="18" /><svg
        :key="sequence"
        class="notice-progress"
        :class="{ paused }"
        viewBox="0 0 36 36"
      >
        <circle cx="18" cy="18" r="16" /></svg></span
    ><span>{{ message }}</span
    ><button class="icon-button" :aria-label="t('close')" @click="emit('dismiss')">
      <X :size="18" />
    </button>
  </div>
</template>
<style>
.cart-notice {
  display: flex;
  align-items: center;
  gap: 14px;
}
.notice-clock {
  position: relative;
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}
.notice-progress {
  position: absolute;
  inset: 0;
  width: 36px;
  height: 36px;
  transform: rotate(-90deg);
}
.notice-progress circle {
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-dasharray: 100.53;
  stroke-dashoffset: 0;
  animation: notice-countdown 3s linear forwards;
}
.notice-progress.paused circle {
  animation-play-state: paused;
}
.cart-notice .icon-button {
  flex-shrink: 0;
}
@keyframes notice-countdown {
  to {
    stroke-dashoffset: 100.53;
  }
}
@media (prefers-reduced-motion: reduce) {
  .notice-progress {
    display: none;
  }
}
</style>
