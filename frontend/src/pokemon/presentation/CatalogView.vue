<script setup lang="ts">
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
      <p class="eyebrow">EL COMIENZO DE TU COLECCIÓN</p>
      <h1 id="hero-title">Tu próximo<br />compañero está aquí.</h1>
      <p>Redescubre los favoritos de Kanto.<br />Encuentra el tuyo y empieza a formar tu equipo.</p>
      <a class="button primary" href="#catalogo">Explorar Pokémon <ArrowDown :size="17" /></a>
    </div>
    <RouterLink v-if="featured" class="hero-art" to="/pokemon/25" aria-label="Descubrir a Pikachu"
      ><span class="hero-orbit" aria-hidden="true"></span
      ><span class="hero-number" aria-hidden="true">025</span
      ><PokemonImage :src="featured.image_url" name="Pikachu" /><span class="hero-caption"
        >PIKACHU <span>Eléctrico · Kanto</span></span
      ></RouterLink
    >
  </section>
  <section id="catalogo" class="catalog-section" aria-labelledby="catalog-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">PRIMERA GENERACIÓN</p>
        <h2 id="catalog-title">Encuentra tu favorito</h2>
      </div>
      <span class="collection-label">Colección Kanto</span>
    </div>
    <div class="catalog-tools">
      <label class="search-field"
        ><Search :size="19" /><span class="sr-only">Buscar Pokémon</span
        ><input
          v-model="search"
          type="search"
          placeholder="Nombre o número de Pokédex"
          maxlength="100"
      /></label>
      <label class="select-field"
        ><SlidersHorizontal :size="17" /><span class="sr-only">Filtrar por tipo</span
        ><select v-model="type">
          <option value="">Todos los tipos</option>
          <option v-for="item in catalog.types" :key="item" :value="item">
            {{ typeName(item) }}
          </option>
        </select></label
      >
      <label class="select-field"
        ><span class="sr-only">Ordenar Pokémon</span
        ><select v-model="sort">
          <option value="number">Número de Pokédex</option>
          <option value="price_asc">Precio: menor a mayor</option>
          <option value="price_desc">Precio: mayor a menor</option>
          <option value="name">Nombre: A a Z</option>
        </select></label
      >
    </div>
    <p v-if="catalog.loading" role="status" class="state-box">Preparando tu próxima aventura…</p>
    <div v-else-if="catalog.error" class="state-box" role="alert">
      <h3>No se ha cargado el catálogo</h3>
      <p>{{ catalog.error }}</p>
      <button class="button primary" @click="catalog.load">Volver a intentar</button>
    </div>
    <template v-else
      ><div class="results-bar">
        <p role="status">
          {{ results.length }} Pokémon{{
            search || type
              ? results.length === 1
                ? ' encontrado'
                : ' encontrados'
              : ' para descubrir'
          }}
        </p>
        <button v-if="search || type" class="text-button" @click="reset">Limpiar filtros</button>
      </div>
      <div v-if="results.length" class="pokemon-grid">
        <PokemonCard v-for="pokemon in results" :key="pokemon.id" :pokemon="pokemon" />
      </div>
      <div v-else class="state-box">
        <h3>No hay coincidencias</h3>
        <p>Prueba otro nombre, número o tipo de Pokémon.</p>
        <button class="button primary" @click="reset">Ver todos los Pokémon</button>
      </div></template
    >
  </section>
</template>
