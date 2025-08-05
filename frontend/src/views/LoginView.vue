<template>
  <div class="login-view max-w-md mx-auto">
    <div class="bg-white p-8 rounded-lg shadow-md">
      <h1 class="text-2xl font-bold text-center text-gray-900 mb-8">Iniciar sesión</h1>
      
      <form class="space-y-6">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="tu@email.com"
          />
        </div>
        
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
            Contraseña
          </label>
          <input
            id="password"
            type="password"
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="••••••••"
          />
        </div>
        
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label for="remember" class="ml-2 block text-sm text-gray-700">
              Recordarme
            </label>
          </div>
          
          <a href="#" class="text-sm text-blue-600 hover:text-blue-500">
            ¿Olvidaste tu contraseña?
          </a>
        </div>
        
        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
        >
          Iniciar sesión
        </button>
      </form>
      
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          ¿No tienes cuenta?
          <router-link to="/register" class="text-blue-600 hover:text-blue-500 font-medium">
            Regístrate aquí
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Login logic will be implemented with the user application layer
</script>
