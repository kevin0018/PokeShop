<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ArrowDown, ArrowLeft, ArrowRight, Minus, Plus, Trash2 } from 'lucide-vue-next'
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
  <div class="section-heading bag-heading">
    <div>
      <p class="eyebrow">{{ t('selection') }}</p>
      <h1>{{ t('cart') }}</h1>
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
  </div>
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
        <p class="ticket-label">{{ t('ticketLabel') }}</p>

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
          <p>{{ t('adventure.credits', { amount: game.trainer.credits }) }}</p>
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
.bag-heading {
  padding: clamp(16px, 3vw, 34px);
  border-radius: var(--shop-radius);
  background: var(--sign);
  color: var(--sign-ink);
  border-bottom: 5px solid var(--studio-yellow);
}
.bag-heading .eyebrow,
.bag-heading .cart-heading-actions,
.bag-heading .text-button {
  color: var(--sign-label);
}
.bag-heading h1 {
  margin: 0;
}
.bag-heading .secondary {
  color: var(--ink);
}
.cart-item-copy h2 {
  font: 900 clamp(1.6rem, 2.5vw, 2.25rem) / 1.14 var(--font-display);
}
.checkout-scene .cart-summary {
  border-top: 5px solid var(--purple);
}
@media (max-width: 700px) {
  .bag-heading {
    align-items: start;
    flex-direction: column;
    gap: 10px;
  }
}

.cart-heading-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--muted-strong);
}

.cart-summary-link {
  display: none;
}

.cart-layout {
  grid-template-columns: minmax(0, 1fr) minmax(280px, 34%);
  gap: 24px;
}

.cart-list-panel,
.cart-item-copy {
  min-width: 0;
}

.cart-lines {
  display: grid;
  gap: 10px;
}

.cart-line,
.cart-line:first-child {
  gap: 14px;
  padding: 12px;
  border: 1px solid var(--line);
  border-radius: var(--shop-radius);
  background: var(--surface);
}

.cart-art {
  flex-shrink: 0;
}

.cart-item-copy h2 {
  overflow-wrap: anywhere;
}

.cart-line-total {
  gap: 4px;
  min-width: max-content;
}

.quantity-control button {
  min-width: 44px;
  min-height: 44px;
}

.checkout-scene {
  position: sticky;
  top: 24px;
}

.cart-summary.pokemon-palette {
  margin: 0;
  padding: 20px;
  border-radius: var(--shop-radius);
  scroll-margin-top: 14px;
}

.cart-summary > .ticket-label {
  margin: 0 0 14px;
  padding-bottom: 10px;
  border-bottom: 1px dashed var(--control-border);
  color: var(--purple);
  font: 700 0.7rem/1.45 var(--font-mono);
  letter-spacing: 0.12em;
}

.cart-summary h2 {
  margin-bottom: 14px;
  font: 900 clamp(1.8rem, 2.5vw, 2.4rem) / 1.05 var(--font-display);
}

.cart-summary .summary-total {
  align-items: baseline;
  border-top: 1px dashed var(--control-border);
  padding-top: 14px;
  margin-top: 14px;
  font-size: 1.25rem;
}

.cart-summary .summary-total strong {
  font-variant-numeric: tabular-nums;
  font-size: clamp(1.3rem, 2.8vw, 2rem);
}

.cart-summary > p {
  margin-top: 14px;
}

.cart-summary > .demo-note {
  padding-top: 12px;
  border-top: 1px dashed var(--control-border);
}

.cart-summary .button {
  margin-top: 12px;
}

.chansey-summary {
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  align-items: center;
  gap: 8px;
  margin: 12px 0 0;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: var(--shop-radius);
  color: var(--muted-strong);
  font-size: 0.82rem;
}

.chansey-summary img {
  width: 70px;
  height: auto;
  object-fit: contain;
}

.chansey-empty {
  display: block;
  object-fit: contain;
  margin: 0 auto 12px;
  width: min(100%, 155px);
  height: auto;
}

.cart-pagination {
  justify-content: space-between;
}

.cart-pagination .button {
  padding-inline: 8px;
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
  }
}

@media (max-width: 460px) {
  .cart-line,
  .cart-line:first-child {
    display: grid;
    grid-template-columns: minmax(0, 62px) minmax(0, 1fr);
    align-items: start;
    gap: 8px 12px;
  }

  .cart-art img {
    width: 100%;
    height: 72px;
  }

  .cart-line-total {
    grid-column: 1 / -1;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--line);
  }
}
</style>
