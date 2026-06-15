<script setup>
// Testul de plasament: calibrarea inițială a modelului de cunoștințe.
// 10 întrebări răspândite pe tot cursul → sistemul află de unde să înceapă cu tine.
import { ref } from 'vue'
import client, { mesajEroare } from '@/api/client'
import { confetti } from '@/lib/confetti'
import McqRunner from '@/components/McqRunner.vue'

const test = ref(null)
const intrebari = ref([])
const rezultat = ref(null)
const eroare = ref('')
const sePorneste = ref(false)

async function incepe() {
  sePorneste.value = true
  eroare.value = ''
  try {
    const { data } = await client.post('/test-adaptiv/plasament/incepe')
    test.value = data
    intrebari.value = data.intrebari.map((i) => ({ cheie: i.index, text: i.text, variante: i.variante }))
  } catch (e) {
    eroare.value = mesajEroare(e)
  } finally {
    sePorneste.value = false
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
  confetti(90)
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Calibrare inițială</h1>
    <p class="text-gray-400 text-sm mt-1 mb-7">
      Ca să nu te plictisești cu lucruri pe care le știi — și să nu te arunce în adânc nepregătit.
    </p>

    <!-- Intro -->
    <div v-if="!test && !rezultat" class="rounded-2xl border border-white/10 bg-[#101010] p-8">
      <p class="text-5xl text-center mb-4">🧭</p>
      <h2 class="text-lg font-semibold text-white text-center">10 întrebări, ~5 minute</h2>
      <div class="text-sm text-gray-400 mt-4 space-y-2 max-w-lg mx-auto">
        <p>• Întrebările acoperă <span class="text-gray-200">tot cursul</span>, de la print() la clase — e normal să nu le știi pe toate.</p>
        <p>• Fiecare răspuns calibrează modelul tău de cunoștințe (BKT); un răspuns corect dă credit și <span class="text-gray-200">fundamentelor</span> conceptului.</p>
        <p>• La final primești <span class="text-gray-200">punctul de start personalizat</span> — lecțiile pe care le poți sări cu încredere.</p>
        <p>• Nu se acordă XP: e o radiografie, nu un concurs. Răspunde sincer, fără să ghicești.</p>
      </div>
      <p v-if="eroare" class="text-sm text-red-400 text-center mt-4">{{ eroare }}</p>
      <div class="text-center mt-6">
        <button @click="incepe" :disabled="sePorneste"
                class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold px-6 py-2.5 rounded-xl text-sm transition-all">
          {{ sePorneste ? 'Se pregătește…' : 'Începe calibrarea' }}
        </button>
      </div>
    </div>

    <!-- Rezultatul -->
    <div v-else-if="rezultat" class="rounded-2xl border border-white/10 bg-[#101010] p-8">
      <div class="text-center">
        <p class="text-5xl mb-3">🎯</p>
        <h2 class="text-xl font-bold text-white">Calibrare încheiată: {{ rezultat.scor }}/{{ rezultat.total }}</h2>
      </div>

      <div v-if="rezultat.start?.lectie_slug" class="mt-6 rounded-xl border border-[#42b883]/30 bg-[#42b883]/5 p-5 text-center">
        <p class="text-xs text-[#42b883] font-bold uppercase tracking-wider">Punctul tău de start</p>
        <p class="text-white font-semibold mt-1.5">{{ rezultat.start.titlu }}</p>
        <p v-if="rezultat.start.lectii_sarite > 0" class="text-sm text-gray-400 mt-1">
          Poți sări cu încredere peste primele {{ rezultat.start.lectii_sarite }} lecții — modelul arată că le stăpânești.
        </p>
        <p v-else class="text-sm text-gray-400 mt-1">Începem cu fundamentele — cel mai solid mod de a construi.</p>
      </div>

      <div v-if="rezultat.pe_concepte?.length" class="mt-5 space-y-2">
        <p class="text-xs text-gray-500 uppercase tracking-wider font-bold">Radiografia pe concepte</p>
        <div v-for="concept in rezultat.pe_concepte" :key="concept.concept"
             class="flex items-center justify-between rounded-xl border border-white/10 px-4 py-2.5">
          <span class="text-sm text-gray-200">{{ concept.concept }}</span>
          <span class="text-sm font-mono"
                :class="concept.corecte === concept.total ? 'text-emerald-400' : concept.corecte === 0 ? 'text-red-400' : 'text-amber-400'">
            {{ concept.corecte }}/{{ concept.total }}
          </span>
        </div>
      </div>

      <div class="flex justify-center gap-3 mt-7 flex-wrap">
        <router-link v-if="rezultat.start?.lectie_slug" :to="`/lectii/${rezultat.start.lectie_slug}`"
                     class="bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-5 py-2.5 rounded-xl text-sm transition-all">
          Începe de la „{{ rezultat.start.titlu }}” →
        </router-link>
        <router-link to="/profil"
                     class="border border-white/15 text-gray-300 hover:bg-white/5 font-semibold px-5 py-2.5 rounded-xl text-sm transition-all">
          Vezi harta măiestriei
        </router-link>
      </div>
    </div>

    <!-- Testul -->
    <McqRunner v-else :intrebari="intrebari" :raspunde="raspunde" @terminat="finalizeaza" />
  </div>
</template>
