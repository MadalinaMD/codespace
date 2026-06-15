<script setup>
// Playground liber: scrie și rulează orice cod Python, direct în browser.
import { ref } from 'vue'
import CodeEditor from '@/components/CodeEditor.vue'
import StepVisualizer from '@/components/StepVisualizer.vue'
import { ruleazaCod } from '@/lib/pyodide'

const COD_INITIAL = `# Playground Python — codul rulează în browserul tău (Pyodide/WebAssembly)
# Încearcă orice: nu poate strica nimic.

for i in range(1, 6):
    print("pătratul lui", i, "este", i ** 2)
`

const cod = ref(COD_INITIAL)
const iesire = ref(null)
const seRuleaza = ref(false)
const status = ref('')
const arataVizualizator = ref(false)
const codDeVizualizat = ref('')

function vizualizeaza() {
  codDeVizualizat.value = cod.value
  arataVizualizator.value = true
}

async function ruleaza() {
  if (seRuleaza.value) return
  seRuleaza.value = true
  status.value = 'Se pregătește Python (prima rulare ~10s)…'
  iesire.value = null
  try {
    iesire.value = await ruleazaCod(cod.value)
  } catch (e) {
    iesire.value = { ok: false, iesire: String(e?.message || e) }
  } finally {
    seRuleaza.value = false
    status.value = ''
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-8 py-10" @keydown.ctrl.enter.prevent="ruleaza">
    <div class="flex items-center justify-between flex-wrap gap-2">
      <div>
        <h1 class="text-2xl font-bold text-white">Playground</h1>
        <p class="text-gray-400 text-sm mt-1">Laboratorul tău liber — experimentează fără consecințe.</p>
      </div>
      <div class="flex gap-2">
        <button @click="cod = COD_INITIAL; iesire = null"
                class="text-xs text-gray-500 hover:text-gray-300 px-3 py-2 transition-colors">↺ Resetează</button>
        <button @click="vizualizeaza"
                class="border border-[#42b883]/50 text-[#42b883] hover:bg-[#42b883]/10 font-bold px-4 py-2 rounded-lg text-sm transition-all"
                title="Vezi execuția linie cu linie, cu variabilele în timp real">
          🔬 Pas cu pas
        </button>
        <button @click="ruleaza" :disabled="seRuleaza" title="Ctrl+Enter"
                class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold px-5 py-2 rounded-lg text-sm transition-all">
          {{ seRuleaza ? 'Rulează…' : '▶ Rulează' }}
        </button>
      </div>
    </div>

    <div class="mt-5">
      <CodeEditor v-model="cod" />
    </div>
    <p v-if="status" class="text-xs text-amber-400/80 mt-2">⏳ {{ status }}</p>

    <div v-if="arataVizualizator" class="mt-4">
      <StepVisualizer :cod="codDeVizualizat" @inchide="arataVizualizator = false" />
    </div>

    <div v-if="iesire" class="mt-4 rounded-xl border border-white/10 bg-[#0c0c0c] p-4">
      <p class="text-[10px] uppercase tracking-wider font-bold mb-2"
         :class="iesire.ok ? 'text-[#42b883]' : 'text-red-400'">
        {{ iesire.ok ? '› Rezultat' : '✗ Eroare' }}
      </p>
      <pre class="text-sm font-mono whitespace-pre-wrap leading-relaxed"
           :class="iesire.ok ? 'text-gray-200' : 'text-red-300'">{{ iesire.iesire || '(programul nu a afișat nimic)' }}</pre>
    </div>
  </div>
</template>
