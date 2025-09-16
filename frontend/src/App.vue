<script setup lang="ts">
import { RouterView } from 'vue-router'
import BaseHeader from './components/BaseHeader.vue'
import BaseFooter from './components/BaseFooter.vue'
</script>

<template>
  <div style="min-height: 100vh; display: flex; flex-direction: column;">
    <BaseHeader />
    <main style="flex: 1;">
      <RouterView />
    </main>
    <BaseFooter />
  </div>
</template>
