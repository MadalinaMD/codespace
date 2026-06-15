<script setup>
// Exercițiul notat: editor + teste instant în browser (Pyodide) + verdict
// oficial pe server + indicii progresive care nu dau soluția.
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import client, { mesajEroare } from '@/api/client'
import { ruleazaTesteLocal } from '@/lib/harness'
import { confetti } from '@/lib/confetti'
import { useUi } from '@/stores/ui'
import MarkdownView from '@/components/MarkdownView.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import TestResults from '@/components/TestResults.vue'
import StepVisualizer from '@/components/StepVisualizer.vue'

const route = useRoute()
const ui = useUi()

const exercitiu = ref(null)
const cod = ref('')
const rezultatLocal = ref(null)
const rezultatOficial = ref(null)
const seRuleaza = ref(false)
const seTrimite = ref(false)
const statusPyodide = ref('')
const indicii = ref([])
const nivelUrmator = ref(1)
const seCereIndiciu = ref(false)
const eroareIndiciu = ref('')
const arataVizualizator = ref(false)
const vizualizare = ref({ cod: '', stdin: '' })
const arataSolutia = ref(false)

const rezolvat = computed(() =>
  exercitiu.value?.rezolvat || rezultatOficial.value?.status === 'acceptat')

function depaneaza() {
  // Vizualizăm execuția pe PRIMUL test picat (sau pe primul test, dacă n-ai rulat încă)
  const rezultate = (rezultatOficial.value || rezultatLocal.value)?.rezultate || []
  let indexTest = rezultate.findIndex((r) => !r.trecut)
  if (indexTest === -1) indexTest = 0
  const test = exercitiu.value.teste[indexTest] || exercitiu.value.teste[0]
  if (exercitiu.value.mod === 'functie' && test?.apel) {
    vizualizare.value = {
      cod: cod.value.replace(/\n+$/, '') + `\n\n# Apelul testului vizualizat:\nrezultat = ${test.apel}`,
      stdin: '',
    }
  } else {
    vizualizare.value = { cod: cod.value, stdin: test?.stdin || '' }
  }
  arataVizualizator.value = true
}

onMounted(async () => {
  const { data } = await client.get(`/exercitii/${route.params.id}`)
  exercitiu.value = data
  cod.value = data.ultimul_cod || data.cod_start
  indicii.value = data.indicii_primite
  nivelUrmator.value = data.nivel_indiciu_urmator
})

async function ruleazaLocal() {
  if (seRuleaza.value) return
  seRuleaza.value = true
  rezultatLocal.value = null
  statusPyodide.value = 'Se pregătește Python în browser (prima rulare ~10s)…'
  try {
    rezultatLocal.value = await ruleazaTesteLocal(cod.value, exercitiu.value.teste, exercitiu.value.mod)
  } catch (e) {
    ui.toast(String(e?.message || e), 'eroare', '⚠️')
  } finally {
    seRuleaza.value = false
    statusPyodide.value = ''
  }
}

async function trimite() {
  if (seTrimite.value) return
  seTrimite.value = true
  try {
    const { data } = await client.post(`/exercitii/${exercitiu.value.id}/trimite`, { cod: cod.value })
    rezultatOficial.value = data
    rezultatLocal.value = null
    ui.anuntaRezultate(data)
    if (data.prima_rezolvare) confetti()
    if (data.status === 'acceptat' && !data.prima_rezolvare) {
      ui.toast('Soluție acceptată din nou — bravo!', 'info', '✅')
    }
    if (data.status === 'acceptat' && !exercitiu.value.solutie_referinta) {
      // Soluția de referință devine vizibilă abia după rezolvare — o reîncărcăm
      const { data: detalii } = await client.get(`/exercitii/${exercitiu.value.id}`)
      exercitiu.value = { ...exercitiu.value, solutie_referinta: detalii.solutie_referinta }
    }
  } catch (e) {
    ui.toast(mesajEroare(e), 'eroare', '⚠️')
  } finally {
    seTrimite.value = false
  }
}

async function cereIndiciu() {
  if (seCereIndiciu.value || nivelUrmator.value > 3) return
  seCereIndiciu.value = true
  eroareIndiciu.value = ''
  try {
    const { data } = await client.post(`/exercitii/${exercitiu.value.id}/indiciu`, {
      cod: cod.value, nivel: nivelUrmator.value,
    })
    indicii.value = [...indicii.value.filter((i) => i.nivel !== data.nivel),
                     { nivel: data.nivel, continut: data.continut }]
    nivelUrmator.value = Math.min(data.nivel + 1, 3 + 1)
  } catch (e) {
    eroareIndiciu.value = mesajEroare(e)
  } finally {
    seCereIndiciu.value = false
  }
}

function reseteaza() {
  cod.value = exercitiu.value.cod_start
  rezultatLocal.value = null
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-8 py-10" v-if="exercitiu">
    <!-- Antet -->
    <router-link :to="`/lectii/${exercitiu.lectie.slug}`" class="text-xs text-gray-500 hover:text-gray-300 transition-colors">
      ← Înapoi la lecția „{{ exercitiu.lectie.titlu }}”
    </router-link>
    <div class="flex items-center gap-3 mt-2">
      <h1 class="text-2xl font-bold text-white">{{ exercitiu.titlu }}</h1>
      <span class="text-xs text-gray-600">{{ '★'.repeat(exercitiu.dificultate) }}</span>
      <span v-if="rezolvat" class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 font-bold">rezolvat</span>
    </div>
    <p class="text-xs text-gray-600 mt-1">Concepte antrenate: {{ exercitiu.concepte.join(' · ') }}</p>

    <!-- Enunțul -->
    <div class="mt-6 rounded-2xl border border-white/10 bg-[#101010] p-6">
      <MarkdownView :continut="exercitiu.enunt_md" />
    </div>

    <!-- Editorul -->
    <div class="mt-6" @keydown.ctrl.enter.exact.prevent="ruleazaLocal" @keydown.ctrl.shift.enter.prevent="trimite">
      <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
        <h2 class="text-sm font-semibold text-gray-300 uppercase tracking-wider">Soluția ta</h2>
        <div class="flex items-center gap-2 flex-wrap">
          <button @click="reseteaza" class="text-xs text-gray-500 hover:text-gray-300 px-3 py-2 transition-colors">↺ Resetează</button>
          <button @click="depaneaza"
                  class="border border-amber-500/40 text-amber-400 hover:bg-amber-500/10 font-bold px-4 py-2 rounded-lg text-sm transition-all"
                  title="Urmărește execuția pe primul test picat, linie cu linie">
            🔬 Depanează
          </button>
          <button @click="ruleazaLocal" :disabled="seRuleaza || seTrimite" title="Ctrl+Enter"
                  class="border border-[#42b883]/50 text-[#42b883] hover:bg-[#42b883]/10 disabled:opacity-50 font-bold px-4 py-2 rounded-lg text-sm transition-all">
            {{ seRuleaza ? 'Rulează…' : '▶ Testează local' }}
          </button>
          <button @click="trimite" :disabled="seTrimite || seRuleaza" title="Ctrl+Shift+Enter"
                  class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold px-4 py-2 rounded-lg text-sm transition-all">
            {{ seTrimite ? 'Se evaluează…' : '📤 Trimite oficial' }}
          </button>
        </div>
      </div>
      <CodeEditor v-model="cod" />
      <p v-if="statusPyodide" class="text-xs text-amber-400/80 mt-2">⏳ {{ statusPyodide }}</p>
      <p class="text-[11px] text-gray-600 mt-2">
        „Testează local” (Ctrl+Enter) rulează instant în browserul tău. „Trimite oficial” (Ctrl+Shift+Enter) evaluează pe server — doar verdictul lui contează pentru progres și XP.
      </p>
    </div>

    <!-- Vizualizatorul de depanare -->
    <div v-if="arataVizualizator" class="mt-5">
      <StepVisualizer :cod="vizualizare.cod" :stdin="vizualizare.stdin"
                      @inchide="arataVizualizator = false" />
    </div>

    <!-- Rezultate -->
    <div class="mt-5 space-y-4">
      <TestResults v-if="rezultatOficial" :rezultat="rezultatOficial" :oficial="true" />
      <TestResults v-else-if="rezultatLocal" :rezultat="rezultatLocal" />
    </div>

    <!-- Soluția de referință (doar după rezolvare) -->
    <div v-if="exercitiu.solutie_referinta" class="mt-5 rounded-2xl border border-emerald-500/25 bg-emerald-500/5 overflow-hidden">
      <button @click="arataSolutia = !arataSolutia"
              class="w-full flex items-center justify-between px-5 py-3.5 text-left">
        <span class="text-sm font-semibold text-emerald-300">
          {{ arataSolutia ? '▾' : '▸' }} Soluția de referință — compar-o cu a ta
        </span>
        <span class="text-[10px] uppercase tracking-wider text-emerald-400/70 font-bold">deblocată prin rezolvare</span>
      </button>
      <div v-if="arataSolutia" class="px-5 pb-5">
        <MarkdownView :continut="'```python\n' + exercitiu.solutie_referinta + '\n```'" />
        <p class="text-xs text-gray-500 mt-2">
          Nu există o singură soluție corectă — dacă a ta trece testele altfel, e la fel de validă.
          Întreabă tutorele dacă vrei să înțelegi diferențele.
        </p>
      </div>
    </div>

    <!-- Indicii progresive -->
    <div class="mt-8 rounded-2xl border border-white/10 bg-[#101010] p-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-white font-semibold">Indicii progresive</h2>
          <p class="text-xs text-gray-500 mt-1">
            Trei niveluri, de la orientare la pseudocod — niciodată soluția. Fiecare nivel folosit scade XP-ul exercițiului cu 10 (minim 15).
          </p>
        </div>
        <button v-if="nivelUrmator <= 3 && !rezolvat" @click="cereIndiciu" :disabled="seCereIndiciu"
                class="shrink-0 border border-amber-500/40 text-amber-400 hover:bg-amber-500/10 disabled:opacity-50 font-bold px-4 py-2 rounded-lg text-sm transition-all">
          {{ seCereIndiciu ? 'Se generează…' : `💡 Indiciu (nivel ${nivelUrmator})` }}
        </button>
      </div>
      <p v-if="eroareIndiciu" class="text-sm text-red-400 mt-3">{{ eroareIndiciu }}</p>
      <div v-if="indicii.length" class="mt-4 space-y-3">
        <div v-for="indiciu in indicii" :key="indiciu.nivel"
             class="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
          <p class="text-[10px] uppercase tracking-wider text-amber-400 font-bold mb-1.5">Nivel {{ indiciu.nivel }}</p>
          <p class="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">{{ indiciu.continut }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
