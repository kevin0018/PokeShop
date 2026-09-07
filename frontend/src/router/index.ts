import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'catalog',
      component: () => import('@/pokemon/presentation/CatalogView.vue'),
    },
    {
      path: '/pokemon/:id',
      name: 'pokemon',
      component: () => import('@/pokemon/presentation/PokemonDetailView.vue'),
    },
    { path: '/carrito', name: 'cart', component: () => import('@/cart/presentation/CartView.vue') },
    { path: '/:pathMatch(.*)*', component: () => import('@/views/NotFoundView.vue') },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
