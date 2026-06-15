<script setup>
// Recapitularea SM-2: întrebările scadente azi, reprogramate după răspuns.
import { onMounted, ref } from 'vue'
import client from '@/api/client'
import { useUi } from '@/stores/ui'
import McqRunner from '@/components/McqRunner.vue'

const ui = useUi()
const coada = ref(null)
const intrebari = ref([])
const sesiuneGata = ref(null)
const seIncarca = ref(true)

onMounted(incarca)

async function incarca() {
  seIncarca.value = true
  sesiuneGata.value = null
  try {
    const { data } = await client.get('/recapitulare')
    coada.value = data
    intrebari.value = data.carduri.map((card) => ({
      cheie: card.card_id,
      text: card.text,
      variante: card.variante,
      meta: `${card.capitol} · repetarea ${card.repetari + 1}`,
    }))
  } finally {
    seIncarca.value = false
  }
}

async function raspunde(intrebare, raspuns) {
  const { data } = await client.post(`/recapitulare/${intrebare.cheie}/raspunde`, {
    intrebare_id: intrebare.cheie, raspuns,
  })
  ui.anuntaRezultate(data)
  const cand = data.interval_zile === 1 ? 'mâine' : `în ${data.interval_zile} zile`
  return {
    ...data,
    detaliu: data.invatat
      ? '🌟 Card stăpânit — iese din coada activă.'
      : `Programat din nou ${cand} (SM-2).`,
  }
}

function terminat({ scor, total }) {
  sesiuneGata.value = { scor, total }
}

function formateazaData(text) {
  if (!text) return ''
  return new Date(text).toLocaleString('ro-RO', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Recapitulare</h1>
    <p class="text-gray-400 text-sm mt-1 mb-7">
      Repetiție spațiată (SM-2): întrebările revin exact când creierul e pe punctul să le uite.
    </p>

    <div v-if="seIncarca" class="text-gray-500 text-sm">Se încarcă coada…</div>

    <!-- Sesiune încheiată -->
    <div v-else-if="sesiuneGata" class="rounded-2xl border border-white/10 bg-[#101010] p-8 text-center">
      <p class="text-5xl mb-3">🧠</p>
      <h2 class="text-xl font-bold text-white">Sesiune încheiată: {{ sesiuneGata.scor }}/{{ sesiuneGata.total }}</h2>
      <p class="text-gray-400 text-sm mt-2">Cardurile au fost reprogramate după performanța ta.</p>
      <button @click="incarca" class="mt-6 bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-5 py-2.5 rounded-xl text-sm transition-all">
        Mai sunt scadente?
      </button>
    </div>

    <!-- Nimic scadent -->
    <div v-else-if="!intrebari.length" class="rounded-2xl border border-white/10 bg-[#101010] p-8 text-center">
      <p class="text-5xl mb-3">✅</p>
      <h2 class="text-xl font-bold text-white">Nimic scadent acum</h2>
      <p class="text-gray-400 text-sm mt-2" v-if="coada?.total_in_invatare">
        Ai {{ coada.total_in_invatare }} carduri în învățare.
        <template v-if="coada.urmatoarea_scadenta"> Următoarea recapitulare: {{ formateazaData(coada.urmatoarea_scadenta) }}.</template>
      </p>
      <p class="text-gray-400 text-sm mt-2" v-else>
        Greșelile de la quiz-uri devin automat carduri de recapitulare — deocamdată nu ai niciunul. Bravo!
      </p>
    </div>

    <template v-else>
      <p class="text-xs text-gray-500 mb-4">{{ coada.total_scadente }} scadente azi · {{ coada.total_in_invatare }} în învățare</p>
      <McqRunner :intrebari="intrebari" :raspunde="raspunde" @terminat="terminat" />
    </template>
  </div>
</template>
