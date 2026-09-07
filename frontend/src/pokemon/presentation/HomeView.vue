<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowUpRight, ArrowRight, Pause, Play, Zap } from 'lucide-vue-next'
import PokeballIntro from '@/components/PokeballIntro.vue'
import { request } from '../infrastructure/httpPokemonRepository'
const { t, locale } = useI18n()
const regions = ref<{ id: string; names: Record<string, string> }[]>([])
const scene = ref<HTMLElement>(),
  paused = ref(false),
  visible = ref(false),
  hidden = ref(document.hidden),
  reduced = ref(true)
const running = computed(() => !paused.value && visible.value && !hidden.value && !reduced.value)
let observer: IntersectionObserver | undefined
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
const updateMotion = () => {
  reduced.value = motion.matches
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
function toggle() {
  paused.value = !paused.value
  reset()
}
function reset() {
  scene.value?.style.setProperty('--dx', '0px')
  scene.value?.style.setProperty('--dy', '0px')
}
onMounted(() => {
  updateMotion()
  motion.addEventListener('change', updateMotion)
  document.addEventListener('visibilitychange', visibility)
  observer = new IntersectionObserver(([entry]) => {
    visible.value = !!entry?.isIntersecting
  })
  if (scene.value) observer.observe(scene.value)
  void request<{ regions: typeof regions.value }>('/metadata')
    .then((r) => (regions.value = r.regions ?? []))
    .catch(() => {})
})
onUnmounted(() => {
  observer?.disconnect()
  motion.removeEventListener('change', updateMotion)
  document.removeEventListener('visibilitychange', visibility)
})
</script>
<template>
  <PokeballIntro />
  <section
    ref="scene"
    class="adventure-hero"
    :data-running="running"
    @pointermove="pointer"
    @pointerleave="reset"
  >
    <svg class="hero-traces" viewBox="0 0 1200 650" preserveAspectRatio="none" aria-hidden="true">
      <path d="M720 -20 620 190 820 190 710 360 1150 290 980 650" />
      <path d="M-20 580 300 510 400 590 730 440" />
    </svg>
    <div class="adventure-copy">
      <p class="eyebrow"><Zap :size="15" /> POKESHOP · {{ t('spark') }}</p>
      <h1>{{ t('adventure') }}</h1>
      <p class="hero-description">{{ t('heroCopy') }}</p>
      <div class="hero-actions">
        <RouterLink class="button primary" to="/catalogo"
          >{{ t('exploreCatalog') }}<ArrowRight :size="18" /></RouterLink
        ><RouterLink class="hero-kanto" to="/catalogo?region=kanto"
          >{{ t('visitKanto') }}<ArrowUpRight :size="17"
        /></RouterLink>
      </div>
    </div>
    <div class="pikachu-scene" :data-running="running">
      <div class="scene-orbit" aria-hidden="true" />
      <span class="scene-word" aria-hidden="true">PIKA!</span>
      <div class="electric-spark spark-one" aria-hidden="true">ϟ</div>
      <div class="electric-spark spark-two" aria-hidden="true">ϟ</div>
      <div class="pikachu-float">
        <img
          class="hero-pikachu"
          src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
          alt="Pikachu"
          width="475"
          height="475"
          fetchpriority="high"
        />
      </div>
      <div class="scene-ball" aria-hidden="true"><span /></div>
      <span class="scene-caption">#025 · KANTO</span>
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
  <section class="region-discovery">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('originIntro') }}</p>
        <h2>{{ t('chooseRegion') }}</h2>
      </div>
      <RouterLink class="back-link" to="/catalogo"
        >{{ t('viewAll') }}<ArrowRight :size="16"
      /></RouterLink>
    </div>
    <div class="region-path">
      <RouterLink
        v-for="(region, index) in regions"
        :key="region.id"
        :to="{ path: '/catalogo', query: { region: region.id } }"
        ><span class="region-index">{{ String(index + 1).padStart(2, '0') }}</span
        ><strong>{{ region.names[locale] ?? region.id }}</strong
        ><ArrowUpRight :size="18"
      /></RouterLink>
    </div>
  </section>
</template>
<style scoped>
.adventure-hero {
  position: relative;
  isolation: isolate;
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  align-items: center;
  min-height: 590px;
  padding: 50px 44px;
  margin: 0 0 50px;
  overflow: hidden;
  border-radius: 30px;
  background:
    radial-gradient(
      ellipse at calc(75% + var(--dx, 0px)) calc(35% + var(--dy, 0px)),
      #775791,
      transparent 62%
    ),
    #2e193f;
  color: #fff7e7;
}
.adventure-hero:before {
  content: '';
  position: absolute;
  inset: -35%;
  background: repeating-linear-gradient(-25deg, transparent 0 90px, #ffffff05 91px 92px);
  z-index: -1;
}
.adventure-copy {
  position: relative;
  z-index: 2;
}
.adventure-copy .eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.65rem;
  letter-spacing: 0.13em;
  color: #eed35c;
  max-width: 350px;
}
.adventure-copy h1 {
  font-size: clamp(2.7rem, 4.5vw, 4.6rem);
  line-height: 1.02;
  letter-spacing: -0.055em;
  color: #fff7e7;
  margin: 24px 0;
  max-width: 600px;
}
.hero-description {
  max-width: 350px;
  color: #e4d4ec;
  line-height: 1.8;
  font-size: 0.95rem;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 22px;
  margin-top: 28px;
}
.hero-actions .primary {
  background: #f2cf54;
  color: #2e193f;
}
.hero-actions .primary:hover {
  background: #ffe480;
}
.hero-kanto {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff7e7;
  font-size: 0.8rem;
  font-weight: 700;
}
.pikachu-scene {
  position: relative;
  aspect-ratio: 1;
  align-self: center;
  min-width: 0;
}
.scene-orbit {
  position: absolute;
  inset: 6%;
  border-radius: 50%;
  background: #f1cf52;
  box-shadow: 0 0 0 24px #f2cf5412;
  transform: rotate(-12deg) scaleY(0.9);
}
.scene-word {
  position: absolute;
  font-size: clamp(5rem, 12vw, 10rem);
  font-weight: 900;
  letter-spacing: -0.09em;
  top: 2%;
  left: 2%;
  transform: rotate(-12deg);
  color: #ffffff1c;
  z-index: 1;
}
.pikachu-float {
  position: absolute;
  inset: 0;
  z-index: 2;
}
.hero-pikachu {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 20px 12px #170b2744);
  transform: rotate(-7deg);
}
.scene-ball {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 74px;
  height: 74px;
  border: 5px solid #2b1939;
  border-radius: 50%;
  background: linear-gradient(#a389bd 44%, #2b1939 44%, #2b1939 55%, #fff5df 55%);
  transform: rotate(-22deg);
  z-index: 3;
}
.scene-ball span {
  position: absolute;
  inset: 27%;
  border: 5px solid #2b1939;
  border-radius: 50%;
  background: #fff5df;
}
.scene-caption {
  position: absolute;
  bottom: -2%;
  right: 14%;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: #f4df99;
  font-weight: 800;
  z-index: 3;
}
.scene-toggle {
  position: absolute;
  right: 0;
  bottom: -4%;
  border: 1px solid #ffffff44;
  background: #2e193f;
  color: #fff7e7;
  border-radius: 50%;
  z-index: 3;
}
.electric-spark {
  position: absolute;
  color: #fff5c5;
  font-size: 70px;
  font-weight: 900;
  line-height: 1;
  z-index: 3;
  animation: electric-pulse 7s ease-in-out infinite;
  animation-play-state: paused;
}
.spark-one {
  right: 0;
  top: 5%;
  transform: rotate(10deg);
}
.spark-two {
  left: 0;
  bottom: 23%;
  font-size: 45px;
  animation-delay: 3s;
}
.hero-traces {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  fill: none;
  stroke: #f7d653;
  stroke-width: 3;
  opacity: 0.18;
}
.hero-traces path {
  stroke-dasharray: 100 1600;
  animation: electric-travel 9s ease-in-out infinite;
  animation-play-state: paused;
}
.hero-traces path + path {
  animation-delay: 4s;
}
[data-running='true'] > .hero-traces path,
[data-running='true'] > .electric-spark {
  animation-play-state: running;
}
.region-discovery {
  padding: 12px 0 50px;
}
.region-path {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
}
.region-path a {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 22px 12px;
  border-bottom: 1px solid var(--line);
  color: var(--ink);
}
.region-path a:hover {
  background: var(--lavender);
}
.region-path svg {
  margin-left: auto;
  color: var(--purple);
}
.region-index {
  font-size: 0.65rem;
  color: var(--muted-strong);
}
@keyframes electric-pulse {
  0%,
  70%,
  100% {
    opacity: 0.3;
  }
  80% {
    opacity: 1;
  }
}
@keyframes electric-travel {
  0%,
  55% {
    stroke-dashoffset: 1700;
  }
  85%,
  100% {
    stroke-dashoffset: -1700;
  }
}
@media (max-width: 1000px) {
  .adventure-hero {
    padding: 36px 28px;
    min-height: 540px;
  }
  .adventure-copy h1 {
    font-size: 3rem;
  }
  .region-path {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 700px) {
  .adventure-hero {
    grid-template-columns: 1fr;
    padding: 28px 22px 38px;
    gap: 24px;
    border-radius: 22px;
  }
  .adventure-copy h1 {
    font-size: clamp(2.45rem, 8.8vw, 3.4rem);
  }
  .adventure-copy .eyebrow {
    font-size: 0.6rem;
  }
  .hero-actions {
    gap: 16px;
  }
  .pikachu-scene {
    width: 100%;
    max-width: 390px;
    justify-self: center;
  }
  .scene-word {
    font-size: 6rem;
  }
  .scene-caption {
    right: 16%;
    font-size: 0.56rem;
  }
  .scene-ball {
    width: 60px;
    height: 60px;
  }
  .region-path {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .region-path a {
    padding: 18px 5px;
    gap: 8px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .hero-traces path,
  .electric-spark {
    animation: none;
  }
}
</style>
