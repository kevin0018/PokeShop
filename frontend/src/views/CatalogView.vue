<template>
  <div class="catalog-view">
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Catálogo Pokemon</h1>
      <p class="text-lg text-gray-600">Descubre y captura los mejores Pokemon</p>
    </div>

    <!-- Search and Filters Section -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Search Bar -->
        <div class="md:col-span-2">
          <label for="search" class="block text-sm font-medium text-gray-700 mb-2">
            Buscar Pokemon
          </label>
          <input
            id="search"
            type="text"
            placeholder="Busca por nombre..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <!-- Type Filter -->
        <div>
          <label for="type" class="block text-sm font-medium text-gray-700 mb-2">
            Tipo
          </label>
          <select
            id="type"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Todos los tipos</option>
            <option value="fire">Fuego</option>
            <option value="water">Agua</option>
            <option value="grass">Planta</option>
            <option value="electric">Eléctrico</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Pokemon Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <!-- Pokemon Card Example -->
      <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div class="aspect-square bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center">
          <img
            src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
            alt="Pikachu"
            class="w-32 h-32 object-contain"
          />
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Pikachu</h3>
          <div class="flex items-center justify-between mb-3">
            <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
              Eléctrico
            </span>
            <span class="text-lg font-bold text-gray-900">€25.99</span>
          </div>
          <button class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors duration-200">
            Añadir al carrito
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-gray-600 mt-4">Cargando Pokemon...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
// Catalog logic will be implemented with the application layer
</script>
