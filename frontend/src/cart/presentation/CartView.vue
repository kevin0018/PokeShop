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
  <section class="order-sheet" aria-labelledby="order-title">
    <RouterLink class="back-link" to="/catalogo"
      ><ArrowLeft :size="16" />{{ t('keepExploring') }}</RouterLink
    >
    <header class="bag-heading">
      <h1 id="order-title">{{ t('cart') }}</h1>
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
      <img class="chansey-empty" src="/studio/113.webp" alt="" width="96" height="96" />
      <div>
        <h2>{{ t('emptyCart') }}</h2>
        <p>{{ t('emptyCartBody') }}</p>
        <RouterLink class="button primary" to="/catalogo">{{ t('explore') }}</RouterLink>
      </div>
    </div>
    <div v-else class="order-ledger">
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
              <span class="dex-number">{{
                number(line.pokemon.species_id ?? line.pokemon.id)
              }}</span>
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
          ><button
            class="button secondary"
            :disabled="page === pages"
            @click="changePage(page + 1)"
          >
            {{ t('next') }}<ArrowRight :size="16" />
          </button>
        </nav>
      </div>
      <footer id="cart-summary" class="order-foot" tabindex="-1">
        <div class="order-tally">
          <img src="/studio/113.webp" alt="" width="68" height="68" />
          <div>
            <p>{{ t('subtotal', { units: t('units', cart.count) }) }}</p>
            <div class="summary-total">
              <span class="sr-only">{{ t('total') }}</span
              ><strong>{{ price(cart.total) }}</strong>
            </div>
            <p v-if="game.trainer" class="cart-balance">
              {{ t('shopBalance') }} ·
              {{ t('adventure.credits', { amount: game.trainer.credits }) }}
            </p>
          </div>
        </div>
        <div class="order-actions">
          <template v-if="game.trainer">
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
          <p v-else>{{ t('demoCart') }}</p>
          <RouterLink class="button secondary" to="/catalogo">{{ t('keepExploring') }}</RouterLink>
        </div>
      </footer>
    </div>
  </section>
  <RecommendationsPanel :ids="cart.entries.map((entry) => entry.id)" />
</template>

<style scoped>
.order-sheet {
  width: min(100%, 900px);
  margin: 0 auto;
}
.order-sheet > .back-link {
  margin-bottom: 12px;
}
.bag-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 4px 18px;
  padding-bottom: 14px;
  border-bottom: 3px double var(--border-strong);
}
.bag-heading h1 {
  margin: 0;
  font:
    600 clamp(2.2rem, 5vw, 4.2rem) / 1.08 Georgia,
    serif;
  letter-spacing: -0.055em;
}
.cart-heading-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px 14px;
  font-size: 0.82rem;
}
.cart-heading-actions > span {
  color: var(--muted-strong);
}
.cart-heading-actions .secondary {
  border: 0;
  background: transparent;
  color: var(--muted-strong);
  padding: 0 4px;
  min-height: 44px;
}
.cart-summary-link {
  display: none;
}
.cart-line,
.cart-line:first-child {
  display: grid;
  grid-template-columns: clamp(96px, 15vw, 148px) minmax(0, 1fr) auto;
  gap: clamp(12px, 3vw, 32px);
  align-items: center;
  padding: 16px 0;
  border: 0;
  border-bottom: 1px solid var(--line);
}
.cart-art.pokemon-palette {
  display: grid;
  place-items: center;
  position: relative;
  isolation: isolate;
  background: transparent;
  border-radius: 0;
}
.cart-art::before {
  content: '';
  position: absolute;
  inset: 12% 8%;
  border-radius: 50%;
  z-index: -1;
  background: color-mix(in srgb, var(--pokemon-tint) 33%, var(--surface));
  box-shadow:
    0 0 0 3px var(--surface),
    0 0 0 4px color-mix(in srgb, var(--pokemon-tint) 40%, var(--line));
}
.cart-art img {
  width: 100%;
  height: clamp(90px, 12vw, 128px);
  padding: 2px;
  object-fit: contain;
  filter: drop-shadow(1px 3px 1px #241c2222);
}
.cart-item-copy {
  min-width: 0;
}
.cart-item-copy h2 {
  margin: 2px 0 4px;
  font:
    600 clamp(1.25rem, 2.4vw, 1.9rem) / 1.12 Georgia,
    serif;
  overflow-wrap: anywhere;
}
.quantity-control {
  margin-top: 6px;
}
.quantity-control button,
.cart-line-total button {
  min-width: 44px;
  min-height: 44px;
}
.cart-line-total {
  gap: 2px;
  min-width: 0;
}
.cart-line-total strong {
  font: 700 clamp(1rem, 2vw, 1.35rem) / 1.3 var(--font-mono);
  font-variant-numeric: tabular-nums;
}
.cart-pagination {
  justify-content: space-between;
}
.order-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px 24px;
  flex-wrap: wrap;
  background: var(--surface);
  padding: clamp(14px, 2.5vw, 26px);
  border-bottom: 3px double var(--border-strong);
  scroll-margin-top: 16px;
}
.order-tally {
  display: flex;
  align-items: center;
  gap: 14px;
}
.order-tally img {
  width: clamp(42px, 6vw, 68px);
  height: auto;
}
.order-tally p,
.order-actions p {
  font-size: 0.82rem;
  color: var(--muted-strong);
  line-height: 1.4;
  margin: 0;
}
.summary-total strong {
  font: 750 clamp(1.65rem, 3vw, 2.4rem) / 1.2 var(--font-body, sans-serif);
  letter-spacing: -0.045em;
  overflow-wrap: anywhere;
}
.order-actions {
  display: grid;
  gap: 6px;
  justify-items: stretch;
  max-width: 32ch;
}
.order-actions .button {
  min-height: 44px;
}
.empty-cart {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: left;
  gap: 20px;
  padding: clamp(24px, 5vw, 56px) 10px;
  border: 0;
  border-bottom: 3px double var(--border-strong);
  border-radius: 0;
  background: transparent;
}
.empty-cart img {
  width: clamp(60px, 12vw, 96px);
  height: auto;
}
.empty-cart p {
  margin: 6px 0 12px;
}
@media (max-width: 600px) {
  .bag-heading {
    display: block;
    padding-bottom: 4px;
  }
  .cart-heading-actions {
    gap: 3px 9px;
  }
  .cart-heading-actions .secondary {
    margin-left: auto;
  }
  .cart-summary-link {
    display: inline-flex;
    min-height: 44px;
  }
  .cart-line,
  .cart-line:first-child {
    grid-template-columns: minmax(66px, 25%) minmax(0, 1fr);
    gap: 4px 16px;
    padding: 12px 0;
  }
  .cart-art {
    grid-row: span 2;
  }
  .cart-line-total {
    grid-column: 2;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
  }
  .cart-line-total .text-button {
    font-size: 0.75rem;
  }
  .order-actions {
    width: 100%;
    max-width: none;
  }
}
</style>
