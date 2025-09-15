<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="bg-gray-50">
    <!-- Header -->
    <header class="bg-gradient-to-r from-red-500 via-yellow-500 to-blue-500 text-white shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-2">
            <img alt="Pokemon Logo" class="h-8 w-8" src="@/assets/logo.svg" />
            <h1 class="text-xl font-bold">PokeShop</h1>
          </div>

          <!-- Navigation -->
          <nav class="hidden md:flex space-x-6">
            <RouterLink 
              to="/" 
              class="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors duration-200"
            >
              Inicio
            </RouterLink>
            <RouterLink 
              to="/catalog" 
              class="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors duration-200"
            >
              Catálogo
            </RouterLink>
            <RouterLink 
              to="/about" 
              class="px-3 py-2 rounded-md text-sm font-medium hover:bg-white hover:bg-opacity-20 transition-colors duration-200"
            >
              Acerca de
            </RouterLink>
          </nav>

          <!-- Mobile menu button -->
          <button class="md:hidden p-2 rounded-md hover:bg-white hover:bg-opacity-20">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- Main content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <p>&copy; 2025 PokeShop. Todos los derechos reservados.</p>
          <p class="text-sm text-gray-400 mt-2">
            Hecho con ❤️ usando Vue 3, Tailwind CSS y FastAPI
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>
