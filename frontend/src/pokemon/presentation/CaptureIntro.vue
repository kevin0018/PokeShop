<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { SkipForward } from 'lucide-vue-next'
import StudioSprite from './StudioSprite.vue'

const props = defineProps<{ id: 6 | 25 | 94; tick: number; target?: HTMLElement }>()
const emit = defineEmits<{ reveal: []; finish: [] }>()
const { t } = useI18n()
const dialog = ref<HTMLDialogElement>()
const ball = ref<HTMLElement>()
const actor = ref<HTMLElement>()
const sprite = ref<HTMLElement>()
const dark = ref<HTMLElement>()
const animations: Animation[] = []
let ended = false

function animate(
  el: HTMLElement,
  frames: Keyframe[],
  duration: number,
  delay = 0,
  easing = 'ease-out',
) {
  const effect = el.animate(frames, { duration, delay, easing, fill: 'both' })
  animations.push(effect)
  return effect
}
function finish() {
  if (ended) return
  ended = true
  dialog.value?.close()
  emit('finish')
}
async function release() {
  const box = dialog.value!
  delete document.documentElement.dataset.captureBoot
  box.showModal()
  // Each exposure holds one cel. Reusing the resting pose gives the two rocks a beat apart.
  const exposures = [
    [0, 0],
    [280, 1],
    [370, 2],
    [510, 3],
    [600, 0],
    [790, 4],
    [880, 5],
    [1030, 6],
    [1130, 0],
    [1270, 7],
    [1360, 8],
    [1440, 9],
    [1510, 10],
    [1580, 11],
    [1650, 12],
    [1730, 13],
    [1820, 14],
    [1940, 15],
  ] as const
  const duration = 1940
  animate(
    ball.value!,
    exposures.map(([time, cel]) => ({
      offset: time / duration,
      backgroundPositionX: `${(cel / 15) * 100}%`,
      easing: 'steps(1, end)',
    })),
    duration,
    0,
    'linear',
  )
  const emergence = animate(
    sprite.value!,
    [
      { opacity: 0, transform: 'scale(.025)', filter: 'brightness(0) invert(1)' },
      { opacity: 1, transform: 'scale(.87)', filter: 'brightness(0) invert(1)', offset: 0.47 },
      { opacity: 1, transform: 'scale(1.04)', filter: 'brightness(1.25)', offset: 0.8 },
      { opacity: 1, transform: 'scale(1)', filter: 'brightness(1)' },
    ],
    650,
    1650,
  )
  await emergence.finished
  if (ended) return
  const from = actor.value!.getBoundingClientRect()
  const to = props.target?.getBoundingClientRect()
  if (!to?.width) return finish()
  emit('reveal')
  animate(
    dark.value!,
    [
      { clipPath: 'polygon(-60% 0, 165% 0, 130% 100%, -95% 100%)' },
      { clipPath: 'polygon(137% 0, 165% 0, 130% 100%, 102% 100%)' },
    ],
    560,
    40,
    'cubic-bezier(.7,0,.2,1)',
  )
  const flight = animate(
    actor.value!,
    [
      { transform: 'translate(0,0) scale(1)' },
      {
        transform: `translate(${to.x - from.x + (to.width - from.width) / 2}px, ${to.y - from.y + (to.height - from.height) / 2}px) scale(${to.width / from.width})`,
      },
    ],
    670,
    0,
    'cubic-bezier(.65,0,.18,1)',
  )
  await flight.finished
  finish()
}
onMounted(() => {
  release().catch(() => {
    if (!ended) finish()
  })
})
onUnmounted(() => {
  ended = true
  animations.forEach((animation) => animation.cancel())
  dialog.value?.close()
  delete document.documentElement.dataset.captureBoot
})
</script>
<template>
  <dialog
    ref="dialog"
    class="capture-intro"
    :aria-label="t('studio.replay')"
    @cancel.prevent="finish"
  >
    <div ref="dark" class="cinema-black"></div>
    <div ref="ball" class="capture-ball" aria-hidden="true"></div>
    <div ref="actor" class="cinema-actor">
      <div ref="sprite"><StudioSprite :id="id" :tick="tick" /></div>
    </div>
    <button autofocus class="skip-capture" @click="finish">
      {{ t('studio.skip') }}<SkipForward :size="15" />
    </button>
  </dialog>
</template>
<style scoped>
.capture-intro[open] {
  display: block;
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  max-width: none;
  max-height: none;
  margin: 0;
  padding: 0;
  border: 0;
  overflow: clip;
  background: transparent;
  color: white;
}
.capture-intro::backdrop {
  background: transparent;
}
:global(body:has(.capture-intro[open])) {
  overflow: hidden;
}
.cinema-black {
  position: absolute;
  inset: 0;
  background: #030304;
  pointer-events: none;
}
.capture-ball {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 256px;
  height: 256px;
  translate: -50% -50%;
  background: url('../../assets/capture-cels.png') 0 0 / 1600% 100% no-repeat;
  image-rendering: pixelated;
}
.cinema-actor {
  width: clamp(150px, 22vmin, 245px);
  aspect-ratio: 1;
  position: absolute;
  left: 50%;
  top: 50%;
  translate: -50% -50%;
}
.cinema-actor > div {
  height: 100%;
}
.skip-capture {
  position: absolute;
  bottom: max(20px, env(safe-area-inset-bottom));
  right: clamp(16px, 3vw, 48px);
  background: #09090b;
  border: 1px solid #5b5960;
  color: #d1cdd2;
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 44px;
  padding: 0 14px;
  font: 600 0.75rem var(--font-body);
}
.skip-capture:focus-visible {
  outline: 1px solid #969097;
  outline-offset: 3px;
}
.skip-capture:focus:not(:focus-visible) {
  outline: 0;
}
</style>
