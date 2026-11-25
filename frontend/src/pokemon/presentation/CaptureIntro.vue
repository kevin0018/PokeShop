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
const lid = ref<HTMLElement>()
const base = ref<HTMLElement>()
const core = ref<HTMLElement>()
const actor = ref<HTMLElement>()
const sprite = ref<HTMLElement>()
const dark = ref<HTMLElement>()
const light = ref<HTMLElement>()
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
  // Rock around the contact point, settle, then split the two shells at the seam.
  animate(
    ball.value!,
    [
      { transform: 'rotate(0deg)' },
      { transform: 'rotate(-24deg)', offset: 0.17 },
      { transform: 'rotate(15deg)', offset: 0.32 },
      { transform: 'rotate(0deg)', offset: 0.43 },
      { transform: 'rotate(0deg)', offset: 0.55 },
      { transform: 'rotate(21deg)', offset: 0.69 },
      { transform: 'rotate(-11deg)', offset: 0.83 },
      { transform: 'rotate(0deg)' },
    ],
    1040,
    270,
    'ease-in-out',
  )
  animate(
    lid.value!,
    [
      { transform: 'translateY(0) rotate(0)' },
      { transform: 'translate(-9%,-75%) rotate(-36deg)', opacity: 0 },
    ],
    530,
    1370,
  )
  animate(
    base.value!,
    [
      { transform: 'none', opacity: 1 },
      { transform: 'translateY(52%) rotate(12deg)', opacity: 0 },
    ],
    560,
    1440,
  )
  animate(
    core.value!,
    [
      { transform: 'scale(.025,.005)', opacity: 0 },
      { transform: 'scale(.65,.08)', opacity: 0.94, offset: 0.25 },
      { transform: 'scale(1)', opacity: 1, offset: 0.58 },
      { transform: 'scale(1.45)', opacity: 0 },
    ],
    850,
    1390,
  )
  animate(light.value!, [{ opacity: 1 }, { opacity: 0 }], 720, 1440)
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
    <div ref="light" class="ball-light" aria-hidden="true"></div>
    <div ref="ball" class="capture-ball" aria-hidden="true">
      <div ref="lid" class="capsule-top"><i></i></div>
      <div ref="base" class="capsule-bottom"></div>
    </div>
    <div ref="core" class="capsule-energy"></div>
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
.cinema-black,
.ball-light {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.cinema-black {
  background: #030304;
}
.ball-light {
  background:
    radial-gradient(ellipse 78px 10px at 50% calc(50% + 58px), #88819856, transparent),
    radial-gradient(ellipse 120px 150px at 49% 47%, #a4a4b80e, transparent);
}
.capture-ball {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 108px;
  aspect-ratio: 1;
  translate: -50% -50%;
  transform-origin: center 90%;
  filter: drop-shadow(0 9px 6px #0009);
}
.capsule-top,
.capsule-bottom {
  position: absolute;
  left: 0;
  width: 100%;
  height: 50%;
}
.capsule-top {
  top: 0;
  z-index: 2;
  border-radius: 100px 100px 0 0;
  background:
    radial-gradient(ellipse at 34% 29%, #fff6f3 0%, #ffbbb4 3%, #fb6563 10%, transparent 32%),
    radial-gradient(ellipse at 38% 40%, #fa4741 8%, #b32427 50%, #510f18 80%, #200c11);
  border-bottom: 4px solid #211b24;
  box-shadow: inset 1px 2px 2px #ffd4c98c;
  transform-origin: 0 100%;
}
.capsule-top i {
  position: absolute;
  left: 39%;
  bottom: -14px;
  width: 25%;
  aspect-ratio: 1;
  border-radius: 50%;
  border: 5px solid #201c24;
  background: radial-gradient(circle at 35% 27%, white, #c7c2c2 64%, #847d87);
  box-shadow: 0 0 0 1px #766477;
}
.capsule-bottom {
  bottom: 0;
  border-top: 3px solid #16141b;
  border-radius: 0 0 100px 100px;
  background: radial-gradient(ellipse at 30% 2%, #edece7, #c2bdba 32%, #776f76 65%, #302837 88%);
}
.capsule-energy {
  position: absolute;
  left: 50%;
  top: 50%;
  width: min(440px, 85vw);
  aspect-ratio: 1;
  translate: -50% -50%;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    #fff 0 9%,
    #fff9edfa 17%,
    #fffce2a6 32%,
    #fffaf73a 46%,
    transparent 68%
  );
  opacity: 0;
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
