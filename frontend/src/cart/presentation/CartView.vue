<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import { ArrowDown, ArrowLeft, ArrowRight, Minus, Plus, Trash2, MapPin } from 'lucide-vue-next'
import { useCartStore } from '../application/cartStore'
import { useAdventureStore } from '@/adventure/store'

import { money, pokemonName, number, typeName } from '@/shared/presentation/format'
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
const selectedId = ref<number>()
const atCounter = computed(
  () =>
    visibleLines.value.find((line) => line.pokemon.id === selectedId.value) ??
    visibleLines.value[0],
)
// Queue positions follow the walkable tiles around the shop shelves.
const queuePositions = [
  [44, 47],
  [62, 39],
  [84, 39],
  [54, 65],
  [38, 77],
  [58, 90],
] as const
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
    <div v-else class="mart-checkout">
      <section class="mart-stage" :aria-label="t('martLocation')">
        <header><MapPin :size="15" />{{ t('martLocation') }}</header>
        <div class="mart-floor">
          <img class="mart-map" src="/studio/viridian-mart.png" width="176" height="144" alt="" />
          <button
            v-for="(line, i) in visibleLines"
            :key="line.pokemon.id"
            class="queue-member"
            :aria-label="pokemonName(line.pokemon)"
            :aria-pressed="atCounter?.pokemon.id === line.pokemon.id"
            :style="{ left: queuePositions[i]![0] + '%', top: queuePositions[i]![1] + '%' }"
            @click="selectedId = line.pokemon.id"
          >
            <img
              :src="`https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${line.pokemon.id}.png`"
              alt=""
              @error.once="($event.target as HTMLImageElement).src = line.pokemon.image_url"
            />
          </button>
        </div>
        <div v-if="atCounter" class="counter-dialogue" aria-live="polite">
          <div>
            <small
              >{{ number(atCounter.pokemon.species_id ?? atCounter.pokemon.id) }} ·
              {{ atCounter.pokemon.types.map(typeName).join(' / ') }}</small
            ><strong>{{ pokemonName(atCounter.pokemon) }}</strong>
          </div>
          <RouterLink :to="`/pokemon/${atCounter.pokemon.id}`"
            >{{ t('studio.details') }} <ArrowRight :size="14"
          /></RouterLink>
        </div>
        <div v-if="!atCounter" class="counter-dialogue">
          <strong>{{ t('martRegister') }}</strong
          ><small>{{ t('units', cart.count) }}</small>
        </div>
      </section>
      <div v-if="!cart.lines.length" class="state-box empty-cart">
        <img class="chansey-empty" src="/studio/113.webp" alt="" width="96" height="96" />
        <div>
          <h2>{{ t('emptyCart') }}</h2>
          <p>{{ t('emptyCartBody') }}</p>
          <RouterLink class="button primary" to="/catalogo">{{ t('explore') }}</RouterLink>
        </div>
      </div>
      <div v-else class="order-ledger">
        <div class="cart-list-panel">
          <div class="register-heading">
            <span aria-hidden="true" class="power-led"></span>{{ t('martRegister') }}
          </div>
          <div class="cart-lines">
            <article
              v-for="line in visibleLines"
              :key="line.pokemon.id"
              class="cart-line"
              :data-selected="line.pokemon.id === atCounter?.pokemon.id"
            >
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
            <RouterLink class="button secondary" to="/catalogo">{{
              t('keepExploring')
            }}</RouterLink>
          </div>
        </footer>
      </div>
    </div>
  </section>
  <RecommendationsPanel :ids="cart.entries.map((entry) => entry.id)" />
</template>

<style scoped>
.order-sheet {
  width: min(100%, 1100px);
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
  font: 750 clamp(1.9rem, 4vw, 3rem) / 1.05 var(--font-mono);
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
.mart-checkout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  align-items: start;
  gap: clamp(12px, 2vw, 28px);
  margin-top: 16px;
}
.mart-stage {
  overflow: hidden;
  border: 3px solid #242c41;
  border-radius: 8px;
  background: #282e41;
  box-shadow: 0 4px 0 #1b2130;
}
.mart-stage header,
.register-heading {
  display: flex;
  align-items: center;
  gap: 9px;
  font: 750 0.8rem/1.4 var(--font-mono);
  padding: 10px 14px;
}
.mart-stage header {
  color: #fff4d5;
  background: #2b3946;
  border-bottom: 3px solid #94bb93;
}
.mart-floor {
  position: relative;
  isolation: isolate;
}
.mart-map {
  width: 100%;
  height: auto;
  display: block;
  image-rendering: pixelated;
}
.queue-member {
  position: absolute;
  display: grid;
  place-items: center;
  transform: translate(-50%, -50%);
  width: 17%;
  aspect-ratio: 1;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 0;
  background: transparent;
}
.queue-member img {
  position: absolute;
  left: 50%;
  top: 50%;
  translate: -50% -50%;
  display: block;
  width: 135%;
  max-width: none;
  height: 135%;
  object-fit: contain;
  image-rendering: pixelated;
  pointer-events: none;
  filter: drop-shadow(0 2px 0 #29253766);
}
.queue-member[aria-pressed='true']::before {
  content: '';
  position: absolute;
  top: 0;
  left: calc(50% - 5px);
  border-inline: 5px solid transparent;
  z-index: 1;
  border-top: 7px solid #ffea78;
  filter: drop-shadow(0 1px 0 #302d37);
}
.queue-member:focus-visible {
  outline: 2px solid #fff8b9;
  outline-offset: -3px;
  border-radius: 8px;
}
@media (prefers-reduced-motion: no-preference) {
  .queue-member[aria-pressed='true'] img {
    animation: mart-hop 0.45s ease-out;
  }
  @keyframes mart-hop {
    45% {
      transform: translateY(-7px);
    }
  }
}
.counter-dialogue {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin: 8px;
  padding: 10px 14px;
  background: #fff3d7;
  color: #302f40;
  border: 3px double #655d70;
  border-radius: 5px;
  font: 700 0.78rem/1.4 var(--font-mono);
}
.counter-dialogue strong,
.counter-dialogue small {
  display: block;
  overflow-wrap: anywhere;
}
.counter-dialogue strong {
  font-size: 1.12rem;
}
.counter-dialogue a {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  min-height: 44px;
  flex: none;
  text-decoration: underline;
}
.order-ledger {
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}
.register-heading {
  background: var(--feature);
  color: var(--ink);
  border-bottom: 1px solid var(--line);
}
.power-led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #56a882;
  box-shadow: 0 0 0 2px #56a88233;
}
.cart-line,
.cart-line:first-child {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border: 0;
  border-bottom: 1px dashed var(--line);
}
.cart-line[data-selected='true'] {
  box-shadow: inset 3px 0 var(--purple);
}
.cart-art.pokemon-palette {
  display: grid;
  place-items: center;
  background: color-mix(in srgb, var(--pokemon-tint) 22%, var(--surface));
  border-radius: 8px;
}
.cart-art img {
  width: 48px;
  height: 52px;
  padding: 1px;
  object-fit: contain;
}
.cart-item-copy {
  min-width: 0;
}
.cart-item-copy h2 {
  margin: 2px 0;
  font: 750 clamp(0.96rem, 1.6vw, 1.2rem) / 1.1 var(--font-body, sans-serif);
  overflow-wrap: anywhere;
}
.quantity-control {
  margin-top: 4px;
}
.quantity-control button,
.cart-line-total button {
  min-width: 44px;
  min-height: 44px;
}
.cart-line-total {
  gap: 0;
  min-width: 0;
}
.cart-line-total strong {
  font: 700 0.95rem/1.3 var(--font-mono);
}
.cart-pagination {
  justify-content: space-between;
}
.order-foot {
  display: grid;
  gap: 12px;
  padding: 14px;
  background: var(--surface);
  scroll-margin-top: 16px;
}
.order-tally {
  padding: 12px 16px;
  background: #233d38;
  color: #dbf0bd;
  border: 4px solid #4b5954;
  border-radius: 5px;
  box-shadow: inset 0 2px 4px #122c2880;
}
.order-tally .summary-total {
  text-align: right;
}
.order-foot .order-tally p {
  color: #d6e7c9;
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
  max-width: none;
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
    grid-template-columns: 42px minmax(0, 1fr) auto;
    gap: 6px;
    padding: 7px 8px;
  }
  .cart-art img {
    width: 42px;
    height: 46px;
  }
  .cart-line-total strong {
    font-size: 0.78rem;
  }
  .cart-line-total .text-button {
    font-size: 0.72rem;
  }
  .order-actions {
    width: 100%;
    max-width: none;
  }
}
@media (max-width: 760px) {
  .mart-checkout {
    grid-template-columns: minmax(0, 1fr);
  }
  .mart-stage {
    width: min(100%, 510px);
    justify-self: center;
    box-sizing: border-box;
  }
}
</style>
