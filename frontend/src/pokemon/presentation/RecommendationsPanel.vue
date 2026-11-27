<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { ArrowLeft, ArrowRight } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import type { Pokemon } from '../domain/pokemon'
import PokemonCard from './PokemonCard.vue'
import PokemonImage from '@/components/PokemonImage.vue'
import { pokemonName } from '@/shared/presentation/format'
const props = defineProps<{ ids: number[]; thumbnails?: boolean }>()
const { t } = useI18n()
const catalog = useCatalogStore()
const items = ref<Pokemon[]>([]),
  error = ref(false),
  loading = ref(false)
const track = ref<HTMLUListElement>()
const firstVisible = ref(0)
function syncPosition() {
  const list = track.value
  if (!list || list.children.length < 2) return
  const stride =
    list.children[1].getBoundingClientRect().left - list.children[0].getBoundingClientRect().left
  if (stride > 0) firstVisible.value = Math.round(list.scrollLeft / stride)
}
function move(direction: number) {
  const list = track.value
  if (list) list.scrollBy({ left: direction * (list.clientWidth + 10), behavior: 'instant' })
}
let controller: AbortController | undefined
async function load() {
  controller?.abort()
  controller = new AbortController()
  const current = controller
  error.value = false
  loading.value = true
  try {
    const result = await request<{ items: Pokemon[] }>(
      '/recommendations?ids=' + props.ids.join(','),
      current.signal,
    )
    if (current.signal.aborted) return
    if (track.value) track.value.scrollLeft = 0
    firstVisible.value = 0
    items.value = result.items
    catalog.remember(result.items)
  } catch {
    if (!current.signal.aborted) error.value = true
  } finally {
    if (!current.signal.aborted) loading.value = false
  }
}
watch(() => props.ids.join(','), load, { immediate: true })
onUnmounted(() => controller?.abort())
</script>
<template>
  <section
    v-if="thumbnails && (loading || error || items.length)"
    :aria-busy="loading"
    class="recommendation-thumbnails"
    aria-labelledby="profile-recommendations"
  >
    <h2 id="profile-recommendations">{{ t('relatedPokemon') }}</h2>
    <p v-if="loading && !items.length" role="status">{{ t('loadingCatalog') }}</p>
    <div v-else-if="error" role="alert">
      <p>{{ t('recommendationsError') }}</p>
      <button class="button secondary" @click="load">{{ t('retry') }}</button>
    </div>
    <ul v-else ref="track" @scroll="syncPosition">
      <li v-for="p in items" :key="p.id">
        <RouterLink
          :to="'/pokemon/' + p.id"
          :aria-label="pokemonName(p)"
          :title="pokemonName(p)"
          class="pokemon-palette"
          :data-type="p.types[0]"
        >
          <PokemonImage :src="p.image_url" :name="pokemonName(p)" />
          <span class="thumbnail-name">{{ pokemonName(p) }}</span>
        </RouterLink>
      </li>
    </ul>
    <div v-if="!error && items.length > 2" class="thumb-controls">
      <span
        >{{ String(firstVisible + 1).padStart(2, '0') }} /
        {{ String(items.length).padStart(2, '0') }}</span
      >
      <button :disabled="firstVisible === 0" :aria-label="t('previous')" @click="move(-1)">
        <ArrowLeft :size="15" />
      </button>
      <button :disabled="firstVisible >= items.length - 2" :aria-label="t('next')" @click="move(1)">
        <ArrowRight :size="15" />
      </button>
    </div>
  </section>
  <section v-else-if="!thumbnails" class="recommendations">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('featured') }}</p>
        <h2>{{ t('recommendations') }}</h2>
      </div>
    </div>
    <p v-if="ids.length">{{ t('recommendationsIntro') }}</p>
    <p v-if="loading" role="status">{{ t('loadingCatalog') }}</p>
    <div v-else-if="error" role="alert">
      <p>{{ t('recommendationsError') }}</p>
      <button class="button secondary" @click="load">{{ t('retry') }}</button>
    </div>
    <div v-else class="pokemon-grid">
      <div v-for="p in items" :key="p.id">
        <span class="recommendation-reason">{{ t(p.reason || 'featured') }}</span
        ><PokemonCard :pokemon="p" />
      </div>
    </div>
  </section>
</template>

<style scoped>
.recommendation-thumbnails h2 {
  margin: 0 0 10px;
  color: var(--profile-muted);
  font: 700 0.73rem/1.4 var(--font-mono);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.recommendation-thumbnails ul {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: calc((100% - 10px) / 2);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  scrollbar-color: #968987 transparent;
  gap: 10px;
  margin: 0;
  padding: 4px 2px 8px;
  list-style: none;
}
.recommendation-thumbnails li {
  scroll-snap-align: start;
}
.thumbnail-name {
  font: 650 0.74rem/1.2 var(--font-mono);
  text-align: center;
  overflow-wrap: anywhere;
}
.recommendation-thumbnails a {
  grid-template-rows: minmax(0, 1fr) auto;
  text-decoration: none;
  display: grid;
  place-items: center;
  aspect-ratio: 1;
  min-height: 44px;
  padding: 4px;
  color: var(--profile-ink);
  background: transparent;
  border: 1px solid color-mix(in srgb, var(--pokemon-tint) 45%, var(--profile-bg));
  border-radius: 8px;
}
.recommendation-thumbnails a:hover .thumbnail-name {
  text-decoration: underline;
  text-underline-offset: 3px;
}
.recommendation-thumbnails a:focus-visible {
  outline: 2px solid var(--profile-ink);
  outline-offset: 2px;
}
.recommendation-thumbnails img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.recommendation-thumbnails .image-fallback {
  min-height: 0;
  padding: 0;
  font-size: 0.58rem;
  overflow-wrap: anywhere;
}
.thumb-controls {
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: flex-end;
}
.thumb-controls span {
  margin-right: auto;
  color: var(--profile-muted);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
}
.thumb-controls button {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: transparent;
  color: white;
  border: 1px solid #fff7;
}
.thumb-controls button:disabled {
  opacity: 0.42;
}
</style>
