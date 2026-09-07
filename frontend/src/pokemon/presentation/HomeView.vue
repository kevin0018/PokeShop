<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowUpRight, ArrowRight, Pause, Play, Zap } from 'lucide-vue-next'
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
  <section class="adventure-hero">
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
    <div
      ref="scene"
      class="pikachu-scene"
      :data-running="running"
      @pointermove="pointer"
      @pointerleave="reset"
    >
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
        @click="
          paused = !paused
          reset()
        "
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
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  align-items: center;
  gap: 20px;
  min-height: 640px;
  padding: 60px 0 70px;
}
.adventure-copy {
  position: relative;
  z-index: 2;
}
.adventure-copy .eyebrow {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.67rem;
  letter-spacing: 0.09em;
}
.adventure-copy h1 {
  font-size: clamp(2.6rem, 4.7vw, 4.6rem);
  line-height: 1.04;
  letter-spacing: -0.055em;
  max-width: 680px;
  color: var(--heading);
  margin: 24px 0;
}
.hero-description {
  max-width: 390px;
  color: var(--muted-strong);
  font-size: 1.05rem;
  line-height: 1.8;
}
.hero-actions {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 32px;
}
.hero-kanto {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--purple);
}
.pikachu-scene {
  position: relative;
  isolation: isolate;
  aspect-ratio: 1;
  --dx: 0px;
  --dy: 0px;
}
.scene-orbit {
  position: absolute;
  inset: 8%;
  border: 1px solid var(--purple);
  border-radius: 50%;
  background: radial-gradient(ellipse, #f6d64e44, transparent 70%);
  transform: rotate(-15deg);
  box-shadow: 0 0 0 22px color-mix(in srgb, var(--purple) 5%, transparent);
}
.scene-orbit:after {
  content: '';
  position: absolute;
  inset: 14%;
  border-radius: 50%;
  border: 1px dashed var(--purple);
  opacity: 0.3;
}
.scene-word {
  position: absolute;
  top: 8%;
  left: 10%;
  font-size: clamp(4rem, 10vw, 9rem);
  font-weight: 900;
  letter-spacing: -0.08em;
  color: var(--purple);
  opacity: 0.12;
  transform: rotate(-12deg);
}
.pikachu-float {
  position: absolute;
  inset: 0;
  animation: pika-float 5s ease-in-out infinite;
  animation-play-state: paused;
}
.hero-pikachu {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 28px 20px #3c215b33);
  transform: translate(var(--dx), var(--dy)) rotate(-8deg);
  transition: transform 0.4s ease;
}
.scene-ball {
  position: absolute;
  bottom: 4%;
  left: 4%;
  width: 76px;
  height: 76px;
  border: 5px solid #332842;
  border-radius: 50%;
  background: linear-gradient(#a387d1 44%, #332842 44%, #332842 55%, #fff5df 55%);
  transform: rotate(-22deg);
  box-shadow: 5px 10px 0 #3c215b18;
}
.scene-ball span {
  position: absolute;
  inset: 27%;
  border: 5px solid #332842;
  border-radius: 50%;
  background: #fff5df;
}
.scene-caption {
  position: absolute;
  bottom: 4%;
  right: 13%;
  font-size: 0.7rem;
  letter-spacing: 0.22em;
  font-weight: 800;
  color: var(--muted-strong);
}
.electric-spark {
  position: absolute;
  color: #edbe24;
  font-size: 90px;
  line-height: 1;
  font-weight: 900;
  animation: spark-glow 6s ease-in-out infinite;
  animation-play-state: paused;
}
.spark-one {
  top: 12%;
  right: 0;
  transform: rotate(12deg);
}
.spark-two {
  bottom: 17%;
  left: 0;
  transform: rotate(-18deg);
  font-size: 55px;
  animation-delay: 2s;
}
.scene-toggle {
  position: absolute;
  right: 0;
  bottom: 0;
  border: 1px solid var(--line);
  border-radius: 50%;
  background: var(--surface);
}
[data-running='true'] .pikachu-float,
[data-running='true'] .electric-spark {
  animation-play-state: running;
}
.region-discovery {
  padding-bottom: 70px;
  border-top: 1px solid var(--line);
  padding-top: 36px;
}
.region-path {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 0;
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
@keyframes pika-float {
  50% {
    transform: translateY(-12px) rotate(2deg);
  }
}
@keyframes spark-glow {
  0%,
  70%,
  100% {
    opacity: 0.35;
  }
  80% {
    opacity: 1;
  }
}
@media (max-width: 900px) {
  .adventure-hero {
    grid-template-columns: 1fr 1fr;
    min-height: 530px;
  }
  .region-path {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 700px) {
  .adventure-hero {
    grid-template-columns: 1fr;
    padding: 36px 0;
    gap: 10px;
  }
  .adventure-copy h1 {
    font-size: clamp(2.5rem, 9vw, 3.5rem);
    max-width: 550px;
  }
  .pikachu-scene {
    max-width: 420px;
    width: 100%;
    justify-self: center;
  }
  .hero-actions {
    gap: 20px;
  }
  .region-path {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .region-path a {
    padding: 18px 5px;
    gap: 8px;
  }
  .scene-word {
    font-size: 6rem;
  }
}
@media (prefers-reduced-motion: reduce) {
  .pikachu-float,
  .electric-spark {
    animation: none;
  }
  .hero-pikachu {
    transition: none;
  }
}
</style>
