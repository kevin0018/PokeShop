<template>
  <div class="cart-view">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Carrito de compras</h1>

    <!-- Empty Cart State -->
    <div class="text-center py-12">
      <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-8 6a2 2 0 002 2h6M7 13l-1 8a2 2 0 002 2h6" />
      </svg>
      <h2 class="text-xl font-semibold text-gray-900 mt-4">Tu carrito está vacío</h2>
      <p class="text-gray-600 mt-2">¡Agrega algunos Pokemon increíbles a tu colección!</p>
      <router-link
        to="/catalog"
        class="inline-block mt-6 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors duration-200"
      >
        Explorar catálogo
      </router-link>
    </div>

    <!-- Cart with Items -->
    <div class="hidden">
      <div class="bg-white rounded-lg shadow-md">
        <!-- Cart Item -->
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center space-x-4">
            <img
              src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
              alt="Pikachu"
              class="w-16 h-16 object-contain"
            />
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900">Pikachu</h3>
              <p class="text-gray-600">Tipo: Eléctrico</p>
            </div>
            <div class="flex items-center space-x-2">
              <button class="p-1 rounded-full hover:bg-gray-100">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                </svg>
              </button>
              <span class="w-8 text-center">1</span>
              <button class="p-1 rounded-full hover:bg-gray-100">
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </button>
            </div>
            <div class="text-lg font-semibold">€25.99</div>
            <button class="text-red-600 hover:text-red-800">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Cart Summary -->
        <div class="p-6">
          <div class="flex justify-between items-center mb-4">
            <span class="text-lg font-semibold">Total:</span>
            <span class="text-2xl font-bold text-blue-600">€25.99</span>
          </div>
          <button class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-200">
            Proceder al checkout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Cart logic will be implemented with the application layer
</script>
