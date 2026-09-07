<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowUpRight, ArrowRight, Pause, Play } from 'lucide-vue-next'
const { t } = useI18n()
const starters = [
  { id: 1, name: 'Bulbasaur', type: 'planta' },
  { id: 4, name: 'Charmander', type: 'fuego' },
  { id: 7, name: 'Squirtle', type: 'agua' },
]
const scene = ref<HTMLElement>(),
  paused = ref(false),
  visible = ref(false),
  hidden = ref(document.hidden),
  reduced = ref(true)
const running = computed(() => !paused.value && visible.value && !hidden.value && !reduced.value)
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
let observer: IntersectionObserver | undefined
const updateMotion = () => {
  reduced.value = motion.matches
  reset()
}
const visibility = () => {
  hidden.value = document.hidden
}
function pointer(event: PointerEvent) {
  if (!running.value || !window.matchMedia('(min-width: 769px) and (pointer: fine)').matches) return
  const r = scene.value!.getBoundingClientRect()
  scene.value!.style.setProperty('--dx', `${(event.clientX - r.x - r.width / 2) * 0.025}px`)
  scene.value!.style.setProperty('--dy', `${(event.clientY - r.y - r.height / 2) * 0.025}px`)
}
function reset() {
  scene.value?.style.setProperty('--dx', '0px')
  scene.value?.style.setProperty('--dy', '0px')
}
function toggle() {
  paused.value = !paused.value
  reset()
}
onMounted(() => {
  updateMotion()
  motion.addEventListener('change', updateMotion)
  document.addEventListener('visibilitychange', visibility)
  observer = new IntersectionObserver(([entry]) => {
    visible.value = !!entry?.isIntersecting
  })
  if (scene.value) observer.observe(scene.value)
})
onUnmounted(() => {
  observer?.disconnect()
  motion.removeEventListener('change', updateMotion)
  document.removeEventListener('visibilitychange', visibility)
})
</script>
<template>
  <section
    ref="scene"
    class="starter-home"
    :data-running="running"
    @pointermove="pointer"
    @pointerleave="reset"
  >
    <div class="starter-haze" aria-hidden="true" />
    <div class="starter-heading">
      <p>POKÉSHOP · {{ t('originalTrio') }}</p>
      <h1>{{ t('starterHeadline') }}</h1>
    </div>
    <div class="starter-scene" :data-running="running">
      <span class="starter-landmark" aria-hidden="true">KANTO</span>
      <RouterLink
        v-for="starter in starters"
        :key="starter.id"
        :to="`/pokemon/${starter.id}`"
        class="hero-starter pokemon-palette"
        :data-type="starter.type"
        :aria-label="t('viewPokemon', { name: starter.name })"
      >
        <span class="starter-aura" aria-hidden="true" />
        <img
          :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${starter.id}.png`"
          :alt="starter.name"
          width="475"
          height="475"
          fetchpriority="high"
        />
        <span class="starter-name"
          ><small>#{{ String(starter.id).padStart(3, '0') }}</small
          >{{ starter.name }}<ArrowUpRight :size="18"
        /></span>
      </RouterLink>
    </div>
    <div class="starter-bottom">
      <RouterLink class="starter-catalog" to="/catalogo"
        >{{ t('exploreCatalog') }}<ArrowRight :size="22"
      /></RouterLink>
      <RouterLink class="starter-kanto" to="/catalogo?region=kanto"
        >{{ t('visitKanto') }}<ArrowUpRight :size="16"
      /></RouterLink>
      <button
        v-if="!reduced"
        class="scene-toggle icon-button"
        :aria-label="t(paused ? 'resumeScene' : 'pauseScene')"
        :title="t(paused ? 'resumeScene' : 'pauseScene')"
        :aria-pressed="paused"
        @click="toggle"
      >
        <Play v-if="paused" :size="18" /><Pause v-else :size="18" />
      </button>
    </div>
  </section>
</template>
<style>
.main-content.home-main {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}
.starter-home {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: calc(100svh - 88px);
  display: grid;
  grid-template-rows: auto 1fr auto;
  background: #f0edf6;
  color: #352644;
  padding: 42px 0 32px;
}
[data-theme='dark'] .starter-home {
  background: #21182e;
  color: #f4edf9;
}
.starter-haze {
  position: absolute;
  inset: -12%;
  z-index: -1;
  background:
    radial-gradient(ellipse at 18% 66%, #64b68c66, transparent 42%),
    radial-gradient(ellipse at 53% 54%, #eab06d55, transparent 38%),
    radial-gradient(ellipse at 88% 65%, #74bddd77, transparent 42%);
  transform: translate(var(--dx, 0px), var(--dy, 0px));
  animation: starter-light 12s ease-in-out infinite alternate;
  animation-play-state: paused;
}
.starter-home[data-running='true'] .starter-haze {
  animation-play-state: running;
}
.starter-heading {
  text-align: center;
  position: relative;
  z-index: 2;
  padding: 0 24px;
}
.starter-heading p {
  font-family: monospace;
  font-size: 0.7rem;
  letter-spacing: 0.22em;
  margin: 0 0 14px;
}
.starter-heading h1 {
  font-size: clamp(2.8rem, 5.2vw, 5.5rem);
  font-weight: 850;
  line-height: 1.03;
  letter-spacing: -0.065em;
  margin: 0 auto;
  max-width: 1100px;
  text-wrap: balance;
  color: inherit;
}
.starter-scene {
  position: relative;
  width: min(1440px, 100%);
  justify-self: center;
  height: clamp(390px, 51vw, 590px);
  align-self: center;
}
.starter-landmark {
  position: absolute;
  width: 100%;
  text-align: center;
  top: 10%;
  font-size: clamp(7rem, 23vw, 23rem);
  line-height: 1;
  letter-spacing: -0.08em;
  font-weight: 900;
  color: transparent;
  -webkit-text-stroke: 1px color-mix(in srgb, currentColor 15%, #8c76aa55);
  user-select: none;
}
.hero-starter {
  position: absolute;
  width: 34%;
  height: 83%;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  isolation: isolate;
}
.hero-starter:nth-of-type(1) {
  left: 3%;
  transform: rotate(-5deg);
}
.hero-starter:nth-of-type(2) {
  left: 33%;
  bottom: 8%;
  z-index: 2;
  transform: rotate(4deg);
}
.hero-starter:nth-of-type(3) {
  right: 3%;
  transform: rotate(5deg);
}
.hero-starter img {
  width: 100%;
  height: calc(100% - 40px);
  object-fit: contain;
  filter: drop-shadow(0 22px 12px #21182e25);
  transition: transform 0.35s ease;
}
.hero-starter:hover img,
.hero-starter:focus-visible img {
  transform: scale(1.045) translateY(-6px);
}
.starter-aura {
  position: absolute;
  width: 78%;
  aspect-ratio: 1;
  top: 12%;
  border-radius: 50%;
  background: color-mix(in srgb, var(--pokemon-tint) 24%, transparent);
  z-index: -1;
  filter: blur(24px);
}
.starter-name {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: clamp(0.85rem, 1.45vw, 1.3rem);
  font-weight: 750;
}
.starter-name small {
  font-family: monospace;
  font-size: 0.6em;
  font-weight: 400;
}
.starter-bottom {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 28px;
  position: relative;
  padding: 18px 70px 0;
}
.starter-catalog {
  display: inline-flex;
  align-items: center;
  gap: 30px;
  padding: 16px 25px;
  background: #513773;
  color: #fff;
  border-radius: 40px;
  font-size: 0.95rem;
  font-weight: 700;
}
[data-theme='dark'] .starter-catalog {
  background: #cfb5ec;
  color: #21182e;
}
.starter-kanto {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
}
.starter-bottom .scene-toggle {
  position: absolute;
  right: 24px;
  bottom: 4px;
  background: transparent;
  color: inherit;
  border: 1px solid currentColor;
  border-radius: 50%;
}
@keyframes starter-light {
  from {
    opacity: 0.65;
  }
  to {
    opacity: 1;
  }
}
@media (max-width: 700px) {
  .starter-home {
    min-height: calc(100svh - 133px);
    padding: 30px 0 24px;
  }
  .starter-heading h1 {
    font-size: clamp(2.7rem, 9vw, 4.4rem);
  }
  .starter-heading p {
    font-size: 0.6rem;
  }
  .starter-scene {
    height: clamp(340px, 80vw, 510px);
  }
  .hero-starter {
    width: 45%;
    height: 65%;
    bottom: 1%;
  }
  .hero-starter:nth-of-type(1) {
    left: 2%;
    z-index: 3;
  }
  .hero-starter:nth-of-type(2) {
    width: 53%;
    left: 24%;
    bottom: 29%;
    height: 72%;
  }
  .hero-starter:nth-of-type(3) {
    right: 2%;
  }
  .starter-name {
    gap: 5px;
    font-size: 0.78rem;
  }
  .hero-starter:nth-of-type(2) .starter-name {
    position: absolute;
    top: -8px;
  }
  .starter-name svg {
    width: 12px;
  }
  .starter-landmark {
    top: 35%;
    font-size: 25vw;
  }
  .starter-bottom {
    gap: 16px;
    padding: 18px 52px 0;
  }
  .starter-catalog {
    padding: 14px 18px;
    gap: 14px;
    font-size: 0.8rem;
  }
  .starter-bottom .scene-toggle {
    right: 12px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .starter-haze {
    animation: none;
  }
  .hero-starter img {
    transition: none;
  }
  .hero-starter:hover img,
  .hero-starter:focus-visible img {
    transform: none;
  }
}
</style>
