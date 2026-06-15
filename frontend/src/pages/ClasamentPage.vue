<script setup>
// Clasamentul: doar nume și performanță — fără date personale.
import { onMounted, ref } from 'vue'
import client from '@/api/client'

const intrari = ref([])
const seIncarca = ref(true)

onMounted(async () => {
  try {
    const { data } = await client.get('/clasament')
    intrari.value = data
  } finally {
    seIncarca.value = false
  }
})

const MEDALII = { 1: '🥇', 2: '🥈', 3: '🥉' }
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Clasament</h1>
    <p class="text-gray-400 text-sm mt-1 mb-7">XP-ul vine doar din rezultate — exerciții rezolvate, quiz-uri, recapitulări.</p>

    <div v-if="seIncarca" class="text-gray-500 text-sm">Se încarcă…</div>
    <div v-else-if="!intrari.length" class="text-gray-500 text-sm rounded-xl border border-white/10 p-5">
      Încă nimeni în clasament — fii primul care rezolvă un exercițiu!
    </div>

    <div v-else class="rounded-2xl border border-white/10 bg-[#101010] overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-white/10 bg-[#0d0d0d]">
            <th class="px-5 py-3 w-14">#</th>
            <th class="px-3 py-3">Student</th>
            <th class="px-3 py-3 text-right">Nivel</th>
            <th class="px-3 py-3 text-right">Exerciții</th>
            <th class="px-3 py-3 text-right">Concepte stăpânite</th>
            <th class="px-5 py-3 text-right">XP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="intrare in intrari" :key="intrare.rank"
              class="border-b border-white/5 last:border-0"
              :class="intrare.esti_tu ? 'bg-[#42b883]/10' : ''">
            <td class="px-5 py-3 font-mono text-gray-400">{{ MEDALII[intrare.rank] || intrare.rank }}</td>
            <td class="px-3 py-3 text-white font-medium">
              {{ intrare.nume }}
              <span v-if="intrare.esti_tu" class="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-[#42b883]/20 text-[#42b883] font-bold ml-2">tu</span>
            </td>
            <td class="px-3 py-3 text-right text-gray-300">{{ intrare.nivel }}</td>
            <td class="px-3 py-3 text-right text-gray-300">{{ intrare.exercitii_rezolvate }}</td>
            <td class="px-3 py-3 text-right text-gray-300">{{ intrare.concepte_stapanite }}</td>
            <td class="px-5 py-3 text-right font-bold text-[#42b883]">{{ intrare.xp }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
