<script setup>
// Profilul studentului: nivel + XP, streak, calendar, harta măiestriei, realizări.
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'
import { useAuth } from '@/stores/auth'
import MasteryMap from '@/components/MasteryMap.vue'

const router = useRouter()
const auth = useAuth()
const profil = ref(null)
const harta = ref(null)
const statistici = ref(null)
const istoricXp = ref([])

onMounted(async () => {
  const [p, h, s, x] = await Promise.all([
    client.get('/gamificare/profil'),
    client.get('/progres/harta'),
    client.get('/progres/statistici'),
    client.get('/gamificare/istoric-xp'),
  ])
  profil.value = p.data
  harta.value = h.data
  statistici.value = s.data
  istoricXp.value = x.data
})

function deschideLectia(concept) {
  if (concept.lectie_slug) router.push(`/lectii/${concept.lectie_slug}`)
}

function dataScurta(text) {
  return new Date(text).toLocaleDateString('ro-RO', { day: 'numeric', month: 'short' })
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-8 py-10" v-if="profil">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-bold text-white">{{ auth.nume }}</h1>
        <p class="text-gray-400 text-sm mt-1">Modelul tău de cunoștințe, la zi.</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-3xl">🔥</span>
        <div>
          <p class="text-xl font-bold text-white leading-none">{{ profil.streak }} zile</p>
          <p class="text-xs text-gray-500 mt-1">seria curentă</p>
        </div>
      </div>
    </div>

    <!-- Nivel + XP -->
    <div class="mt-6 rounded-2xl border border-white/10 bg-[#101010] p-6">
      <div class="flex items-center justify-between mb-3">
        <p class="text-white font-semibold">Nivel {{ profil.nivel }}</p>
        <p class="text-xs text-gray-500">{{ profil.xp_in_nivel }} / {{ profil.xp_necesar_nivel }} XP până la nivelul {{ profil.nivel + 1 }}</p>
      </div>
      <div class="h-2.5 rounded-full bg-white/5 overflow-hidden">
        <div class="h-full bg-gradient-to-r from-[#42b883] to-emerald-400 transition-all duration-500"
             :style="{ width: profil.progres_nivel + '%' }"></div>
      </div>
      <p class="text-xs text-gray-600 mt-2">
        {{ profil.xp_total }} XP în total — câștigat exclusiv din rezultate: exerciții, quiz-uri, recapitulări.
      </p>
    </div>

    <!-- Calendarul activității -->
    <div v-if="statistici" class="mt-6 rounded-2xl border border-white/10 bg-[#101010] p-6">
      <p class="text-white font-semibold mb-3">Ultimele 30 de zile</p>
      <div class="flex gap-1.5 flex-wrap">
        <div v-for="zi in statistici.calendar" :key="zi.zi"
             class="w-5 h-5 rounded"
             :class="zi.activ ? 'bg-[#42b883]' : 'bg-white/5'"
             :title="`${zi.zi}: ${zi.activ ? 'activ' : 'fără activitate'}`"></div>
      </div>
    </div>

    <!-- Harta măiestriei -->
    <div class="mt-8">
      <h2 class="text-lg font-semibold text-white mb-1">Harta măiestriei</h2>
      <p class="text-sm text-gray-500 mb-4">
        Graful conceptelor cursului, cu săgețile de la fundament spre avansat.
        {{ harta?.stapanite || 0 }} din {{ harta?.total || 0 }} concepte stăpânite.
      </p>
      <MasteryMap v-if="harta" :concepte="harta.concepte" @selecteaza="deschideLectia" />
    </div>

    <!-- Realizări -->
    <div class="mt-8">
      <h2 class="text-lg font-semibold text-white mb-4">
        Realizări <span class="text-sm text-gray-500 font-normal">({{ profil.realizari_deblocate }}/{{ profil.realizari_total }})</span>
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div v-for="realizare in profil.realizari" :key="realizare.cod"
             class="rounded-xl border p-4 transition-all"
             :class="realizare.deblocata
               ? 'border-amber-500/30 bg-amber-500/5'
               : 'border-white/5 bg-[#0d0d0d] opacity-45 grayscale'">
          <p class="text-2xl">{{ realizare.icon }}</p>
          <p class="text-sm font-semibold text-white mt-1.5">{{ realizare.titlu }}</p>
          <p class="text-xs text-gray-500 mt-0.5">{{ realizare.descriere }}</p>
        </div>
      </div>
    </div>

    <!-- Istoricul XP -->
    <div v-if="istoricXp.length" class="mt-8">
      <h2 class="text-lg font-semibold text-white mb-4">Istoricul XP</h2>
      <div class="rounded-2xl border border-white/10 bg-[#101010] divide-y divide-white/5">
        <div v-for="(eveniment, index) in istoricXp" :key="index"
             class="flex items-center justify-between px-5 py-2.5">
          <span class="text-sm text-gray-300 truncate mr-4">{{ eveniment.descriere }}</span>
          <span class="shrink-0 text-xs text-gray-500">{{ dataScurta(eveniment.creat_la) }}
            <span class="text-[#42b883] font-bold ml-2">+{{ eveniment.puncte }}</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
