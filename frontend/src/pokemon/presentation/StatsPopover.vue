<script setup lang="ts">
import { nextTick, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { PopoverRoot, PopoverAnchor, PopoverPortal, PopoverContent } from 'reka-ui'
import { ChartNoAxesColumnIncreasing, X } from 'lucide-vue-next'
defineProps<{ stats?: Record<string, number> }>()
const { t } = useI18n(),
  open = ref(false),
  pinned = ref(false),
  trigger = ref<HTMLButtonElement>()
let timer: ReturnType<typeof setTimeout> | undefined,
  suppressed = false,
  hovering = false
const fine = () => window.matchMedia('(hover: hover) and (pointer: fine)').matches
function enter() {
  hovering = true
  clearTimeout(timer)
  if (fine() && !suppressed) open.value = true
}
function blur() { suppressed=false; schedule() }
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
      !document.activeElement?.closest('.stats-popover')
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
  <PopoverRoot :open="open" @update:open="!$event && close()"
    ><PopoverAnchor as-child
      ><button
        ref="trigger"
        class="button secondary stats-trigger"
        :aria-expanded="open"
        aria-haspopup="dialog"
        @mouseenter="enter"
        @mouseleave="leave"
        @focus="focus"
        @blur="blur"
        @click="click"
      >
        <ChartNoAxesColumnIncreasing :size="18" />{{ t('viewStats') }}
      </button></PopoverAnchor
    ><PopoverPortal
      ><PopoverContent
        class="stats-popover"
        :side-offset="12"
        :collision-padding="16"
        :aria-label="t('baseStats')"
        @open-auto-focus.prevent
        @close-auto-focus.prevent
        @escape-key-down.prevent="close(true)"
        @pointer-down-outside="close()"
        @focus-outside="close()"
        @mouseenter="enter"
        @mouseleave="leave"
        @focusout="schedule"
      >
        <div class="stats-popover-heading">
          <h2>{{ t('baseStats') }}</h2>
          <button class="icon-button" :aria-label="t('close')" @click="close(true)">
            <X :size="18" />
          </button>
        </div>
        <div
          v-for="key in ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']"
          :key="key"
          class="stat"
        >
          <div>
            <span>{{ t(key) }}</span
            ><strong>{{ stats?.[key] ?? t('missingData') }}</strong>
          </div>
          <meter
            v-if="stats?.[key] != null"
            min="0"
            max="255"
            :value="stats[key]"
            :aria-label="t(key)"
          >
            {{ stats[key] }} / 255
          </meter>
        </div>
      </PopoverContent></PopoverPortal
    ></PopoverRoot
  >
</template>
<style>
.stats-trigger {
  margin-top: 18px;
}
.stats-popover {
  z-index: 120;
  width: min(360px, calc(100vw - 32px));
  background: var(--surface);
  color: var(--ink);
  padding: 20px 24px;
  border: 1px solid var(--line);
  border-radius: 20px;
  box-shadow: 0 18px 60px #0003;
}
.stats-popover-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 16px;
}
.stats-popover-heading h2 {
  font-size: 1.1rem;
  margin: 0;
}
.stats-popover .stat {
  margin: 14px 0;
}
</style>
