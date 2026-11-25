<script lang="ts">
let captureSeen = false
</script>
<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
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
  RotateCcw,
  Tv,
  Zap,
  Ghost,
} from 'lucide-vue-next'
import { useAdventureStore } from '@/adventure/store'
import CaptureIntro from './CaptureIntro.vue'
import StudioSprite from './StudioSprite.vue'
import { useCartStore } from '@/cart/application/cartStore'
import { useCatalogStore } from '../application/catalogStore'
import { readPreference, savePreference } from '@/shared/infrastructure/preferences'
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
const cart = useCartStore()
const catalog = useCatalogStore()
const product = computed(() => offers.value.find((entry) => entry.id === star.value.id))
const cartQuantity = computed(
  () => cart.entries.find((entry) => entry.id === star.value.id)?.quantity ?? 0,
)
const owned = computed(() => game.trainer?.collection.some((entry) => entry.id === star.value.id))
const canAdd = computed(() => {
  if (game.trainer)
    return (
      !game.busy &&
      !owned.value &&
      cartQuantity.value === 0 &&
      game.shop.some((entry) => entry.id === star.value.id)
    )
  return product.value && cartQuantity.value < product.value.stock
})
const buyLabel = computed(() => {
  if (game.trainer) {
    if (owned.value) return t('adventure.owned')
    if (cartQuantity.value) return t('adventure.inCart')
  } else if (product.value && !canAdd.value) {
    return t(product.value.stock ? 'stockMax' : 'soldOut')
  }
  return t('addCart')
})
const actor = ref<HTMLElement>()
const scene = ref<HTMLElement>()
const paused = ref(false)
const visible = ref(false)
const hidden = ref(document.hidden)
const motion = window.matchMedia('(prefers-reduced-motion: reduce)')
const reduced = ref(motion.matches)
const captureKey = 'pokeshop.capture.v2'
const intro = ref(!reduced.value && !captureSeen && !readPreference(captureKey))
const revealing = ref(false)
const filmReady = computed(() => !intro.value || revealing.value)
function endIntro() {
  captureSeen = true
  savePreference(captureKey, 'seen')
  intro.value = false
  revealing.value = false
}
async function replay() {
  scene.value?.scrollIntoView({ block: 'start', behavior: 'instant' })
  await nextTick()
  intro.value = true
}
const running = computed(() => !paused.value && visible.value && !hidden.value && !reduced.value)
// Both shots use the same pose so the Pokémon can land in the offer without a cut.
const tick = ref(0)
watch(
  () => running.value || (intro.value && !reduced.value && !hidden.value),
  (playing, _, cleanup) => {
    if (!playing) return
    const timer = window.setInterval(() => tick.value++, 100)
    cleanup(() => window.clearInterval(timer))
  },
  { immediate: true },
)
const updateMotion = () => {
  reduced.value = motion.matches
  if (reduced.value && intro.value) endIntro()
}
const visibility = () => {
  hidden.value = document.hidden
}
let observer: IntersectionObserver | undefined
onMounted(() => {
  if (!intro.value) delete document.documentElement.dataset.captureBoot
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
      catalog.remember(items)
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
  <CaptureIntro
    v-if="intro"
    :id="star.id"
    :target="actor"
    :tick="tick"
    @reveal="revealing = true"
    @finish="endIntro"
  />
  <section
    ref="scene"
    class="cut-scene starter-scene"
    :data-star="star.id"
    :data-running="running"
    :data-ready="filmReady"
  >
    <div class="on-air-set">
      <div class="ink-field" aria-hidden="true"></div>
      <div class="paper-rip" aria-hidden="true"></div>
      <div class="broadcast-frame">
        <div class="feature-head" :key="'head' + star.id">
          <p class="program-slug"><Radio :size="16" /> {{ t('studio.special') }}</p>
          <h1>{{ star.name }}</h1>
          <p class="feature-types">
            <component :is="star.icon" :size="15" />
            {{ (product?.types ?? [star.type]).map(typeName).join(' / ') }}
            <span>·</span> {{ number(star.id) }}
          </p>
        </div>
        <div class="fighter-field">
          <span class="back-number" aria-hidden="true">{{ number(star.id).slice(1) }}</span>
          <div class="ink-strikes" aria-hidden="true"></div>
          <span class="floor-ink" aria-hidden="true"></span>
          <div ref="actor" class="feature-actor" :class="{ 'in-capsule': intro }">
            <div :key="star.id" class="sprite-cutout">
              <StudioSprite :id="star.id" :tick="tick" />
            </div>
          </div>
        </div>
        <div :key="'offer' + star.id" class="feature-offer">
          <p class="sales-pitch">{{ t(`studio.pitch${star.id}`) }}</p>
          <div class="offer-tape" v-if="priceFor(star.id)">
            <div class="price-cut">
              <small>{{ t('studio.price') }}</small
              ><strong>{{ priceFor(star.id) }}</strong>
            </div>
            <button class="buy-cut" :disabled="!canAdd" @click="cart.add(star.id)">
              <ShoppingBag :size="17" />{{ buyLabel }}
            </button>
          </div>
          <div class="stage-caption">
            <RouterLink :to="`/pokemon/${star.id}`"
              >{{ t('studio.details') }}<ArrowUpRight :size="17"
            /></RouterLink>
            <RouterLink to="/catalogo">{{ t('studio.shop') }}<ArrowRight :size="17" /></RouterLink>
          </div>
        </div>
      </div>
    </div>
    <div class="broadcast-controls">
      <div class="control-inner">
        <div class="on-screen"><span></span>{{ t('studio.onScreen') }}</div>
        <span class="sr-only" role="status">{{ star.name }} {{ priceFor(star.id) }}</span>
        <div class="tuner">
          <button :aria-label="t('studio.previous')" @click="tune(-1)">
            <ChevronLeft :size="19" />
          </button>
          <b
            >{{ String(selected + 1).padStart(2, '0') }}
            <i>/ {{ String(stars.length).padStart(2, '0') }}</i></b
          >
          <button :aria-label="t('studio.next')" @click="tune(1)">
            <ChevronRight :size="19" />
          </button>
        </div>
        <div v-if="!reduced" class="playback-controls">
          <button :aria-label="t('studio.replay')" :title="t('studio.replay')" @click="replay">
            <RotateCcw :size="16" /><span>{{ t('studio.replay') }}</span>
          </button>
          <button
            class="scene-toggle"
            :aria-label="t(paused ? 'resumeScene' : 'pauseScene')"
            :title="t(paused ? 'resumeScene' : 'pauseScene')"
            :aria-pressed="paused"
            @click="paused = !paused"
          >
            <Play v-if="paused" :size="16" /><Pause v-else :size="16" />
          </button>
        </div>
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
