<script setup>
// Lecția: teorie în Markdown, exemplu rulabil în browser, exerciții, navigare.
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'
import { ruleazaCod } from '@/lib/pyodide'
import { useUi } from '@/stores/ui'
import MarkdownView from '@/components/MarkdownView.vue'
import CodeEditor from '@/components/CodeEditor.vue'
import StepVisualizer from '@/components/StepVisualizer.vue'

const route = useRoute()
const router = useRouter()
const ui = useUi()

const lectie = ref(null)
const seIncarca = ref(true)
const codExemplu = ref('')
const iesire = ref(null)
const seRuleaza = ref(false)
const statusPyodide = ref('')
const arataVizualizator = ref(false)
const codDeVizualizat = ref('')

function vizualizeaza() {
  codDeVizualizat.value = codExemplu.value
  arataVizualizator.value = true
}

async function incarca(slug) {
  seIncarca.value = true
  iesire.value = null
  try {
    const { data } = await client.get(`/lectii/${slug}`)
    lectie.value = data
    codExemplu.value = data.cod_exemplu || '# Această lecție nu are exemplu de cod.'
    // Marcăm vizita fără să blocăm afișarea
    client.post(`/lectii/${slug}/vizita`).then(({ data: vizita }) => {
      ui.anuntaRezultate(vizita)
    }).catch(() => {})
  } finally {
    seIncarca.value = false
  }
}

onMounted(() => incarca(route.params.slug))
watch(() => route.params.slug, (slug) => slug && incarca(slug))

async function ruleaza() {
  if (seRuleaza.value) return
  seRuleaza.value = true
  iesire.value = null
  statusPyodide.value = 'Se pregătește Python (prima rulare durează ~10s)…'
  try {
    iesire.value = await ruleazaCod(codExemplu.value)
  } catch (e) {
    iesire.value = { ok: false, iesire: String(e?.message || e) }
  } finally {
    seRuleaza.value = false
    statusPyodide.value = ''
  }
}

function procentCuloare(p) {
  if (p >= 0.95) return 'bg-emerald-500'
  if (p >= 0.6) return 'bg-[#42b883]'
  if (p > 0.2) return 'bg-amber-500'
  return 'bg-gray-600'
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-8 py-10">
    <div v-if="seIncarca" class="text-gray-500 text-sm">Se încarcă lecția…</div>

    <template v-else-if="lectie">
      <!-- Antet -->
      <p class="text-xs text-gray-500 uppercase tracking-wider">{{ lectie.capitol.titlu }}</p>
      <h1 class="text-2xl font-bold text-white mt-1">{{ lectie.titlu }}</h1>

      <!-- Conceptele lecției + stăpânirea curentă -->
      <div class="flex flex-wrap gap-2 mt-4">
        <div v-for="concept in lectie.concepte" :key="concept.slug"
             class="flex items-center gap-2 rounded-full border border-white/10 bg-[#101010] pl-3 pr-2 py-1"
             :title="`Stăpânire estimată: ${Math.round(concept.p * 100)}%`">
          <span class="text-xs text-gray-300">{{ concept.nume }}</span>
          <span class="w-12 h-1.5 rounded-full bg-white/10 overflow-hidden">
            <span class="block h-full rounded-full" :class="procentCuloare(concept.p)"
                  :style="{ width: Math.round(concept.p * 100) + '%' }"></span>
          </span>
        </div>
      </div>

      <!-- Teoria -->
      <div class="mt-8">
        <MarkdownView :continut="lectie.continut_md" />
      </div>

      <!-- Exemplul rulabil -->
      <div class="mt-9" @keydown.ctrl.enter.prevent="ruleaza">
        <div class="flex items-center justify-between mb-3 flex-wrap gap-2">
          <h2 class="text-lg font-semibold text-white">💡 Exemplu — rulează-l și modifică-l</h2>
          <div class="flex gap-2">
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
        <CodeEditor v-model="codExemplu" />
        <p v-if="statusPyodide" class="text-xs text-amber-400/80 mt-2">⏳ {{ statusPyodide }}</p>
        <div v-if="iesire" class="mt-3 rounded-xl border border-white/10 bg-[#0c0c0c] p-4">
          <p class="text-[10px] uppercase tracking-wider font-bold mb-2"
             :class="iesire.ok ? 'text-[#42b883]' : 'text-red-400'">
            {{ iesire.ok ? '› Rezultat' : '✗ Eroare' }}
          </p>
          <pre class="text-sm font-mono whitespace-pre-wrap leading-relaxed"
               :class="iesire.ok ? 'text-gray-200' : 'text-red-300'">{{ iesire.iesire || '(programul nu a afișat nimic)' }}</pre>
        </div>
        <div v-if="arataVizualizator" class="mt-3">
          <StepVisualizer :cod="codDeVizualizat" @inchide="arataVizualizator = false" />
        </div>
      </div>

      <!-- Exercițiile lecției -->
      <div v-if="lectie.exercitii.length" class="mt-9">
        <h2 class="text-lg font-semibold text-white mb-3">🎯 Exerciții notate</h2>
        <div class="space-y-2.5">
          <router-link v-for="exercitiu in lectie.exercitii" :key="exercitiu.id"
                       :to="`/exercitii/${exercitiu.id}`"
                       class="flex items-center justify-between rounded-xl border border-white/10 bg-[#101010] hover:border-[#42b883]/40 px-5 py-3.5 transition-all group">
            <div class="flex items-center gap-3">
              <span :class="exercitiu.rezolvat ? 'text-emerald-400' : 'text-gray-600'">
                {{ exercitiu.rezolvat ? '✓' : '○' }}
              </span>
              <span class="text-sm text-gray-200">{{ exercitiu.titlu }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs text-gray-600">{{ '★'.repeat(exercitiu.dificultate) }}</span>
              <span class="text-gray-600 group-hover:text-[#42b883] transition-colors">→</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Întreabă tutorele -->
      <router-link :to="{ path: '/tutore', query: { lectie: lectie.slug } }"
                   class="mt-7 flex items-center gap-3 rounded-xl border border-white/10 bg-[#101010] hover:border-[#42b883]/40 px-5 py-3.5 transition-all text-sm text-gray-300">
        💬 Ai o nelămurire? Întreabă tutorele AI despre lecția asta →
      </router-link>

      <!-- Sursa bibliografică -->
      <p v-if="lectie.sursa" class="text-[11px] text-gray-600 mt-7 italic">📚 {{ lectie.sursa }}</p>

      <!-- Navigare -->
      <div class="flex justify-between mt-9 pt-6 border-t border-white/10">
        <button v-if="lectie.anterioara" @click="router.push(`/lectii/${lectie.anterioara.slug}`)"
                class="text-sm text-gray-400 hover:text-white transition-colors">
          ← {{ lectie.anterioara.titlu }}
        </button>
        <span v-else></span>
        <button v-if="lectie.urmatoarea" @click="router.push(`/lectii/${lectie.urmatoarea.slug}`)"
                class="text-sm text-[#42b883] hover:text-[#5fd0a0] transition-colors font-medium">
          {{ lectie.urmatoarea.titlu }} →
        </button>
      </div>
    </template>
  </div>
</template>
