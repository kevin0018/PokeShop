<template>
  <div class="profile-view max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Mi perfil</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Profile Info -->
      <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Información personal</h2>
        
        <form class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700 mb-2">
                Nombre
              </label>
              <input
                id="firstName"
                type="text"
                value="Juan"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700 mb-2">
                Apellidos
              </label>
              <input
                id="lastName"
                type="text"
                value="Pérez"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              id="email"
              type="email"
              value="juan.perez@email.com"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
              Teléfono
            </label>
            <input
              id="phone"
              type="tel"
              value="+34 123 456 789"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            type="submit"
            class="bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            Guardar cambios
          </button>
        </form>
      </div>

      <!-- Profile Stats -->
      <div class="space-y-6">
        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Estadísticas</h3>
          <div class="space-y-4">
            <div class="flex justify-between">
              <span class="text-gray-600">Pokemon capturados:</span>
              <span class="font-semibold">12</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Pedidos realizados:</span>
              <span class="font-semibold">8</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Total gastado:</span>
              <span class="font-semibold">€234.56</span>
            </div>
          </div>
        </div>

        <div class="bg-white p-6 rounded-lg shadow-md">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Pokemon favorito</h3>
          <div class="text-center">
            <img
              src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
              alt="Pikachu"
              class="w-20 h-20 mx-auto object-contain"
            />
            <p class="font-medium mt-2">Pikachu</p>
            <p class="text-sm text-gray-600">Eléctrico</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Order History -->
    <div class="mt-8 bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-xl font-semibold text-gray-900 mb-6">Historial de pedidos</h2>
      
      <div class="space-y-4">
        <!-- Order Item -->
        <div class="border border-gray-200 rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium">#12345</span>
            <span class="text-sm text-gray-600">15/01/2025</span>
          </div>
          <div class="flex items-center space-x-4">
            <img
              src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
              alt="Pikachu"
              class="w-12 h-12 object-contain"
            />
            <div class="flex-1">
              <p class="font-medium">Pikachu + 2 más</p>
              <p class="text-sm text-gray-600">€75.99</p>
            </div>
            <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
              Entregado
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Profile logic will be implemented with the user application layer
</script>
