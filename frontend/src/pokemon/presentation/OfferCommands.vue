<script setup lang="ts">
import { BookOpen, ShoppingBag, Store } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

defineProps<{
  id: number
  name: string
  price: string
  stock?: number
  buyLabel: string
  canAdd: boolean
  open: boolean
}>()
const emit = defineEmits<{ add: [] }>()
const { t } = useI18n()

function moveFocus(event: KeyboardEvent) {
  const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[event.key]
  if (!step || event.altKey || event.ctrlKey || event.metaKey) return
  const actions = Array.from(
    (event.currentTarget as HTMLElement).querySelectorAll<HTMLElement>('button:enabled, a[href]'),
  )
  const index = actions.indexOf(event.target as HTMLElement)
  if (index < 0) return
  event.preventDefault()
  actions[(index + step + actions.length) % actions.length]?.focus()
}
</script>

<template>
  <div
    class="offer-commands"
    role="group"
    :aria-label="name"
    :data-open="open"
    :inert="!open"
    @keydown="moveFocus"
  >
    <div v-if="price" class="command-spoke spoke-price">
      <div class="price-tag">
        <small>{{ t('studio.price') }}</small>
        <strong>{{ price }}</strong>
        <span v-if="stock !== undefined">{{ stock ? t('stock', stock) : t('soldOutNow') }}</span>
      </div>
    </div>
    <div v-if="price" class="command-spoke spoke-buy">
      <button class="command-key" :disabled="!canAdd" @click="emit('add')">
        <ShoppingBag aria-hidden="true" /><span>{{ buyLabel }}</span>
      </button>
    </div>
    <div class="command-spoke spoke-shop">
      <RouterLink class="command-key" to="/catalogo"
        ><Store aria-hidden="true" /><span>{{ t('catalog') }}</span></RouterLink
      >
    </div>
    <div class="command-spoke spoke-detail">
      <RouterLink class="command-key" :to="`/pokemon/${id}`"
        ><BookOpen aria-hidden="true" /><span>{{ t('studio.details') }}</span></RouterLink
      >
    </div>
  </div>
</template>

<style scoped>
.offer-commands {
  --command-red: #c51933;
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
}
.offer-commands[data-open='false'] {
  visibility: hidden;
}
.command-spoke {
  position: absolute;
  width: max-content;
  max-width: 34%;
  rotate: var(--tilt);
  transform-origin: var(--pivot) center;
  filter: drop-shadow(3px 5px 0 #100e12);
}
.command-spoke::before {
  content: '';
  position: absolute;
  inset: 14% -6% -18% -3%;
  z-index: -1;
  background: var(--command-red);
  clip-path: polygon(0 0, 100% 8%, 86% 38%, 100% 61%, 5% 100%, 14% 74%, 0 78%);
}
.spoke-price,
.spoke-detail {
  right: 62%;
  --pivot: 100%;
  --slide: 38px;
}
.spoke-buy,
.spoke-shop {
  left: 62%;
  --pivot: 0%;
  --slide: -38px;
}
.spoke-price {
  top: 21%;
  --tilt: 10deg;
  --delay: 0ms;
}
.spoke-buy {
  top: 28%;
  --tilt: -12deg;
  --delay: 75ms;
}
.spoke-shop {
  top: 62%;
  --tilt: 11deg;
  --delay: 140ms;
}
.spoke-detail {
  top: 66%;
  --tilt: -12deg;
  --delay: 205ms;
}
.price-tag,
.command-key {
  position: relative;
  isolation: isolate;
  color: var(--sheet);
}
.price-tag::before,
.command-key::before,
.command-key::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  background: var(--sheet);
  clip-path: polygon(5% 4%, 100% 0, 97% 89%, 0 100%);
}
.price-tag {
  padding: 11px clamp(20px, 3vw, 45px);
  line-height: 1;
  color: var(--ink);
  display: grid;
  justify-items: start;
  gap: 3px;
}
.price-tag small,
.price-tag span {
  font: 750 0.64rem/1.3 var(--font-mono);
}
.price-tag small {
  text-transform: uppercase;
  letter-spacing: 0.18em;
}
.price-tag strong {
  font: 900 clamp(2.1rem, 4.4vw, 4rem) / 0.94 var(--font-display);
  letter-spacing: -0.035em;
}
.command-key {
  pointer-events: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 0;
  background: transparent;
  min-height: 60px;
  padding: 12px clamp(16px, 2.1vw, 30px);
  text-decoration: none;
  font: 900 clamp(1.45rem, 2.85vw, 2.8rem) / 1 var(--font-display);
  text-transform: uppercase;
  transition: transform 120ms ease-out;
}
.command-key::after {
  inset: 3px;
  background: var(--ink);
}
.command-key svg {
  flex: none;
  width: 1em;
  height: 1em;
  padding: 0.15em;
  border-radius: 50%;
  color: var(--ink);
  background: var(--sheet);
  stroke-width: 2.8;
}
.spoke-detail .command-key {
  flex-direction: row-reverse;
}
.spoke-buy .command-key::after {
  background: var(--command-red);
}
.command-key:disabled {
  opacity: 0.8;
}
.command-key:is(:hover, :focus-visible):not(:disabled) {
  color: var(--ink);
  transform: scale(1.065);
}
.command-key:is(:hover, :focus-visible):not(:disabled)::after {
  background: var(--sheet);
}
.command-key:is(:hover, :focus-visible):not(:disabled) svg {
  background: var(--ink);
  color: var(--sheet);
}
.offer-commands[data-open='true'] .command-spoke {
  animation: fan-in 320ms var(--delay) cubic-bezier(0.16, 0.88, 0.22, 1) both;
}
@keyframes fan-in {
  0% {
    opacity: 0;
    transform: translateX(var(--slide)) scaleX(0.25) rotate(calc(-1 * var(--tilt)));
  }
  72% {
    opacity: 1;
    transform: translateX(0) scaleX(1.045);
  }
  100% {
    opacity: 1;
    transform: none;
  }
}
@media (max-width: 650px) {
  .offer-commands {
    position: relative;
    width: min(100%, 440px);
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-areas: 'price buy' 'detail shop';
    align-items: center;
    gap: 12px 10px;
    padding: 4px 5px 8px;
  }
  .command-spoke {
    position: relative;
    inset: auto;
    width: 100%;
    max-width: none;
    --tilt: -2deg;
    --slide: 12px;
  }
  .command-spoke::before {
    inset: 12% -2% -8%;
  }
  .spoke-price {
    grid-area: price;
  }
  .spoke-buy {
    grid-area: buy;
  }
  .spoke-detail {
    grid-area: detail;
  }
  .spoke-shop {
    grid-area: shop;
  }
  .command-key {
    width: 100%;
    min-height: 46px;
    gap: 5px;
    padding: 9px 12px;
    font-size: clamp(1.05rem, 4.6vw, 1.5rem);
  }
  .price-tag {
    padding: 7px 14px;
    gap: 1px;
  }
  .price-tag strong {
    font-size: clamp(1.9rem, 7.2vw, 2.65rem);
  }
  .price-tag small,
  .price-tag span {
    font-size: 0.54rem;
  }
}
@media (prefers-reduced-motion: reduce) {
  .offer-commands .command-spoke,
  .command-key {
    animation: none !important;
    transition: none;
  }
}
</style>
