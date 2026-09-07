<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { X } from 'lucide-vue-next'
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
    <span class="notice-disc" aria-hidden="true"
      ><span :key="sequence" class="notice-pie" :class="{ paused }" /></span
    ><span>{{ message }}</span
    ><button class="icon-button" :aria-label="t('close')" @click="emit('dismiss')">
      <X :size="18" />
    </button>
  </div>
</template>
<style>
@property --notice-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 360deg;
}
.cart-notice {
  display: flex;
  align-items: center;
  gap: 12px;
}
.notice-disc {
  width: 25px;
  height: 25px;
  flex-shrink: 0;
  border-radius: 50%;
  background: #ffffff26;
  overflow: hidden;
}
.notice-pie {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(currentColor var(--notice-angle), transparent 0);
  animation: notice-slice 3s linear forwards;
}
.notice-pie.paused {
  animation-play-state: paused;
}
.cart-notice .icon-button {
  flex-shrink: 0;
}
@keyframes notice-slice {
  from {
    --notice-angle: 360deg;
  }
  to {
    --notice-angle: 0deg;
  }
}
@media (prefers-reduced-motion: reduce) {
  .notice-pie {
    animation: none;
    background: currentColor;
    opacity: 0.65;
  }
}
</style>
