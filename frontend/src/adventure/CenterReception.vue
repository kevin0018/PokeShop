<script setup lang="ts">
defineProps<{ selected: number }>()
</script>

<template>
  <div class="center-reception" aria-hidden="true">
    <div class="reception-window reception-window-left">
      <span class="reception-heart">♥</span>
    </div>
    <div class="reception-window reception-window-right">
      <span
        v-for="i in 6"
        :key="i"
        class="reception-light"
        :class="{ active: i <= selected }"
      ></span>
    </div>
    <svg class="center-nurse" viewBox="0 0 80 112" shape-rendering="crispEdges" focusable="false">
      <path fill="#aa4769" d="M18 30H62V66H18Z" />
      <path fill="#e78ba3" d="M14 28H26V52H14ZM54 28H66V52H54Z" />
      <path fill="#f0a1b6" d="M24 18H56V38H24Z" />
      <path fill="#f7d0b8" d="M26 32H54V57H26Z" />
      <path fill="#3d3049" d="M31 40H35V44H31ZM45 40H49V44H45Z" />
      <path fill="#bd6c79" d="M37 50H43V52H37Z" />
      <path fill="#fff3e9" d="M22 18V8H58V18Z" />
      <path fill="#e78ba3" d="M36 9H44V16H36Z" />
      <path fill="#d66b88" d="M24 60H56L65 94H15Z" />
      <path fill="#f7d0b8" d="M15 70H23V89H15ZM57 70H65V89H57Z" />
      <path fill="#fff3e9" d="M29 60H51V88H29Z" />
      <path fill="#f0a1b6" d="M36 58H44V63H36Z" />
      <path fill="#8b5f78" d="M24 94H35V109H24ZM45 94H56V109H45Z" />
    </svg>
    <div class="reception-counter"><span class="counter-emblem pokeball"></span></div>
  </div>
</template>
