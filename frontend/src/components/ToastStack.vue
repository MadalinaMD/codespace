<script setup>
import { useUi } from '@/stores/ui'

const ui = useUi()
const CULORI = {
  xp: 'border-[#42b883]/40 bg-[#10221a]',
  realizare: 'border-amber-500/40 bg-[#221d10]',
  eroare: 'border-red-500/40 bg-[#221010]',
  info: 'border-white/15 bg-[#161616]',
}
</script>

<template>
  <div class="fixed bottom-5 right-5 z-50 space-y-2 w-80">
    <TransitionGroup name="toast">
      <div v-for="toast in ui.toasturi" :key="toast.id"
           class="rounded-xl border px-4 py-3 shadow-2xl flex items-center gap-3 backdrop-blur"
           :class="CULORI[toast.tip] || CULORI.info">
        <span v-if="toast.icon" class="text-xl">{{ toast.icon }}</span>
        <p class="text-sm text-gray-100 flex-1">{{ toast.mesaj }}</p>
        <button @click="ui.inchide(toast.id)" class="text-gray-500 hover:text-gray-300">✕</button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active { transition: all 0.25s ease; }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: translateY(10px); }
</style>
