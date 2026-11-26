<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const props = defineProps<{ arriving: boolean }>()
const emit = defineEmits<{ openPc: []; arrived: [] }>()
const { t } = useI18n()
const player = ref<HTMLElement>()
const position = ref<'counter' | 'walking' | 'pc'>('counter')
const pending = ref(false)

async function openPc() {
  const actor = player.value
  if (!actor || pending.value) return
  if (position.value === 'pc') {
    emit('openPc')
    return
  }
  pending.value = true
  try {
    if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      actor.closest('.lobby-map')?.scrollIntoView({ block: 'nearest', behavior: 'instant' })
      // Finish entering from the lobby door before turning towards the PC.
      await Promise.allSettled(actor.getAnimations().map((animation) => animation.finished))
      if (!actor.isConnected) return
      position.value = 'walking'
      await nextTick()
      await Promise.allSettled(actor.getAnimations().map((animation) => animation.finished))
    }
    if (!actor.isConnected) return
    if (props.arriving) emit('arrived')
    position.value = 'pc'
    emit('openPc')
  } finally {
    pending.value = false
  }
}
defineExpose({ openPc })
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
        ref="player"
        aria-hidden="true"
        class="lobby-player"
        :class="{ arriving: arriving && position === 'counter' }"
        :data-position="position"
        @animationend.self="arriving && emit('arrived')"
        ><i></i
      ></span>
      <button
        type="button"
        class="pc-access"
        aria-haspopup="dialog"
        :aria-disabled="pending"
        @click="openPc"
      >
        <span>{{ t('adventure.openPc') }}</span>
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
.lobby-player[data-position='pc'],
.lobby-player[data-position='walking'] {
  left: 76.67%;
  top: 32%;
}
.lobby .pc-access {
  /* The terminal is the tile immediately to the right of the reception desk. */
  left: 76.67%;
  top: 18%;
  right: auto;
  bottom: auto;
  transform: translate(-50%, -50%);
  width: 9%;
  height: 21%;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 2px solid #fff2a9;
  border-radius: 4px;
  background: transparent;
  box-shadow: 0 0 0 1px #503c45;
  touch-action: manipulation;
}
.lobby .pc-access span {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 3px 7px;
  white-space: nowrap;
  background: #302d40;
  color: #ffefc3;
  font: 700 0.7rem/1.4 var(--font-mono);
  border-radius: 3px;
}
.lobby .pc-access:hover,
.lobby .pc-access:focus-visible {
  background: #fff2a929;
}
@media (prefers-reduced-motion: no-preference) {
  .lobby-player[data-position='walking'] {
    animation: walk-to-pc 1.24s linear both;
  }
  .lobby-player[data-position='walking'] i {
    background-image: url('/studio/trainer-pc-walk.png');
    background-size: 300% 200%;
    animation:
      pc-stride 0.32s steps(3) infinite,
      pc-turn 1.24s step-end both;
  }
  @keyframes walk-to-pc {
    0% {
      left: 50%;
      top: 57%;
    }
    62% {
      left: 76.67%;
      top: 57%;
    }
    100% {
      left: 76.67%;
      top: 32%;
    }
  }
  @keyframes pc-stride {
    from {
      background-position-x: 0%;
    }
    to {
      background-position-x: 150%;
    }
  }
  @keyframes pc-turn {
    0% {
      background-position-y: 0%;
    }
    62%,
    100% {
      background-position-y: 100%;
    }
  }
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
