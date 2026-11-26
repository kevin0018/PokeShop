<script setup lang="ts">
import { Monitor } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
defineProps<{ arriving: boolean }>()
const emit = defineEmits<{ openPc: []; arrived: [] }>()
const { t } = useI18n()
</script>
<template>
  <div class="lobby">
    <header>
      <span>{{ t('adventure.viridianCity') }}</span>
      <h2>{{ t('adventure.pokemonCenter') }}</h2>
    </header>
    <div class="lobby-map">
      <img src="/studio/viridian-lobby.png" width="240" height="160" alt="" />
      <span
        aria-hidden="true"
        class="lobby-player"
        :class="{ arriving }"
        @animationend.self="emit('arrived')"
        ><i></i
      ></span>
      <button type="button" class="pc-access" aria-haspopup="dialog" @click="emit('openPc')">
        <Monitor :size="16" />{{ t('adventure.openPc') }}
      </button>
    </div>
  </div>
</template>
<style scoped>
.lobby {
  min-width: 0;
  align-self: start;
  background: #26263b;
  border: 3px solid #292638;
  border-radius: 6px;
  overflow: hidden;
}
.lobby header {
  padding: 13px 18px;
  border-bottom: 3px solid #cd775f;
  background: #2b293c;
  color: #fff0ce;
}
.lobby header span {
  font: 700 0.7rem/1.4 var(--font-mono);
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: #ffc48b;
}
.lobby header h2 {
  margin: 3px 0 0;
  font: 750 clamp(1.35rem, 2.3vw, 2.2rem) / 1.1 var(--font-mono);
}
.lobby-map {
  position: relative;
  isolation: isolate;
  background: #201e2e;
}
.lobby-map img {
  width: 100%;
  height: auto;
  display: block;
  image-rendering: pixelated;
}
.lobby-player {
  position: absolute;
  left: 50%;
  top: 57%;
  width: 6.667%;
  aspect-ratio: 1/2;
  transform: translate(-50%, -92%);
}
.lobby-player i {
  display: block;
  width: 100%;
  height: 100%;
  background: url('/studio/trainer-walk.png') 50% 0/300% 100%;
  image-rendering: pixelated;
}
.lobby .pc-access {
  right: 4%;
  top: 33%;
  bottom: auto;
  min-height: 44px;
  height: auto;
  width: auto;
  padding: 5px 9px;
  gap: 6px;
  color: #fcf3dc;
  background: #27283e;
  border: 2px solid #ffe0a4;
  border-radius: 4px;
  font: 700 0.78rem/1.25 var(--font-mono);
  box-shadow: 2px 2px 0 #292234;
}
.lobby .pc-access:hover {
  background: #443752;
}
@media (prefers-reduced-motion: no-preference) {
  .lobby-player.arriving {
    animation: lobby-arrive 1s linear both;
  }
  .arriving i {
    animation: arrival-steps 0.34s steps(3) 3;
  }
  @keyframes lobby-arrive {
    0% {
      top: 93%;
      opacity: 0;
    }
    15% {
      opacity: 1;
    }
    100% {
      top: 57%;
    }
  }
}
</style>
