<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  ArrowRight,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Droplets,
  Flame,
  Gamepad2,
  Leaf,
  Pause,
  Play,
  Radio,
  ShoppingBag,
  Sparkle,
  Tv,
  Zap,
  Ghost,
} from 'lucide-vue-next'
import { useAdventureStore } from '@/adventure/store'
import { money, number, typeName } from '@/shared/presentation/format'
import type { Pokemon } from '../domain/pokemon'
import { request } from '../infrastructure/httpPokemonRepository'

const { t, n } = useI18n()
const game = useAdventureStore()
const stars = [
  { id: 6, name: 'Charizard', type: 'fuego', icon: Flame },
  { id: 25, name: 'Pikachu', type: 'electrico', icon: Zap },
  { id: 94, name: 'Gengar', type: 'fantasma', icon: Ghost },
] as const
const starters = [
  { id: 1, name: 'Bulbasaur', type: 'planta', icon: Leaf },
  { id: 4, name: 'Charmander', type: 'fuego', icon: Flame },
  { id: 7, name: 'Squirtle', type: 'agua', icon: Droplets },
]
const selected = ref(0)
const star = computed(() => stars[selected.value]!)
function tune(step: number) {
  selected.value = (selected.value + step + stars.length) % stars.length
}

const offers = ref<Pokemon[]>([])
const controller = new AbortController()
function priceFor(id: number) {
  if (game.trainer) {
    const offer = game.shop.find((entry) => entry.id === id)
    return offer ? t('adventure.credits', { amount: n(offer.price) }) : ''
  }
  const offer = offers.value.find((entry) => entry.id === id)
  return offer ? money(offer.price_cents) : ''
}
const scene = ref<HTMLElement>()
const paused = ref(false)
const visible = ref(false)
const hidden = ref(document.hidden)
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
const reduced = ref(motion.matches)
const running = computed(() => !paused.value && visible.value && !hidden.value && !reduced.value)
const updateMotion = () => {
  reduced.value = motion.matches
}
const visibility = () => {
  hidden.value = document.hidden
}
let observer: IntersectionObserver | undefined
onMounted(() => {
  motion.addEventListener('change', updateMotion)
  document.addEventListener('visibilitychange', visibility)
  observer = new IntersectionObserver(([entry]) => {
    visible.value = !!entry?.isIntersecting
  })
  if (scene.value) observer.observe(scene.value)
  const ids = [...stars, ...starters].map((entry) => entry.id)
  request<{ items: Pokemon[] }>(`/batch?ids=${ids.join(',')}`, controller.signal)
    .then(({ items }) => {
      offers.value = items
    })
    .catch(() => {
      /* The showcase links remain available while prices are offline. */
    })
})
onUnmounted(() => {
  observer?.disconnect()
  controller.abort()
  motion.removeEventListener('change', updateMotion)
  document.removeEventListener('visibilitychange', visibility)
})
</script>

<template>
  <section ref="scene" class="studio-hero starter-scene" :data-running="running">
    <div class="studio-copy">
      <div class="program-label">
        <span><Radio :size="15" />POKÉSHOP TV</span><b>{{ t('studio.special') }}</b>
      </div>
      <h1>{{ t('studio.title') }}<br /><em>Pokémon.</em></h1>
      <p>{{ t('studio.intro') }}</p>
      <RouterLink class="studio-cta" to="/catalogo"
        ><ShoppingBag :size="18" />{{ t('studio.shop') }}<ArrowRight :size="18"
      /></RouterLink>
    </div>
    <div class="showcase">
      <div class="stage-orbit" aria-hidden="true"></div>
      <Sparkle class="stage-glint glint-a" aria-hidden="true" />
      <Sparkle class="stage-glint glint-b" aria-hidden="true" />
      <span class="stage-glint glint-c" aria-hidden="true">+</span>
      <div class="stage-plinth" aria-hidden="true"></div>
      <div class="stage-art">
        <RouterLink
          :key="star.id"
          :to="`/pokemon/${star.id}`"
          :aria-label="t('viewPokemon', { name: star.name })"
        >
          <img
            :src="`/studio/${star.id}.webp`"
            alt=""
            width="475"
            height="475"
            fetchpriority="high"
          />
        </RouterLink>
      </div>
      <div class="stage-caption" aria-live="polite" aria-atomic="true">
        <span
          ><component :is="star.icon" :size="13" />{{ typeName(star.type) }} ·
          {{ number(star.id) }}</span
        >
        <RouterLink :to="`/pokemon/${star.id}`"
          >{{ star.name }}<ArrowUpRight :size="22"
        /></RouterLink>
        <small v-if="priceFor(star.id)">{{ priceFor(star.id) }}</small>
      </div>
      <button
        v-if="!reduced"
        class="scene-toggle studio-round"
        :aria-label="t(paused ? 'resumeScene' : 'pauseScene')"
        :aria-pressed="paused"
        @click="paused = !paused"
      >
        <Play v-if="paused" :size="15" /><Pause v-else :size="15" />
      </button>
    </div>
    <div class="program-bar">
      <div class="on-screen">
        <span class="status-light"></span>{{ t('studio.onScreen')
        }}<span class="program-name">{{ t('studio.lineup') }}</span>
      </div>
      <div class="tuner">
        <button :aria-label="t('studio.previous')" @click="tune(-1)">
          <ChevronLeft :size="18" />
        </button>
        <span>{{ String(selected + 1).padStart(2, '0') }} <i>/ 03</i></span>
        <button :aria-label="t('studio.next')" @click="tune(1)"><ChevronRight :size="18" /></button>
      </div>
    </div>
  </section>
  <section class="starter-stand" aria-labelledby="stand-title">
    <header class="stand-heading">
      <div>
        <p class="station-kicker"><Tv :size="16" />{{ t('kantoStarters') }}</p>
        <h2 id="stand-title">{{ t('studio.stand') }}</h2>
      </div>
      <RouterLink class="stand-link" to="/catalogo?region=kanto"
        >{{ t('studio.viewKanto') }}<ArrowRight :size="17"
      /></RouterLink>
    </header>
    <div class="stand-shelf">
      <RouterLink
        v-for="starter in starters"
        :key="starter.id"
        :to="`/pokemon/${starter.id}`"
        class="stand-card hero-starter"
        :data-type="starter.type"
      >
        <span class="stand-type"
          ><component :is="starter.icon" :size="14" />{{ typeName(starter.type) }}</span
        >
        <span class="stand-dex">{{ number(starter.id) }}</span>
        <img :src="`/studio/${starter.id}.webp`" alt="" width="475" height="475" />
        <span class="stand-info"
          ><strong>{{ starter.name }}</strong
          ><small v-if="priceFor(starter.id)">{{ priceFor(starter.id) }}</small></span
        >
        <ArrowUpRight class="stand-arrow" :size="30" />
      </RouterLink>
    </div>
  </section>
  <RouterLink class="battle-extra" to="/aventura">
    <Gamepad2 :size="24" /><span>{{ t('studio.battle') }}</span
    ><ArrowRight :size="18" />
  </RouterLink>
</template>

<style src="./studio.css"></style>
