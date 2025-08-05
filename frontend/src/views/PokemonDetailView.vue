<template>
  <div class="pokemon-detail-view">
    <!-- Pokemon Hero Section -->
    <div class="bg-gradient-to-r from-blue-500 to-purple-600 text-white py-12 mb-8">
      <div class="max-w-4xl mx-auto px-4">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <!-- Pokemon Image -->
          <div class="text-center">
            <img
              src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
              alt="Pikachu"
              class="w-64 h-64 mx-auto object-contain"
            />
          </div>
          
          <!-- Pokemon Info -->
          <div>
            <h1 class="text-4xl font-bold mb-4">Pikachu</h1>
            <div class="flex items-center space-x-4 mb-4">
              <span class="px-3 py-1 bg-yellow-500 text-white rounded-full text-sm font-medium">
                Eléctrico
              </span>
              <span class="text-2xl font-bold">€25.99</span>
            </div>
            <p class="text-lg mb-6">
              Pikachu es un Pokémon de tipo eléctrico conocido por sus mejillas que almacenan electricidad.
            </p>
            <button class="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200">
              Añadir al carrito
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pokemon Stats -->
    <div class="max-w-4xl mx-auto px-4 mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Estadísticas</h2>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-red-600">35</div>
          <div class="text-sm text-gray-600">HP</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-orange-600">55</div>
          <div class="text-sm text-gray-600">Ataque</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-blue-600">40</div>
          <div class="text-sm text-gray-600">Defensa</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-purple-600">50</div>
          <div class="text-sm text-gray-600">At. Especial</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-green-600">50</div>
          <div class="text-sm text-gray-600">Def. Especial</div>
        </div>
        <div class="bg-white p-4 rounded-lg shadow-md text-center">
          <div class="text-2xl font-bold text-yellow-600">90</div>
          <div class="text-sm text-gray-600">Velocidad</div>
        </div>
      </div>
    </div>

    <!-- Pokemon Details -->
    <div class="max-w-4xl mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-xl font-bold text-gray-900 mb-4">Información básica</h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-600">Altura:</span>
              <span class="font-medium">0.4 m</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Peso:</span>
              <span class="font-medium">6.0 kg</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Categoría:</span>
              <span class="font-medium">Ratón</span>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-xl font-bold text-gray-900 mb-4">Habilidades</h3>
          <div class="space-y-2">
            <span class="inline-block px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
              Electricidad Estática
            </span>
            <span class="inline-block px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
              Pararrayos (Oculta)
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  id: string
}

defineProps<Props>()

// Pokemon detail logic will be implemented with the application layer
</script>
