<script setup>
// Quizul unui capitol — întrebările vin fără răspunsul corect; serverul notează.
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import client, { mesajEroare } from '@/api/client'
import { confetti } from '@/lib/confetti'
import { useUi } from '@/stores/ui'
import McqRunner from '@/components/McqRunner.vue'

const route = useRoute()
const ui = useUi()

const tentativaId = ref(null)
const capitol = ref('')
const intrebari = ref([])
const eroare = ref('')
const rezultat = ref(null)
const seIncarca = ref(true)

onMounted(incepe)

async function incepe() {
  seIncarca.value = true
  eroare.value = ''
  rezultat.value = null
  try {
    const { data } = await client.post(`/quiz/incepe/${route.params.capitolSlug}`)
    tentativaId.value = data.tentativa_id
    capitol.value = data.capitol
    intrebari.value = data.intrebari.map((i) => ({ cheie: i.id, text: i.text, variante: i.variante }))
  } catch (e) {
    eroare.value = mesajEroare(e)
  } finally {
    seIncarca.value = false
  }
}

async function raspunde(intrebare, raspuns) {
  const { data } = await client.post(`/quiz/${tentativaId.value}/raspunde`, {
    intrebare_id: intrebare.cheie, raspuns,
  })
  return data
}

async function finalizeaza({ scor, total }) {
  const { data } = await client.post(`/quiz/${tentativaId.value}/finalizeaza`)
  rezultat.value = data
  ui.anuntaRezultate(data)
  if (data.total > 0 && data.scor === data.total) confetti()
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Quiz: {{ capitol }}</h1>
    <p class="text-gray-400 text-sm mt-1 mb-7">Răspunsurile greșite intră automat în coada de recapitulare.</p>

    <div v-if="seIncarca" class="text-gray-500 text-sm">Se pregătește quiz-ul…</div>
    <p v-else-if="eroare" class="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3">{{ eroare }}</p>

    <!-- Rezumat final -->
    <div v-else-if="rezultat" class="rounded-2xl border border-white/10 bg-[#101010] p-8 text-center">
      <p class="text-5xl mb-3">{{ rezultat.scor === rezultat.total ? '💯' : rezultat.scor >= rezultat.total / 2 ? '🎉' : '💪' }}</p>
      <h2 class="text-xl font-bold text-white">{{ rezultat.scor }} din {{ rezultat.total }} corecte</h2>
      <p v-if="rezultat.xp_castigat" class="text-[#42b883] font-semibold mt-2">+{{ rezultat.xp_castigat }} XP</p>
      <p v-else-if="!rezultat.prima_tentativa" class="text-gray-500 text-sm mt-2">
        XP-ul se acordă doar la prima tentativă a capitolului — dar modelul tău de cunoștințe s-a actualizat.
      </p>
      <div class="flex justify-center gap-3 mt-6">
        <button @click="incepe" class="border border-white/15 text-gray-300 hover:bg-white/5 font-semibold px-5 py-2.5 rounded-xl text-sm transition-all">
          Încearcă din nou
        </button>
        <router-link to="/curs" class="bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-5 py-2.5 rounded-xl text-sm transition-all">
          Înapoi la curs
        </router-link>
      </div>
    </div>

    <McqRunner v-else-if="intrebari.length" :intrebari="intrebari" :raspunde="raspunde" @terminat="finalizeaza" />
  </div>
</template>
