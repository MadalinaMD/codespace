<script setup>
// Testul adaptiv: generat pe conceptele slabe ale studentului, notat pe server.
import { ref } from 'vue'
import client, { mesajEroare } from '@/api/client'
import { useUi } from '@/stores/ui'
import McqRunner from '@/components/McqRunner.vue'

const ui = useUi()
const test = ref(null)
const intrebari = ref([])
const rezultat = ref(null)
const eroare = ref('')
const seGenereaza = ref(false)

async function genereaza() {
  seGenereaza.value = true
  eroare.value = ''
  rezultat.value = null
  try {
    const { data } = await client.post('/test-adaptiv/genereaza')
    test.value = data
    intrebari.value = data.intrebari.map((i) => ({ cheie: i.index, text: i.text, variante: i.variante }))
  } catch (e) {
    eroare.value = mesajEroare(e)
  } finally {
    seGenereaza.value = false
  }
}

async function raspunde(intrebare, raspuns) {
  const { data } = await client.post(`/test-adaptiv/${test.value.test_id}/raspunde`, {
    index: intrebare.cheie, raspuns,
  })
  return data
}

async function finalizeaza() {
  const { data } = await client.post(`/test-adaptiv/${test.value.test_id}/finalizeaza`)
  rezultat.value = data
  ui.anuntaRezultate(data)
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Test adaptiv</h1>
    <p class="text-gray-400 text-sm mt-1 mb-7">
      Sistemul îți alege întrebările pe baza modelului tău de cunoștințe: exact conceptele unde ai cel mai mult de câștigat.
    </p>

    <!-- Start -->
    <div v-if="!test && !rezultat" class="rounded-2xl border border-white/10 bg-[#101010] p-8 text-center">
      <p class="text-5xl mb-3">🎯</p>
      <h2 class="text-lg font-semibold text-white">Pregătit pentru o verificare țintită?</h2>
      <p class="text-gray-400 text-sm mt-2 max-w-md mx-auto">
        Întrebările sunt generate de AI pe conceptele tale slabe (sau alese din banca de întrebări, dacă AI-ul nu e disponibil) și notate pe server.
      </p>
      <p v-if="eroare" class="text-sm text-red-400 mt-4">{{ eroare }}</p>
      <button @click="genereaza" :disabled="seGenereaza"
              class="mt-6 bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold px-6 py-2.5 rounded-xl text-sm transition-all">
        {{ seGenereaza ? 'Se generează testul…' : 'Generează testul' }}
      </button>
    </div>

    <!-- Rezultat -->
    <div v-else-if="rezultat" class="rounded-2xl border border-white/10 bg-[#101010] p-8">
      <div class="text-center">
        <p class="text-5xl mb-3">{{ rezultat.scor >= rezultat.total * 0.8 ? '🏆' : '📈' }}</p>
        <h2 class="text-xl font-bold text-white">{{ rezultat.scor }} din {{ rezultat.total }} corecte</h2>
        <p v-if="rezultat.xp_castigat" class="text-[#42b883] font-semibold mt-2">+{{ rezultat.xp_castigat }} XP</p>
      </div>
      <div v-if="rezultat.pe_concepte?.length" class="mt-6 space-y-2">
        <p class="text-xs text-gray-500 uppercase tracking-wider font-bold">Defalcat pe concepte</p>
        <div v-for="concept in rezultat.pe_concepte" :key="concept.concept"
             class="flex items-center justify-between rounded-xl border border-white/10 px-4 py-2.5">
          <span class="text-sm text-gray-200">{{ concept.concept }}</span>
          <span class="text-sm font-mono"
                :class="concept.corecte === concept.total ? 'text-emerald-400' : concept.corecte === 0 ? 'text-red-400' : 'text-amber-400'">
            {{ concept.corecte }}/{{ concept.total }}
          </span>
        </div>
      </div>
      <div class="flex justify-center gap-3 mt-7">
        <button @click="test = null; rezultat = null"
                class="border border-white/15 text-gray-300 hover:bg-white/5 font-semibold px-5 py-2.5 rounded-xl text-sm transition-all">
          Alt test
        </button>
        <router-link to="/profil" class="bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-5 py-2.5 rounded-xl text-sm transition-all">
          Vezi harta măiestriei
        </router-link>
      </div>
    </div>

    <!-- Testul în desfășurare -->
    <template v-else>
      <p class="text-xs text-gray-500 mb-4">Concepte vizate: {{ test.concepte_vizate.join(' · ') }}</p>
      <McqRunner :intrebari="intrebari" :raspunde="raspunde" @terminat="finalizeaza" />
    </template>
  </div>
</template>
