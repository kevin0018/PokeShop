<template>
  <div class="checkout-view max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 mb-8">Checkout</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Checkout Form -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Información de envío</h2>
        
        <form class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700 mb-2">
                Nombre
              </label>
              <input
                id="firstName"
                type="text"
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
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label for="address" class="block text-sm font-medium text-gray-700 mb-2">
              Dirección
            </label>
            <input
              id="address"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label for="city" class="block text-sm font-medium text-gray-700 mb-2">
                Ciudad
              </label>
              <input
                id="city"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label for="state" class="block text-sm font-medium text-gray-700 mb-2">
                Provincia
              </label>
              <input
                id="state"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label for="zip" class="block text-sm font-medium text-gray-700 mb-2">
                Código postal
              </label>
              <input
                id="zip"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </form>

        <h2 class="text-xl font-semibold text-gray-900 mt-8 mb-6">Método de pago</h2>
        
        <div class="space-y-4">
          <div class="flex items-center space-x-2">
            <input
              id="card"
              name="payment"
              type="radio"
              checked
              class="text-blue-600 focus:ring-blue-500"
            />
            <label for="card" class="text-sm font-medium text-gray-700">
              Tarjeta de crédito/débito
            </label>
          </div>
          
          <div class="pl-6 space-y-4">
            <div>
              <label for="cardNumber" class="block text-sm font-medium text-gray-700 mb-2">
                Número de tarjeta
              </label>
              <input
                id="cardNumber"
                type="text"
                placeholder="1234 5678 9012 3456"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="expiry" class="block text-sm font-medium text-gray-700 mb-2">
                  Fecha de vencimiento
                </label>
                <input
                  id="expiry"
                  type="text"
                  placeholder="MM/YY"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label for="cvc" class="block text-sm font-medium text-gray-700 mb-2">
                  CVC
                </label>
                <input
                  id="cvc"
                  type="text"
                  placeholder="123"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="bg-white p-6 rounded-lg shadow-md h-fit">
        <h2 class="text-xl font-semibold text-gray-900 mb-6">Resumen del pedido</h2>
        
        <!-- Order Items -->
        <div class="space-y-4 mb-6">
          <div class="flex items-center space-x-3">
            <img
              src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"
              alt="Pikachu"
              class="w-12 h-12 object-contain"
            />
            <div class="flex-1">
              <h3 class="font-medium">Pikachu</h3>
              <p class="text-sm text-gray-600">Cantidad: 1</p>
            </div>
            <span class="font-medium">€25.99</span>
          </div>
        </div>
        
        <!-- Price Breakdown -->
        <div class="border-t pt-4 space-y-2">
          <div class="flex justify-between">
            <span>Subtotal:</span>
            <span>€25.99</span>
          </div>
          <div class="flex justify-between">
            <span>Envío:</span>
            <span>€4.99</span>
          </div>
          <div class="flex justify-between">
            <span>IVA (21%):</span>
            <span>€6.50</span>
          </div>
          <div class="border-t pt-2 flex justify-between text-lg font-semibold">
            <span>Total:</span>
            <span>€37.48</span>
          </div>
        </div>
        
        <button class="w-full mt-6 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors duration-200">
          Completar pedido
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Checkout logic will be implemented with the application layer
</script>
