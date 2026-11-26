<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

type Motion = 'strike' | 'flight' | 'fall' | 'beam' | 'bolt' | 'pulse' | 'drain' | 'whip'
type Effect = [
  tile: number,
  motion: Motion,
  count: number,
  size: number,
  arc: number,
  color: string,
]
// Tiles run left to right in the local 32px effect atlas.
const effects: Record<string, Effect> = {
  tackle: [0, 'strike', 1, 30, 0, '#fff3ad'],
  'quick-attack': [1, 'flight', 3, 20, 0, '#fff5ca'],
  bite: [2, 'strike', 1, 36, 0, '#ffca73'],
  swift: [3, 'flight', 4, 15, 11, '#ffe85a'],
  'vine-whip': [4, 'whip', 2, 25, 0, '#85ce40'],
  'razor-leaf': [5, 'flight', 5, 15, 17, '#93ce54'],
  'mega-drain': [6, 'drain', 6, 10, 9, '#b4ec65'],
  ember: [7, 'flight', 3, 13, 8, '#ffae38'],
  flamethrower: [8, 'beam', 10, 22, 5, '#ff7028'],
  scratch: [9, 'strike', 3, 21, 6, '#ffe894'],
  'water-gun': [10, 'beam', 7, 12, 4, '#44baf4'],
  'bubble-beam': [11, 'flight', 8, 14, 8, '#95e3ff'],
  'thunder-shock': [12, 'bolt', 2, 16, 5, '#ffd44a'],
  thunderbolt: [13, 'bolt', 4, 27, 12, '#fff15a'],
  confusion: [14, 'pulse', 3, 19, 0, '#ee8ddc'],
  psybeam: [15, 'beam', 7, 15, 6, '#ce74ff'],
  'karate-chop': [16, 'strike', 1, 32, 12, '#ffa268'],
  'low-kick': [17, 'strike', 1, 27, -12, '#ed9861'],
  'rock-throw': [18, 'flight', 1, 26, 28, '#bb9761'],
  'rock-slide': [19, 'fall', 6, 24, 16, '#d1a475'],
  'mud-slap': [20, 'flight', 5, 14, 13, '#ad8053'],
  sludge: [21, 'flight', 4, 15, 8, '#bd68d7'],
  'sludge-bomb': [22, 'flight', 1, 32, 27, '#aa49b9'],
  psychic: [23, 'pulse', 5, 34, 0, '#ed86b7'],
  strength: [24, 'strike', 1, 42, 0, '#ffd681'],
  'ancient-power': [25, 'fall', 3, 23, -24, '#d5ae84'],
  slam: [26, 'strike', 1, 38, 19, '#fff1bc'],
  acid: [27, 'beam', 6, 9, 13, '#afd649'],
  lick: [28, 'strike', 1, 36, 4, '#ec8e99'],
  'shadow-ball': [29, 'flight', 1, 32, 6, '#8362ba'],
  gust: [30, 'flight', 2, 24, 6, '#c3dbe2'],
  'wing-attack': [31, 'flight', 2, 29, 12, '#d6ece6'],
  'dragon-breath': [32, 'beam', 9, 17, 7, '#a664de'],
  'ice-beam': [33, 'beam', 8, 14, 0, '#92efff'],
  struggle: [34, 'strike', 3, 18, 7, '#ffd4a3'],
}
const canvas = ref<HTMLCanvasElement>()
let atlas: HTMLImageElement
let finish: (() => void) | undefined
onMounted(() => {
  atlas = new Image()
  atlas.src = '/studio/gyms/move-effects.png'
})
onUnmounted(() => finish?.())

function play(move: string, opponent: boolean, hit: boolean) {
  finish?.()
  const surface = canvas.value
  const ctx = surface?.getContext('2d')
  if (!surface || !ctx) return
  const [tile, motion, count, size, arc, color] = effects[move] ?? effects.tackle!
  const endX = hit ? 176 : 197
  const endY = hit ? 35 : 16
  function stamp(x: number, y: number, scale: number, index = tile) {
    const width = Math.max(1, Math.round(scale))
    if (atlas.complete && atlas.naturalWidth) {
      ctx!.drawImage(
        atlas,
        index * 32,
        0,
        32,
        32,
        Math.round(x - width / 2),
        Math.round(y - width / 2),
        width,
        width,
      )
    } else {
      ctx!.fillStyle = color
      ctx!.fillRect(x - width / 4, y - width / 4, width / 2, width / 2)
    }
  }
  function render(progress: number) {
    if (!ctx) return
    ctx.clearRect(0, 0, 240, 112)
    ctx.save()
    ctx.imageSmoothingEnabled = false
    if (opponent) {
      ctx.translate(235, 112)
      ctx.scale(-1, -1)
    }
    const wave = Math.sin(progress * Math.PI)
    if (motion === 'whip') {
      for (let strand = 0; strand < count; strand++) {
        const t = Math.min(1, Math.max(0, (progress - strand * 0.14) * 1.55))
        const reach = Math.sin(t * Math.PI)
        const x = 58 + (endX - 58) * reach
        const y = 76 + (endY - 76) * reach
        for (const [stroke, width] of [
          ['#254e2d', 4],
          [color, 2],
        ] as const) {
          ctx.strokeStyle = stroke
          ctx.lineWidth = width
          ctx.beginPath()
          ctx.moveTo(58, 76)
          ctx.bezierCurveTo(
            82,
            76 + (strand ? 26 : -33) * reach,
            x - 18,
            y + (strand ? -32 : 31) * reach,
            x,
            y,
          )
          ctx.stroke()
        }
        if (hit && reach > 0.94) stamp(x, y, 16, 0)
      }
    } else if (motion === 'bolt') {
      ctx.lineWidth = 2
      ctx.strokeStyle = color
      for (let k = 0; k < count; k++) {
        ctx.beginPath()
        ctx.moveTo(58, 76)
        for (let j = 1; j <= 10; j++) {
          const t = j / 10
          const jag = j === 10 ? 0 : Math.sin(j * 9 + k * 7 + Math.floor(progress * 9)) * arc
          ctx.lineTo(58 + (endX - 58) * t, 76 + (endY - 76) * t + jag)
        }
        if (progress > 0.15 && progress < 0.85) ctx.stroke()
      }
      stamp(endX, endY, size * wave)
    } else {
      for (let i = 0; i < count; i++) {
        const t = progress * (count === 1 ? 1 : 1.5) - (count === 1 ? 0 : (i / (count - 1)) * 0.5)
        if (t < 0 || t > 1) continue
        const swing = Math.sin(t * Math.PI)
        let travel = t
        if (motion === 'drain') travel = 1 - t
        let x = 58 + (endX - 58) * travel
        let y = 76 + (endY - 76) * travel - swing * arc
        let scale = size
        if (motion === 'flight' || motion === 'drain') y += Math.sin(i * 2.4) * swing * 8
        if (motion === 'beam') {
          y += Math.sin(i * 2 + t * 12) * arc * swing
          ctx.strokeStyle = color
          ctx.lineWidth = 2
          ctx.beginPath()
          ctx.moveTo(x - 14, y + 5)
          ctx.lineTo(x, y)
          ctx.stroke()
        }
        if (motion === 'strike') {
          x = endX + Math.sin(i * 4) * 8 - (1 - t) * 11
          y = endY - arc * (1 - t)
          scale *= swing
        }
        if (motion === 'fall') {
          x = endX + Math.cos(i * 4) * 16
          y = endY - (1 - t) * arc * 3
          scale *= 0.65 + t * 0.35
        }
        if (motion === 'pulse') {
          x = endX
          y = endY
          scale *= 0.3 + t * 1.5
          ctx.globalAlpha = 1 - t
        }
        stamp(x, y, scale)
        ctx.globalAlpha = 1
      }
    }
    ctx.restore()
  }
  surface.dataset.move = move
  return new Promise<void>((resolve) => {
    let frame = 0
    const start = performance.now()
    const duration = motion === 'whip' ? 850 : 700
    const end = () => {
      cancelAnimationFrame(frame)
      window.clearTimeout(timer)
      ctx.clearRect(0, 0, 240, 112)
      delete surface.dataset.move
      finish = undefined
      resolve()
    }
    const timer = window.setTimeout(end, duration + 100)
    finish = end
    function tick(now: number) {
      const progress = Math.min(1, (now - start) / duration)
      render(progress)
      if (progress < 1) frame = requestAnimationFrame(tick)
      else end()
    }
    frame = requestAnimationFrame(tick)
  })
}
defineExpose({ play })
</script>

<template>
  <canvas ref="canvas" width="240" height="112" class="move-effect" aria-hidden="true" />
</template>

<style scoped>
.move-effect {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  image-rendering: pixelated;
  z-index: 2;
}
</style>
