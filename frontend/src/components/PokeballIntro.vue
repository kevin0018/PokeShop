<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { DialogRoot, DialogPortal, DialogContent, DialogTitle, DialogClose } from 'reka-ui'
const { t } = useI18n()
const key = 'pokeshop.intro.v1'
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
let seen = false
try {
  seen = sessionStorage.getItem(key) === 'seen'
  sessionStorage.setItem(key, 'seen')
} catch {
  seen = document.documentElement.dataset.introSeen === 'true'
}
document.documentElement.dataset.introSeen = 'true'
const open = ref(!seen && !motion.matches)
let timer: ReturnType<typeof setTimeout> | undefined
function finish() {
  open.value = false
  clearTimeout(timer)
}
function visibility() {
  if (document.hidden) finish()
}
function reduced() {
  if (motion.matches) finish()
}
onMounted(() => {
  if (open.value) timer = setTimeout(finish, 1200)
  motion.addEventListener('change', reduced)
  document.addEventListener('visibilitychange', visibility)
})
onUnmounted(() => {
  clearTimeout(timer)
  motion.removeEventListener('change', reduced)
  document.removeEventListener('visibilitychange', visibility)
})
</script>
<template>
  <DialogRoot :open="open" @update:open="!$event && finish()"
    ><DialogPortal
      ><DialogContent class="pokeball-intro" :aria-describedby="undefined" @escape-key-down="finish"
        ><DialogTitle class="sr-only">{{ t('welcomeIntro') }}</DialogTitle>
        <div class="intro-half intro-top" aria-hidden="true" />
        <div class="intro-half intro-bottom" aria-hidden="true" />
        <div class="intro-core" aria-hidden="true" />
        <DialogClose class="intro-skip" @click="finish"
          >{{ t('skipIntro') }} →</DialogClose
        ></DialogContent
      ></DialogPortal
    ></DialogRoot
  >
</template>
<style>
.pokeball-intro {
  position: fixed;
  inset: 0;
  z-index: 200;
  isolation: isolate;
  overflow: hidden;
}
.intro-half {
  position: absolute;
  left: 0;
  width: 100%;
  height: 50%;
  background: #f6f0df;
  animation: ball-open-bottom 1.2s cubic-bezier(0.65, 0, 0.2, 1) both;
}
.intro-top {
  top: 0;
  background: radial-gradient(ellipse at 35% 20%, #e8696d, #a62442);
  border-bottom: 10px solid #241c32;
  animation-name: ball-open-top;
}
.intro-bottom {
  bottom: 0;
  border-top: 10px solid #241c32;
}
.intro-core {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 110px;
  height: 110px;
  border: 14px solid #241c32;
  border-radius: 50%;
  background: #fff9e9;
  transform: translate(-50%, -50%);
  box-shadow: inset 0 0 0 8px #d9d0ca;
  animation: ball-core 1.2s ease-in-out both;
}
.intro-skip {
  position: absolute;
  top: 24px;
  right: 24px;
  min-height: 44px;
  padding: 10px 20px;
  border-radius: 30px;
  border: 1px solid #fff8;
  background: #241c32;
  color: #fff9e9;
  font: inherit;
  cursor: pointer;
}
@keyframes ball-open-top {
  0%,
  15% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-101%);
  }
}
@keyframes ball-open-bottom {
  0%,
  15% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(101%);
  }
}
@keyframes ball-core {
  0%,
  15% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
  }
  55% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(2);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(2);
  }
}
@media (prefers-reduced-motion: reduce) {
  .pokeball-intro {
    display: none;
  }
  .intro-half,
  .intro-core {
    animation: none;
  }
}
</style>
