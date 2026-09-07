<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ArrowLeft, ArrowRight, Minus, Plus, Trash2 } from 'lucide-vue-next'
import { useCartStore } from '../application/cartStore'

import { money, pokemonName, number } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
import RecommendationsPanel from '@/pokemon/presentation/RecommendationsPanel.vue'
const cart = useCartStore()
const page = ref(1)
const pages = computed(() => Math.max(1, Math.ceil(cart.lines.length / 6)))
const visibleLines = computed(() => cart.lines.slice((page.value - 1) * 6, page.value * 6))
watch(pages, (count) => {
  page.value = Math.min(page.value, count)
})
function changePage(value: number) {
  page.value = value
  document
    .querySelector('.cart-list-panel')
    ?.scrollIntoView({ block: 'start', behavior: 'instant' })
}

onMounted(() => {
  if (!cart.loading) void cart.hydrate()
})
</script>
<template>
  <RouterLink class="back-link" to="/catalogo"
    ><ArrowLeft :size="16" />{{ t('keepExploring') }}</RouterLink
  >
  <div class="section-heading">
    <div>
      <p class="eyebrow">{{ t('selection') }}</p>
      <h1>{{ t('cart') }}</h1>
    </div>
    <span>{{ t('units', cart.count) }}</span>
  </div>
  <p v-if="cart.loading" role="status" class="state-box">{{ t('loadingCart') }}</p>
  <div v-else-if="cart.error" role="alert" class="state-box">
    <p>{{ t('catalogError') }}</p>
    <button class="button primary" @click="cart.hydrate">{{ t('retry') }}</button>
  </div>
  <div v-else-if="!cart.lines.length" class="state-box empty-cart">
    <img
      class="chansey-empty"
      src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/113.png"
      alt="Chansey"
      width="180"
      height="180"
    />
    <h2>{{ t('emptyCart') }}</h2>
    <p>{{ t('emptyCartBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('explore') }}</RouterLink>
  </div>
  <div v-else class="cart-layout">
    <div class="cart-list-panel">
      <div class="cart-lines">
        <article v-for="line in visibleLines" :key="line.pokemon.id" class="cart-line">
          <RouterLink :to="`/pokemon/${line.pokemon.id}`" class="cart-art"
            ><PokemonImage :src="line.pokemon.image_url" :name="pokemonName(line.pokemon)"
          /></RouterLink>
          <div class="cart-item-copy">
            <span class="dex-number">{{ number(line.pokemon.species_id ?? line.pokemon.id) }}</span>
            <h2>
              <RouterLink :to="`/pokemon/${line.pokemon.id}`">{{
                pokemonName(line.pokemon)
              }}</RouterLink>
            </h2>
            <p>{{ t('perUnit', { price: money(line.pokemon.price_cents) }) }}</p>
            <div class="quantity-control">
              <button
                :aria-label="t('decrease', { name: pokemonName(line.pokemon) })"
                :disabled="line.quantity === 1"
                @click="cart.setQuantity(line.pokemon.id, line.quantity - 1)"
              >
                <Minus :size="15" /></button
              ><span :aria-label="t('quantity', { name: pokemonName(line.pokemon) })">{{
                line.quantity
              }}</span
              ><button
                :aria-label="t('increase', { name: pokemonName(line.pokemon) })"
                :disabled="line.quantity >= line.pokemon.stock"
                @click="cart.setQuantity(line.pokemon.id, line.quantity + 1)"
              >
                <Plus :size="15" />
              </button>
            </div>
          </div>
          <div class="cart-line-total">
            <strong>{{ money(line.pokemon.price_cents * line.quantity) }}</strong
            ><button
              class="text-button"
              :aria-label="t('removePokemon', { name: pokemonName(line.pokemon) })"
              @click="cart.remove(line.pokemon.id)"
            >
              <Trash2 :size="16" />{{ t('remove') }}
            </button>
          </div>
        </article>
      </div>
      <nav v-if="pages > 1" class="pagination cart-pagination" :aria-label="t('cartPage')">
        <button class="button secondary" :disabled="page === 1" @click="changePage(page - 1)">
          <ArrowLeft :size="16" />{{ t('previous') }}</button
        ><span>{{ t('pageOf', { page, pages }) }}</span
        ><button class="button secondary" :disabled="page === pages" @click="changePage(page + 1)">
          {{ t('next') }}<ArrowRight :size="16" />
        </button>
      </nav>
    </div>
    <div class="checkout-scene">
      <aside class="cart-summary">
        <p class="ticket-label">{{ t('ticketLabel') }}</p>

        <h2>{{ t('summary') }}</h2>
        <div>
          <span>{{ t('subtotal', { units: t('units', cart.count) }) }}</span
          ><strong>{{ money(cart.total) }}</strong>
        </div>
        <div class="summary-total">
          <span>{{ t('total') }}</span
          ><strong>{{ money(cart.total) }}</strong>
        </div>
        <p>{{ t('cartSaved') }}</p>
        <p class="demo-note">{{ t('demoCart') }}</p>
        <RouterLink class="button secondary" to="/catalogo">{{ t('keepExploring') }}</RouterLink>
      </aside>
      <div class="chansey-summary">
        <img
          src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/113.png"
          alt="Chansey"
          width="220"
          height="220"
        />
        <p>{{ t('chanseyCopy') }}</p>
      </div>
    </div>
  </div>
  <RecommendationsPanel :ids="cart.entries.map((entry) => entry.id)" />
</template>

<style scoped>
.cart-layout {
  grid-template-columns: minmax(0, 1fr) minmax(0, 520px);
  gap: 28px;
}
.cart-list-panel {
  min-width: 0;
  scroll-margin-top: 24px;
}
.cart-line {
  padding: 16px 0;
  gap: 14px;
}
.cart-art {
  flex-shrink: 0;
}
.checkout-scene {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 200px;
  align-items: start;
  position: sticky;
  top: 24px;
}
.chansey-summary {
  padding: 40px 0 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.chansey-summary img {
  width: 220px;
  max-width: 110%;
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 10px 8px #0002);
}
.chansey-summary p {
  font-size: 0.78rem;
  line-height: 1.7;
  text-align: center;
  color: var(--muted-strong);
  padding: 0 10px;
}
.cart-summary {
  border-radius: 12px 12px 0 0;
  position: relative;
  padding: 24px 22px 36px;
  background: var(--surface);
  border: 1px solid var(--line);
  clip-path: polygon(
    0 0,
    100% 0,
    100% 98%,
    95% 100%,
    90% 98%,
    85% 100%,
    80% 98%,
    75% 100%,
    70% 98%,
    65% 100%,
    60% 98%,
    55% 100%,
    50% 98%,
    45% 100%,
    40% 98%,
    35% 100%,
    30% 98%,
    25% 100%,
    20% 98%,
    15% 100%,
    10% 98%,
    5% 100%,
    0 98%
  );
}
.cart-summary .ticket-label {
  font-family: monospace;
  letter-spacing: 0.16em;
  font-size: 0.65rem;
  text-align: center;
  color: var(--purple);
  margin: 0 0 20px;
  padding: 0 0 16px;
  border-bottom: 1px dashed var(--line);
}
.cart-summary h2 {
  font-size: 1.25rem;
}
.cart-summary .summary-total {
  border-top: 1px dashed var(--line);
  padding-top: 20px;
}
.cart-summary > .demo-note {
  border-top: 1px dashed var(--line);
  padding-top: 16px;
}
.chansey-empty {
  display: block;
  object-fit: contain;
  margin: 0 auto 12px;
  width: 240px;
  height: 240px;
  max-width: 100%;
}
.cart-pagination {
  gap: 12px;
  justify-content: space-between;
}
.cart-pagination .button {
  padding: 10px;
  font-size: 0.75rem;
}
@media (max-width: 1100px) {
  .cart-layout {
    grid-template-columns: minmax(0, 1fr) 300px;
  }
  .checkout-scene {
    grid-template-columns: 1fr;
  }
  .chansey-summary {
    grid-row: 1;
    padding: 0 0 14px;
  }
  .chansey-summary img {
    width: 180px;
    height: 180px;
  }
  .chansey-summary p {
    max-width: 280px;
    margin: 0;
  }
  .cart-summary {
    grid-row: 2;
  }
}
@media (max-width: 760px) {
  .cart-layout {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  .checkout-scene {
    position: static;
    width: 100%;
    max-width: 460px;
    justify-self: center;
  }
  .chansey-summary img {
    width: 200px;
    height: 200px;
  }
  .cart-pagination {
    gap: 6px;
  }
  .cart-pagination span {
    font-size: 0.7rem;
  }
  .cart-pagination .button {
    gap: 4px;
    padding: 9px 7px;
  }
}
</style>
