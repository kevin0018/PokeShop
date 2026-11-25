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
      <p class="eyebrow">{{ t('kantoShop') }}</p>
      <h1>{{ t('starterHeadline') }}</h1>
      <p class="starter-intro">{{ t('kantoIntro') }}</p>
      <div class="starter-bottom">
        <RouterLink class="button primary" to="/catalogo">
          {{ t('exploreCatalog') }}<ArrowRight :size="18" aria-hidden="true" />
        </RouterLink>
        <RouterLink class="starter-kanto" to="/catalogo?region=kanto">
          {{ t('visitKanto') }}<ArrowUpRight :size="15" aria-hidden="true" />
        </RouterLink>
      </div>
    </div>
    <div class="starter-display">
      <div class="starter-display-heading">
        <h2>{{ t('kantoStarters') }}</h2>
        <button
          v-if="!reduced"
          class="scene-toggle icon-button"
          :aria-label="t(paused ? 'resumeScene' : 'pauseScene')"
          :title="t(paused ? 'resumeScene' : 'pauseScene')"
          :aria-pressed="paused"
          @click="toggle"
        >
          <Play v-if="paused" :size="16" /><Pause v-else :size="16" />
        </button>
      </div>
      <div class="starter-scene" :data-running="running">
        <RouterLink
          v-for="starter in starters"
          :key="starter.id"
          :to="`/pokemon/${starter.id}`"
          class="hero-starter pokemon-palette"
          :data-type="starter.type"
          :aria-label="t('viewPokemon', { name: starter.name })"
        >
          <span class="starter-aura" aria-hidden="true" />
          <span class="starter-id">#{{ String(starter.id).padStart(3, '0') }}</span>
          <img
            :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${starter.id}.png`"
            alt=""
            width="475"
            height="475"
            fetchpriority="high"
          />
          <span class="starter-name">
            {{ starter.name }}<ArrowUpRight :size="17" aria-hidden="true" />
          </span>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<style>
.starter-home {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: minmax(0, 0.84fr) minmax(0, 1.16fr);
  gap: clamp(20px, 3vw, 48px);
  align-items: center;
  overflow: clip;
  min-height: clamp(510px, 52vw, 700px);
  padding: clamp(20px, 4.6vw, 68px);
  border-radius: var(--shop-radius);
  background: var(--sign);
  color: var(--sign-ink);
}

.starter-haze {
  position: absolute;
  inset: -24px;
  z-index: -1;
  background:
    repeating-linear-gradient(90deg, transparent 0 39px, var(--sign-rule) 39px 40px),
    repeating-linear-gradient(0deg, transparent 0 39px, var(--sign-rule) 39px 40px);
  mask-image: linear-gradient(115deg, transparent 20%, currentColor);
  transform: translate(var(--dx, 0px), var(--dy, 0px));
  animation: starter-light 12s ease-in-out infinite alternate;
  animation-play-state: paused;
}

.starter-home[data-running='true'] .starter-haze {
  animation-play-state: running;
}

.starter-heading {
  min-width: 0;
}

.starter-heading .eyebrow {
  color: var(--sign-label);
}

.starter-heading h1 {
  max-width: 9ch;
  margin: 18px 0;
  font-size: clamp(3.4rem, 6.8vw, 6.6rem);
  line-height: 0.94;
  letter-spacing: -0.075em;
  overflow-wrap: anywhere;
  text-wrap: balance;
}

.starter-intro {
  max-width: 35ch;
  color: var(--sign-label);
  line-height: 1.6;
}

.starter-bottom {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin-top: 28px;
}

.starter-bottom .primary {
  background: var(--sign-accent);
  color: var(--sign-ink);
}

.starter-bottom .primary:hover {
  background: var(--sign-accent-hover);
}

.starter-kanto {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.86rem;
}

.starter-kanto:hover,
.starter-kanto:focus-visible {
  color: var(--sign-ink);
  text-decoration: underline;
}

.starter-home :focus-visible {
  outline-color: var(--sign-ink);
}

.starter-display {
  min-width: 0;
}

.starter-display-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.starter-display-heading h2 {
  font: 600 0.76rem/1.4 var(--font-mono);
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--sign-label);
}

.starter-display-heading .scene-toggle {
  border: 1px solid var(--sign-label);
  border-radius: 50%;
}

.starter-scene {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-template-rows: repeat(2, minmax(0, 1fr));
  height: clamp(350px, 37vw, 520px);
  gap: 8px;
}

.hero-starter {
  position: relative;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-width: 0;
  padding: clamp(10px, 1.4vw, 20px);
  border-radius: calc(var(--shop-radius) / 2);
  color: var(--sign);
  background: color-mix(in srgb, var(--pokemon-tint) 42%, var(--sign-ink));
}

.hero-starter:first-child {
  grid-row: span 2;
}

.hero-starter:hover {
  color: var(--sign);
}

.hero-starter img {
  position: absolute;
  inset: 11% 5% auto;
  width: 90%;
  height: 66%;
  object-fit: contain;
  z-index: -1;
  filter: drop-shadow(0 16px 10px var(--shop-shadow));
  transition: transform 240ms ease;
}

.hero-starter:first-child img {
  top: 12%;
  height: 76%;
}

.hero-starter:hover img,
.hero-starter:focus-visible img {
  transform: translateY(-5px) scale(1.04);
}

.starter-aura {
  position: absolute;
  inset: 0;
  z-index: -2;
  border-radius: inherit;
  background: radial-gradient(circle, var(--sign-ink) 0 31%, transparent 32%);
  opacity: 0.4;
}

.starter-id {
  font: 700 0.68rem/1.4 var(--font-mono);
}

.starter-name {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4px;
  font-weight: 750;
  font-size: clamp(0.86rem, 1.5vw, 1.25rem);
}

.starter-name svg {
  flex: none;
}

@keyframes starter-light {
  from {
    opacity: 0.45;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 820px) {
  .starter-home {
    grid-template-columns: minmax(0, 1fr);
  }

  .starter-heading h1 {
    max-width: 13ch;
    font-size: clamp(2.6rem, 8.8vw, 4.6rem);
  }

  .starter-bottom {
    margin-top: 18px;
  }

  .starter-scene {
    height: clamp(270px, 70vw, 420px);
  }
}

@media (max-width: 420px) {
  .starter-home {
    padding: 16px;
    gap: 18px;
  }

  .starter-bottom {
    gap: 4px 14px;
  }

  .starter-name svg {
    width: 13px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .starter-haze {
    animation: none;
  }

  .hero-starter:hover img,
  .hero-starter:focus-visible img {
    transform: none;
  }
}
</style>
