<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ArrowDown, ArrowLeft, ArrowRight, Minus, Plus, ShoppingBag, Trash2 } from 'lucide-vue-next'
import { useCartStore } from '../application/cartStore'
import { useAdventureStore } from '@/adventure/store'

import { money, pokemonName, number } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
import RecommendationsPanel from '@/pokemon/presentation/RecommendationsPanel.vue'
const cart = useCartStore()
const game = useAdventureStore()
const alreadyPurchased = computed(
  () =>
    cart.lines.length > 0 &&
    cart.lines.every((line) => game.trainer?.collection.some((p) => p.id === line.pokemon.id)),
)
const price = (amount: number) =>
  game.trainer ? t('adventure.credits', { amount }) : money(amount)
const purchased = ref(false)
async function checkout() {
  purchased.value = Boolean(await cart.checkout())
}
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
  <header class="bag-heading">
    <div>
      <p class="eyebrow"><ShoppingBag :size="16" />{{ t('selection') }}</p>
      <h1>{{ t('cart') }}</h1>
    </div>
    <div class="bag-host" aria-hidden="true">
      <img
        src="/studio/113.webp"
        :class="{ 'chansey-empty': !cart.entries.length }"
        alt=""
        width="310"
        height="310"
      />
    </div>
    <div class="cart-heading-actions">
      <span>{{ t('units', cart.count) }}</span>
      <a
        v-if="!cart.loading && !cart.error && cart.lines.length"
        href="#cart-summary"
        class="text-button cart-summary-link"
      >
        {{ t('total') }} {{ price(cart.total) }}<ArrowDown :size="15" aria-hidden="true" />
      </a>
      <button
        v-if="cart.entries.length"
        class="button secondary"
        :disabled="game.busy"
        @click="cart.clear"
      >
        <Trash2 :size="16" />{{ t('clearCart') }}
      </button>
    </div>
  </header>
  <p v-if="purchased" role="status" class="state-box">
    {{ t('adventure.purchaseCompleted') }}
    <RouterLink to="/aventura">{{ t('adventure.teamTab') }}</RouterLink>
  </p>
  <p v-if="game.trainer && game.error" role="alert" class="state-box">
    {{ t(`adventure.errors.${game.error}`) }}
  </p>
  <p v-if="cart.loading" role="status" class="state-box">{{ t('loadingCart') }}</p>
  <div v-else-if="cart.error" role="alert" class="state-box">
    <p>{{ t('catalogError') }}</p>
    <button class="button primary" @click="cart.hydrate">{{ t('retry') }}</button>
  </div>
  <div v-else-if="!cart.lines.length" class="state-box empty-cart">
    <h2>{{ t('emptyCart') }}</h2>
    <p>{{ t('emptyCartBody') }}</p>
    <RouterLink class="button primary" to="/catalogo">{{ t('explore') }}</RouterLink>
  </div>
  <div v-else class="cart-layout">
    <div class="cart-list-panel">
      <div class="cart-lines">
        <article v-for="line in visibleLines" :key="line.pokemon.id" class="cart-line">
          <RouterLink
            :to="`/pokemon/${line.pokemon.id}`"
            class="cart-art pokemon-palette"
            :data-type="line.pokemon.types[0]"
            ><PokemonImage :src="line.pokemon.image_url" :name="pokemonName(line.pokemon)"
          /></RouterLink>
          <div class="cart-item-copy">
            <span class="dex-number">{{ number(line.pokemon.species_id ?? line.pokemon.id) }}</span>
            <h2>
              <RouterLink :to="`/pokemon/${line.pokemon.id}`">{{
                pokemonName(line.pokemon)
              }}</RouterLink>
            </h2>
            <p>{{ t('perUnit', { price: price(line.pokemon.price_cents) }) }}</p>
            <div v-if="!game.trainer" class="quantity-control">
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
            <strong>{{ price(line.pokemon.price_cents * line.quantity) }}</strong
            ><button
              class="text-button"
              :aria-label="t('removePokemon', { name: pokemonName(line.pokemon) })"
              :disabled="game.busy"
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
      <aside
        id="cart-summary"
        tabindex="-1"
        class="cart-summary pokemon-palette"
        :data-type="cart.recentLines[0]?.pokemon.types[0]"
      >
        <h2>{{ t('summary') }}</h2>
        <div>
          <span>{{ t('subtotal', { units: t('units', cart.count) }) }}</span
          ><strong>{{ price(cart.total) }}</strong>
        </div>
        <div class="summary-total">
          <span>{{ t('total') }}</span
          ><strong>{{ price(cart.total) }}</strong>
        </div>
        <p>{{ t('cartSaved') }}</p>
        <template v-if="game.trainer">
          <div class="cart-balance">
            <span>{{ t('shopBalance') }}</span
            ><strong>{{ t('adventure.credits', { amount: game.trainer.credits }) }}</strong>
          </div>
          <p v-if="cart.total > game.trainer.credits && !alreadyPurchased">
            {{ t('adventure.insufficient') }}
          </p>
          <button
            class="button primary"
            :disabled="
              game.busy ||
              !cart.lines.length ||
              (cart.total > game.trainer.credits && !alreadyPurchased)
            "
            @click="checkout"
          >
            {{ t('adventure.confirmPurchase') }}
          </button>
        </template>
        <p v-else class="demo-note">{{ t('demoCart') }}</p>
        <RouterLink class="button secondary" to="/catalogo">{{ t('keepExploring') }}</RouterLink>
      </aside>
    </div>
  </div>
  <RecommendationsPanel :ids="cart.entries.map((entry) => entry.id)" />
</template>

<style scoped>
.bag-heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 0 14px;
  padding: 0 clamp(14px, 2vw, 26px);
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--ink);
  border-radius: 14px;
  margin-bottom: 20px;
}
.bag-heading > div:first-child {
  padding: 18px 0;
}
.bag-heading .eyebrow {
  display: flex;
  align-items: center;
  gap: 6px;
  font: 700 0.72rem/1.4 var(--font-mono);
  color: var(--purple);
}
.bag-heading h1 {
  margin: 4px 0 0;
  font: 750 clamp(1.8rem, 4vw, 3rem) / 1.05 var(--font-body, sans-serif);
  letter-spacing: -0.045em;
}
.bag-host img {
  display: block;
  width: clamp(56px, 8vw, 96px);
  height: auto;
}
.cart-heading-actions {
  grid-column: 1/-1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 14px;
  border-top: 1px solid var(--line);
  padding: 4px clamp(12px, 2vw, 26px);
  min-height: 44px;
  font: 700 0.78rem/1.4 var(--font-mono);
}
.cart-heading-actions .secondary {
  margin-left: auto;
  background: transparent;
  border: 0;
  color: var(--ink);
  min-height: 44px;
  padding: 4px;
}
.cart-summary-link {
  display: none;
}
.cart-layout {
  grid-template-columns: minmax(0, 1fr) minmax(285px, 32%);
  gap: clamp(16px, 3vw, 38px);
}
.cart-lines {
  display: grid;
  gap: 12px;
}
.cart-line,
.cart-line:first-child {
  display: grid;
  grid-template-columns: minmax(76px, 18%) minmax(0, 1fr) auto;
  gap: 14px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  background: var(--surface);
}
.cart-art.pokemon-palette {
  display: grid;
  place-items: center;
  align-self: stretch;
  border-radius: 0;
  background: color-mix(in srgb, var(--pokemon-tint) 22%, var(--surface));
}
.cart-art img {
  width: 100%;
  height: clamp(105px, 11vw, 150px);
  object-fit: contain;
  filter: drop-shadow(2px 2px 0 #241c2266);
}
.cart-item-copy {
  min-width: 0;
  padding-block: 10px;
}
.cart-item-copy h2 {
  font: 750 clamp(1.1rem, 2vw, 1.6rem) / 1.2 var(--font-body, sans-serif);
  overflow-wrap: anywhere;
}
.quantity-control {
  margin-top: 8px;
  border-radius: 2px;
}
.quantity-control button {
  min-width: 44px;
  min-height: 44px;
  color: var(--ink);
}
.cart-line-total {
  padding: 8px 12px 8px 0;
  gap: 2px;
}
.cart-line-total strong {
  font: 700 clamp(1rem, 1.6vw, 1.3rem) / 1.2 var(--font-body, sans-serif);
}
.cart-line-total button {
  min-height: 44px;
}
.checkout-scene {
  position: sticky;
  top: 12px;
  min-width: 0;
}
.checkout-scene .cart-summary {
  position: relative;
  margin: 0;
  scroll-margin-top: 14px;
  padding: clamp(16px, 2vw, 26px);
  border: 1px solid var(--line);
  border-radius: 14px;
  color: var(--ink);
  background: var(--surface);
}
.cart-summary h2,
.empty-cart h2 {
  font: 750 clamp(1.25rem, 2vw, 1.6rem) / 1.2 var(--font-body, sans-serif);
  letter-spacing: -0.035em;
}
.cart-summary > p {
  margin-top: 12px;
  color: var(--muted-strong);
}
.cart-summary .summary-total {
  border-top: 1px solid var(--line);
  padding-top: 14px;
  margin-top: 12px;
  align-items: baseline;
}
.summary-total strong {
  font: 750 clamp(1.4rem, 2vw, 1.75rem) / 1.1 var(--font-body, sans-serif);
  overflow-wrap: anywhere;
}
.cart-balance {
  margin-top: 12px;
  color: var(--muted-strong);
}
.cart-summary .button,
.empty-cart .button {
  margin-top: 12px;
  min-height: 44px;
  border-radius: 8px;
}
.empty-cart {
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  text-align: left;
  padding: clamp(20px, 3vw, 40px);
}
.empty-cart p {
  margin-block: 10px;
}
.cart-pagination {
  justify-content: space-between;
}
.cart-pagination .button {
  padding-inline: 8px;
}
@media (prefers-reduced-motion: no-preference) {
  .bag-host img {
    animation: bag-host-enter 320ms ease-out both;
  }
  @keyframes bag-host-enter {
    from {
      opacity: 0;
      transform: translateX(14px) rotate(4deg);
    }
  }
}
@media (max-width: 760px) {
  .cart-layout {
    grid-template-columns: minmax(0, 1fr);
  }
  .checkout-scene {
    position: static;
  }
  .cart-summary-link {
    display: inline-flex;
    min-height: 44px;
    color: var(--ink);
  }
}
@media (max-width: 520px) {
  .bag-heading > div:first-child {
    padding: 16px 4px 18px 12px;
  }
  .cart-heading-actions {
    gap: 0 8px;
  }
  .cart-heading-actions .secondary {
    font-size: 0.78rem;
  }
  .cart-line,
  .cart-line:first-child {
    grid-template-columns: minmax(75px, 32%) minmax(0, 1fr);
    gap: 0 12px;
  }
  .cart-item-copy {
    padding-right: 8px;
  }
  .cart-line-total {
    grid-column: 1/-1;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid var(--line);
    padding: 0 12px;
  }
}
</style>
