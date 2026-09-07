<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowUpRight, ArrowRight, Weight } from 'lucide-vue-next'
import { request } from '../infrastructure/httpPokemonRepository'
import { useCatalogStore } from '../application/catalogStore'
import type { Pokemon } from '../domain/pokemon'
import { money, decimal, pokemonName, number } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
const { t } = useI18n()
const featured = ref<Pokemon[]>([]),
  generations = ref<number[]>([]),
  error = ref(false),
  loading = ref(true)
const catalog = useCatalogStore()
const weightClass = (p: Pokemon) =>
  (p.weight_kg ?? 0) > 100 ? 'heavy' : (p.weight_kg ?? 0) > 10 ? 'medium' : 'light'
async function load() {
  loading.value = true
  error.value = false
  try {
    const data = await request<{ items: Pokemon[] }>('/featured')
    featured.value = data.items
    catalog.remember(data.items)
    generations.value = (await request<{ generations: number[] }>('/metadata')).generations
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
<template>
  <section class="home-intro">
    <div>
      <p class="eyebrow">{{ t('homeEyebrow') }}</p>
      <h1>
        {{ t('homeTitle') }}<br /><em>{{ t('homeTitleAccent') }}</em>
      </h1>
    </div>
    <div class="home-intro-side">
      <p>{{ t('homeIntro') }}</p>
      <RouterLink class="button primary" to="/catalogo"
        >{{ t('exploreCatalog') }}<ArrowRight :size="18"
      /></RouterLink>
    </div>
  </section>
  <p v-if="loading" class="state-box" role="status">{{ t('loadingCatalog') }}</p>
  <div v-else-if="error" class="state-box" role="alert">
    <p>{{ t('catalogError') }}</p>
    <button class="button primary" @click="load">{{ t('retry') }}</button>
  </div>
  <section v-else class="weight-bento" :aria-label="t('featured')">
    <RouterLink
      v-for="p in featured"
      :key="p.id"
      :to="'/pokemon/' + p.id"
      class="bento-pokemon"
      :class="weightClass(p)"
    >
      <div class="bento-top">
        <span
          >{{ number(p.species_id ?? p.id) }} ·
          {{ t(weightClass(p) === 'light' ? 'weightLight' : weightClass(p)) }}</span
        ><ArrowUpRight :size="22" />
      </div>
      <PokemonImage :src="p.image_url" :name="pokemonName(p)" />
      <div class="bento-bottom">
        <div>
          <p class="bento-weight"><Weight :size="15" />{{ decimal(p.weight_kg ?? 0) }} kg</p>
          <h2>{{ pokemonName(p) }}</h2>
        </div>
        <strong>{{ money(p.price_cents) }}</strong>
      </div>
    </RouterLink>
  </section>
  <p class="bento-caption">{{ t('weightCategories') }}</p>
  <section class="generation-section">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('generationsEyebrow') }}</p>
        <h2>{{ t('chooseGeneration') }}</h2>
      </div>
      <RouterLink class="back-link" to="/catalogo"
        >{{ t('viewAll') }}<ArrowRight :size="16"
      /></RouterLink>
    </div>
    <div class="generation-links">
      <RouterLink
        v-for="g in generations"
        :key="g"
        :to="{ path: '/catalogo', query: { generation: g } }"
        ><span>{{ t('generationNumber', { n: g }) }}</span
        ><ArrowUpRight :size="18"
      /></RouterLink>
    </div>
  </section>
</template>
