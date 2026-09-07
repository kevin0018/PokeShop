<script setup lang="ts">
import { nextTick, onUnmounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { PopoverRoot, PopoverAnchor, PopoverPortal, PopoverContent } from 'reka-ui'
import { ShoppingBag, ArrowRight, X } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import { useCartStore } from '../application/cartStore'
import { money, pokemonName } from '@/shared/presentation/format'
import PokemonImage from '@/components/PokemonImage.vue'
const cart = useCartStore()
const route = useRoute()
watch(
  () => route.fullPath,
  () => {
    close()
    suppressed = false
  },
)
const { t } = useI18n(),
  open = ref(false),
  pinned = ref(false),
  trigger = ref<HTMLButtonElement>(),
  closeButton = ref<HTMLButtonElement>()
let timer: ReturnType<typeof setTimeout> | undefined,
  suppressed = false,
  hovering = false
const fine = () => window.matchMedia('(hover: hover) and (pointer: fine)').matches
function enter() {
  hovering = true
  clearTimeout(timer)
  if (fine() && !suppressed) open.value = true
}
function blur() {
  suppressed = false
  schedule()
}
function focus() {
  if (!suppressed && fine()) open.value = true
}
function leave() {
  hovering = false
  suppressed = false
  schedule()
}
function schedule() {
  clearTimeout(timer)
  timer = setTimeout(() => {
    if (
      !pinned.value &&
      !hovering &&
      document.activeElement !== trigger.value &&
      !document.activeElement?.closest('.cart-preview')
    )
      open.value = false
  }, 180)
}
function click() {
  if (pinned.value) {
    close(true)
    return
  }
  suppressed = false
  pinned.value = true
  open.value = true
  void nextTick(() => closeButton.value?.focus())
}
function outside(event: CustomEvent<{ originalEvent: Event }>) {
  if (trigger.value?.contains(event.detail.originalEvent.target as Node)) {
    event.preventDefault()
    return
  }
  close()
}
function close(restore = false) {
  clearTimeout(timer)
  suppressed = true
  pinned.value = false
  open.value = false
  if (restore) void nextTick(() => trigger.value?.focus())
}
onUnmounted(() => clearTimeout(timer))
</script>
<template>
  <PopoverRoot :open="open" @update:open="!$event && close()">
    <PopoverAnchor as-child>
      <button
        ref="trigger"
        type="button"
        class="cart-link cart-preview-trigger"
        :aria-expanded="open"
        aria-haspopup="dialog"
        @mouseenter="enter"
        @mouseleave="leave"
        @focus="focus"
        @blur="blur"
        @click="click"
      >
        <ShoppingBag :size="19" aria-hidden="true" /><span>{{ t('cart') }}</span>
        <span class="cart-count">{{ cart.count }}</span>
      </button>
    </PopoverAnchor>
    <PopoverPortal>
      <PopoverContent
        class="cart-preview"
        align="end"
        :side-offset="12"
        :collision-padding="12"
        :aria-label="t('cartPreview')"
        @open-auto-focus.prevent
        @close-auto-focus.prevent
        @escape-key-down.prevent="close(true)"
        @pointer-down-outside="outside"
        @focus-outside="outside"
        @mouseenter="enter"
        @mouseleave="leave"
        @focusout="schedule"
      >
        <div class="cart-preview-heading">
          <h2>{{ t('cartPreview') }}</h2>
          <button
            ref="closeButton"
            type="button"
            class="icon-button"
            :aria-label="t('close')"
            @click="close(true)"
          >
            <X :size="18" />
          </button>
        </div>
        <p v-if="cart.loading" role="status">{{ t('loadingCart') }}</p>
        <div v-else-if="cart.error" role="alert">
          <p>{{ t('catalogError') }}</p>
          <button class="button secondary" @click="cart.hydrate">{{ t('retry') }}</button>
        </div>
        <template v-else>
          <ul v-if="cart.recentLines.length" class="cart-preview-lines">
            <li v-for="line in cart.recentLines" :key="line.pokemon.id">
              <RouterLink :to="`/pokemon/${line.pokemon.id}`" @click="close()">
                <div class="cart-preview-art">
                  <PokemonImage :src="line.pokemon.image_url" :name="pokemonName(line.pokemon)" />
                </div>
                <div class="cart-preview-copy">
                  <strong>{{ pokemonName(line.pokemon) }}</strong>
                  <span>{{ line.quantity }} × {{ money(line.pokemon.price_cents) }}</span>
                </div>
                <strong>{{ money(line.quantity * line.pokemon.price_cents) }}</strong>
              </RouterLink>
            </li>
          </ul>
          <p v-else>{{ t('emptyCart') }}</p>
          <div class="cart-preview-total">
            <span>{{ t('total') }} · {{ t('units', cart.count) }}</span
            ><strong>{{ money(cart.total) }}</strong>
          </div>
        </template>
        <RouterLink class="button primary cart-preview-link" to="/carrito" @click="close()"
          >{{ t('viewFullCart') }}<ArrowRight :size="16"
        /></RouterLink>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
<style>
.cart-preview-trigger {
  background: transparent;
  border: 0;
  padding: 10px 0;
  color: var(--ink);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
}
.cart-preview-trigger[aria-expanded='true'] {
  color: var(--purple);
}
.cart-preview {
  z-index: 120;
  width: min(390px, calc(100vw - 24px));
  max-height: calc(100dvh - 24px);
  overflow-y: auto;
  padding: 20px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--surface);
  color: var(--ink);
  box-shadow: 0 18px 60px #0003;
}
.cart-preview-heading,
.cart-preview-total {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.cart-preview-heading h2 {
  font-size: 1.05rem;
  margin: 0;
}
.cart-preview-lines {
  list-style: none;
  padding: 0;
  margin: 12px 0;
}
.cart-preview-lines li + li {
  border-top: 1px solid var(--line);
}
.cart-preview-lines a {
  display: grid;
  grid-template-columns: 58px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  font-size: 0.8rem;
}
.cart-preview-art {
  height: 58px;
  border-radius: 12px;
  background: var(--lavender);
}
.cart-preview-art img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.cart-preview-copy {
  display: grid;
  gap: 5px;
  overflow-wrap: anywhere;
}
.cart-preview-copy span {
  color: var(--muted-strong);
  font-size: 0.75rem;
}
.cart-preview-total {
  border-top: 1px dashed var(--line);
  padding: 16px 0;
  font-size: 0.85rem;
}
.cart-preview-link {
  width: 100%;
}
@media (max-width: 400px) {
  .cart-preview {
    padding: 16px;
  }
  .cart-preview-lines a {
    grid-template-columns: 46px minmax(0, 1fr);
  }
  .cart-preview-lines a > strong {
    grid-column: 2;
  }
  .cart-preview-art {
    height: 46px;
    grid-row: span 2;
  }
}
</style>
