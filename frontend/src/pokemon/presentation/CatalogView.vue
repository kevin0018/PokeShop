<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { computed, ref } from 'vue'
import { ArrowDown, Search, SlidersHorizontal } from 'lucide-vue-next'
import { useCatalogStore } from '../application/catalogStore'
import { filterCatalog } from '../application/filterCatalog'
import type { CatalogSort } from '../domain/pokemon'
import { typeName } from '@/shared/presentation/format'
import PokemonCard from './PokemonCard.vue'
import PokemonImage from '@/components/PokemonImage.vue'
const catalog = useCatalogStore()
const search = ref('')
const type = ref('')
const sort = ref<CatalogSort>('number')
const results = computed(() => filterCatalog(catalog.items, search.value, type.value, sort.value))
const featured = computed(() => catalog.items.find((item) => item.id === 25))
function reset() {
  search.value = ''
  type.value = ''
  sort.value = 'number'
}
</script>
<template>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-copy">
      <p class="eyebrow">{{ t('heroEyebrow') }}</p>
      <h1 id="hero-title">{{ t('heroLine1') }}<br />{{ t('heroLine2') }}</h1>
      <p>{{ t('heroIntro') }}<br />{{ t('heroBody') }}</p>
      <a class="button primary" href="#catalogo">{{ t('explore') }}<ArrowDown :size="17" /></a>
    </div>
    <RouterLink
      v-if="featured"
      class="hero-art"
      to="/pokemon/25"
      :aria-label="t('discover', { name: 'Pikachu' })"
      ><span class="hero-orbit" aria-hidden="true"></span
      ><span class="hero-number" aria-hidden="true">025</span
      ><PokemonImage :src="featured.image_url" name="Pikachu" /><span class="hero-caption"
        >PIKACHU <span>{{ typeName('electrico') }} · Kanto</span></span
      ></RouterLink
    >
  </section>
  <section id="catalogo" class="catalog-section" aria-labelledby="catalog-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">{{ t('generation') }}</p>
        <h2 id="catalog-title">{{ t('favorites') }}</h2>
      </div>
      <span class="collection-label">{{ t('collection') }}</span>
    </div>
    <div class="catalog-tools">
      <label class="search-field"
        ><Search :size="19" /><span class="sr-only">{{ t('search') }}</span
        ><input
          v-model="search"
          type="search"
          :placeholder="t('searchPlaceholder')"
          maxlength="100"
      /></label>
      <label class="select-field"
        ><SlidersHorizontal :size="17" /><span class="sr-only">{{ t('filterType') }}</span
        ><select v-model="type">
          <option value="">{{ t('allTypes') }}</option>
          <option v-for="item in catalog.types" :key="item" :value="item">
            {{ typeName(item) }}
          </option>
        </select></label
      >
      <label class="select-field"
        ><span class="sr-only">{{ t('sort') }}</span
        ><select v-model="sort">
          <option value="number">{{ t('sortNumber') }}</option>
          <option value="price_asc">{{ t('sortLow') }}</option>
          <option value="price_desc">{{ t('sortHigh') }}</option>
          <option value="name">{{ t('sortName') }}</option>
        </select></label
      >
    </div>
    <p v-if="catalog.loading" role="status" class="state-box">{{ t('loadingCatalog') }}</p>
    <div v-else-if="catalog.error" class="state-box" role="alert">
      <h3>{{ t('catalogFailed') }}</h3>
      <p>{{ t(catalog.error) }}</p>
      <button class="button primary" @click="catalog.load">{{ t('retry') }}</button>
    </div>
    <template v-else
      ><div class="results-bar">
        <p role="status">
          {{ t(search || type ? 'found' : 'available', results.length) }}
        </p>
        <button v-if="search || type" class="text-button" @click="reset">
          {{ t('clearFilters') }}
        </button>
      </div>
      <div v-if="results.length" class="pokemon-grid">
        <PokemonCard v-for="pokemon in results" :key="pokemon.id" :pokemon="pokemon" />
      </div>
      <div v-else class="state-box">
        <h3>{{ t('noMatches') }}</h3>
        <p>{{ t('trySearch') }}</p>
        <button class="button primary" @click="reset">{{ t('viewAll') }}</button>
      </div></template
    >
  </section>
</template>
