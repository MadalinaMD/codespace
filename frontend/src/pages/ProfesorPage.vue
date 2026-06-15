<script setup>
// Panoul profesorului: analitica clasei, integritate academică, generator de
// conținut cu aprobare umană și gestiunea băncii de întrebări.
import { onMounted, ref } from 'vue'
import client, { mesajEroare } from '@/api/client'
import { useUi } from '@/stores/ui'

const ui = useUi()
const tab = ref('ansamblu')
const TABURI = [
  ['ansamblu', '📊 Ansamblu'],
  ['heatmap', '🗺️ Heatmap concepte'],
  ['studenti', '👥 Studenți'],
  ['integritate', '🔍 Integritate'],
  ['generator', '🤖 Generator AI'],
  ['intrebari', '❓ Întrebări'],
]

const ansamblu = ref(null)
const heatmap = ref([])
const studenti = ref([])
const erori = ref([])
const exercitii = ref([])
const exercitiuAles = ref(null)
const similaritate = ref(null)
const concepte = ref([])
const schite = ref([])
const intrebari = ref([])
const seGenereaza = ref(false)
const genConcept = ref('')
const genNumar = ref(3)

onMounted(async () => {
  const [a, c] = await Promise.all([
    client.get('/profesor/ansamblu'),
    client.get('/profesor/concepte'),
  ])
  ansamblu.value = a.data
  concepte.value = c.data
  genConcept.value = c.data[0]?.slug || ''
})

async function deschide(numeTab) {
  tab.value = numeTab
  try {
    if (numeTab === 'heatmap' && !heatmap.value.length) {
      heatmap.value = (await client.get('/profesor/heatmap')).data
    } else if (numeTab === 'studenti' && !studenti.value.length) {
      studenti.value = (await client.get('/profesor/studenti')).data
    } else if (numeTab === 'integritate') {
      if (!erori.value.length) erori.value = (await client.get('/profesor/erori')).data
      if (!exercitii.value.length) exercitii.value = (await client.get('/profesor/exercitii')).data
    } else if (numeTab === 'generator') {
      schite.value = (await client.get('/profesor/schite')).data
    } else if (numeTab === 'intrebari' && !intrebari.value.length) {
      intrebari.value = (await client.get('/profesor/intrebari')).data
    }
  } catch (e) {
    ui.toast(mesajEroare(e), 'eroare', '⚠️')
  }
}

async function verificaSimilaritatea() {
  if (!exercitiuAles.value) return
  similaritate.value = null
  similaritate.value = (await client.get(`/profesor/similaritate/${exercitiuAles.value}`)).data
}

async function genereazaIntrebari() {
  seGenereaza.value = true
  try {
    const { data } = await client.post('/profesor/genereaza/intrebari',
      { concept_slug: genConcept.value, numar: genNumar.value })
    ui.toast(data.mesaj, 'info', '🤖')
    schite.value = (await client.get('/profesor/schite')).data
  } catch (e) {
    ui.toast(mesajEroare(e), 'eroare', '⚠️')
  } finally {
    seGenereaza.value = false
  }
}

async function genereazaExercitiu() {
  seGenereaza.value = true
  try {
    const { data } = await client.post('/profesor/genereaza/exercitiu',
      { concept_slug: genConcept.value })
    ui.toast(data.validat ? 'Exercițiu generat și VALIDAT prin execuție.' : 'Generat, dar INVALID — vezi raportul.',
             data.validat ? 'info' : 'eroare', '🤖')
    schite.value = (await client.get('/profesor/schite')).data
  } catch (e) {
    ui.toast(mesajEroare(e), 'eroare', '⚠️')
  } finally {
    seGenereaza.value = false
  }
}

async function decideSchita(schita, decizie) {
  try {
    await client.post(`/profesor/schite/${schita.id}/${decizie}`)
    schite.value = schite.value.filter((s) => s.id !== schita.id)
    ui.toast(decizie === 'aproba' ? 'Adăugat în curs.' : 'Schiță respinsă.', 'info', decizie === 'aproba' ? '✅' : '🗑️')
  } catch (e) {
    ui.toast(mesajEroare(e), 'eroare', '⚠️')
  }
}

async function reseteazaParola(student) {
  if (!confirm(`Resetezi parola pentru ${student.nume}?`)) return
  const { data } = await client.post(`/profesor/studenti/${student.id}/reseteaza-parola`)
  alert(`${data.mesaj}\nParola temporară: ${data.parola_temporara}\n(Comunic-o studentului pe un canal sigur.)`)
}

async function stergeStudent(student) {
  if (!confirm(`Ștergi DEFINITIV contul „${student.nume}” și tot progresul lui?`)) return
  await client.delete(`/profesor/studenti/${student.id}`)
  studenti.value = studenti.value.filter((s) => s.id !== student.id)
}

async function dezactiveazaIntrebarea(intrebare) {
  if (!confirm('Retragi întrebarea din quiz-uri?')) return
  await client.delete(`/profesor/intrebari/${intrebare.id}`)
  intrebari.value = intrebari.value.filter((i) => i.id !== intrebare.id)
}

function culoareHeat(valoare) {
  if (valoare === null) return 'bg-white/5 text-gray-600'
  if (valoare >= 0.8) return 'bg-emerald-500/20 text-emerald-300'
  if (valoare >= 0.6) return 'bg-[#42b883]/15 text-[#42b883]'
  if (valoare >= 0.4) return 'bg-amber-500/15 text-amber-300'
  return 'bg-red-500/15 text-red-300'
}
</script>

<template>
  <div class="max-w-6xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Panoul profesorului</h1>
    <p class="text-gray-400 text-sm mt-1">Analitica clasei, integritatea academică și conținutul cursului.</p>

    <!-- Taburi -->
    <div class="flex flex-wrap gap-1.5 mt-6 p-1 rounded-xl bg-[#0d0d0d] border border-white/5 w-fit">
      <button v-for="[cheie, eticheta] in TABURI" :key="cheie" @click="deschide(cheie)"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              :class="tab === cheie ? 'bg-[#42b883] text-black font-bold' : 'text-gray-400 hover:text-gray-200'">
        {{ eticheta }}
      </button>
    </div>

    <!-- ANSAMBLU -->
    <div v-if="tab === 'ansamblu' && ansamblu" class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-7">
      <div v-for="[eticheta, valoare] in [
             ['Studenți', ansamblu.studenti], ['Lecții', ansamblu.lectii],
             ['Exerciții', ansamblu.exercitii], ['Întrebări active', ansamblu.intrebari],
             ['Submisii', ansamblu.submisii_total], ['Rata de acceptare', ansamblu.procent_acceptare + '%'],
             ['Întrebări generate de AI', ansamblu.intrebari_ai], ['Schițe în așteptare', ansamblu.schite_in_asteptare],
           ]" :key="eticheta"
           class="rounded-2xl border border-white/10 bg-[#101010] p-5">
        <p class="text-2xl font-bold text-white">{{ valoare }}</p>
        <p class="text-xs text-gray-500 mt-1">{{ eticheta }}</p>
      </div>
    </div>

    <!-- HEATMAP -->
    <div v-if="tab === 'heatmap'" class="mt-7 rounded-2xl border border-white/10 bg-[#101010] overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-white/10 bg-[#0d0d0d]">
            <th class="px-5 py-3">Concept</th>
            <th class="px-3 py-3 text-right">Studenți</th>
            <th class="px-3 py-3 text-right">Măiestrie medie</th>
            <th class="px-5 py-3 text-right">Stăpânire</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="concept in heatmap" :key="concept.slug" class="border-b border-white/5 last:border-0">
            <td class="px-5 py-2.5 text-gray-200">{{ concept.nume }}</td>
            <td class="px-3 py-2.5 text-right text-gray-400">{{ concept.studenti }}</td>
            <td class="px-3 py-2.5 text-right">
              <span class="px-2 py-1 rounded-md text-xs font-bold" :class="culoareHeat(concept.medie_p)">
                {{ concept.medie_p === null ? '—' : Math.round(concept.medie_p * 100) + '%' }}
              </span>
            </td>
            <td class="px-5 py-2.5 text-right text-gray-400">
              {{ concept.procent_stapanire === null ? '—' : concept.procent_stapanire + '%' }}
            </td>
          </tr>
        </tbody>
      </table>
      <p class="px-5 py-3 text-[11px] text-gray-600 border-t border-white/10">
        Măiestria medie = media p(cunoaștere) BKT a studenților cu observații pe concept. Roșu = clasa se împotmolește acolo.
      </p>
    </div>

    <!-- STUDENȚI -->
    <div v-if="tab === 'studenti'" class="mt-7 space-y-3">
      <div v-for="student in studenti" :key="student.id"
           class="rounded-2xl border bg-[#101010] p-5"
           :class="student.la_risc ? 'border-red-500/30' : 'border-white/10'">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p class="text-white font-semibold">
              {{ student.nume }}
              <span v-if="student.la_risc" class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-red-500/15 text-red-400 font-bold ml-2">la risc</span>
            </p>
            <p class="text-xs text-gray-500 mt-0.5">{{ student.email }}</p>
            <p v-if="student.motive_risc.length" class="text-xs text-red-400/90 mt-1.5">
              ⚠ {{ student.motive_risc.join(' · ') }}
            </p>
          </div>
          <div class="flex items-center gap-5 text-center">
            <div><p class="text-lg font-bold text-white">{{ student.xp }}</p><p class="text-[10px] text-gray-500">XP</p></div>
            <div><p class="text-lg font-bold text-white">{{ student.exercitii_rezolvate }}</p><p class="text-[10px] text-gray-500">exerciții</p></div>
            <div>
              <p class="text-lg font-bold" :class="student.medie_maiestrie === null ? 'text-gray-600' : student.medie_maiestrie < 0.4 ? 'text-red-400' : 'text-white'">
                {{ student.medie_maiestrie === null ? '—' : Math.round(student.medie_maiestrie * 100) + '%' }}
              </p>
              <p class="text-[10px] text-gray-500">măiestrie</p>
            </div>
            <div><p class="text-sm text-gray-300">{{ student.ultima_activitate || 'niciodată' }}</p><p class="text-[10px] text-gray-500">ultima activitate</p></div>
          </div>
          <div class="flex gap-2">
            <button @click="reseteazaParola(student)"
                    class="text-xs text-gray-400 hover:text-amber-400 border border-white/10 rounded-lg px-3 py-1.5 transition-colors">Resetează parola</button>
            <button @click="stergeStudent(student)"
                    class="text-xs text-gray-400 hover:text-red-400 border border-white/10 rounded-lg px-3 py-1.5 transition-colors">Șterge</button>
          </div>
        </div>
      </div>
      <p v-if="!studenti.length" class="text-gray-500 text-sm">Niciun student înscris încă.</p>
    </div>

    <!-- INTEGRITATE -->
    <div v-if="tab === 'integritate'" class="mt-7 grid md:grid-cols-2 gap-6">
      <div class="rounded-2xl border border-white/10 bg-[#101010] p-6">
        <h3 class="text-white font-semibold mb-1">Erorile frecvente ale clasei</h3>
        <p class="text-xs text-gray-500 mb-4">Misconcepțiile colective — materialul de remediat la curs.</p>
        <div v-if="!erori.length" class="text-sm text-gray-500">Nicio submisie cu erori încă.</div>
        <div v-for="eroare in erori" :key="eroare.categorie" class="mb-3">
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-300">{{ eroare.titlu }}</span>
            <span class="text-gray-500 font-mono text-xs">{{ eroare.numar }}× ({{ eroare.procent }}%)</span>
          </div>
          <div class="h-1.5 rounded-full bg-white/5 overflow-hidden">
            <div class="h-full bg-red-400/70" :style="{ width: eroare.procent + '%' }"></div>
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-white/10 bg-[#101010] p-6">
        <h3 class="text-white font-semibold mb-1">Similaritatea soluțiilor</h3>
        <p class="text-xs text-gray-500 mb-4">Compară structural (AST normalizat) ultimele soluții acceptate — redenumirea variabilelor nu păcălește analiza.</p>
        <div class="flex gap-2">
          <select v-model="exercitiuAles" class="flex-1 bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200">
            <option :value="null" disabled>Alege exercițiul…</option>
            <option v-for="exercitiu in exercitii" :key="exercitiu.id" :value="exercitiu.id">
              {{ exercitiu.titlu }} ({{ exercitiu.lectie }})
            </option>
          </select>
          <button @click="verificaSimilaritatea" :disabled="!exercitiuAles"
                  class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-40 text-black font-bold px-4 rounded-lg text-sm transition-all">Verifică</button>
        </div>
        <div v-if="similaritate" class="mt-4">
          <p class="text-xs text-gray-500 mb-2">{{ similaritate.solutii_comparate }} soluții comparate.</p>
          <div v-if="!similaritate.perechi_suspecte.length" class="text-sm text-emerald-400">✓ Nicio pereche suspectă (prag 90%).</div>
          <div v-for="(pereche, index) in similaritate.perechi_suspecte" :key="index"
               class="rounded-lg border border-red-500/30 bg-red-500/5 px-3 py-2 text-sm text-gray-200 mb-2">
            ⚠ {{ pereche.student_1.nume }} ↔ {{ pereche.student_2.nume }}
            <span class="text-red-400 font-bold float-right">{{ Math.round(pereche.scor * 100) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- GENERATOR -->
    <div v-if="tab === 'generator'" class="mt-7 space-y-6">
      <div class="rounded-2xl border border-white/10 bg-[#101010] p-6">
        <h3 class="text-white font-semibold mb-1">Generează conținut nou</h3>
        <p class="text-xs text-gray-500 mb-4">
          AI-ul propune; exercițiile sunt validate prin EXECUȚIE (soluția generată trebuie să treacă testele generate); tu aprobi. Nimic nu intră în curs fără semnătura ta.
        </p>
        <div class="flex flex-wrap gap-2 items-center">
          <select v-model="genConcept" class="bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200">
            <option v-for="concept in concepte" :key="concept.slug" :value="concept.slug">{{ concept.nume }}</option>
          </select>
          <select v-model.number="genNumar" class="bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200">
            <option v-for="n in [2, 3, 4, 5]" :key="n" :value="n">{{ n }} întrebări</option>
          </select>
          <button @click="genereazaIntrebari" :disabled="seGenereaza"
                  class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold px-4 py-2 rounded-lg text-sm transition-all">
            {{ seGenereaza ? 'Se generează…' : 'Generează întrebări' }}
          </button>
          <button @click="genereazaExercitiu" :disabled="seGenereaza"
                  class="border border-[#42b883]/50 text-[#42b883] hover:bg-[#42b883]/10 disabled:opacity-50 font-bold px-4 py-2 rounded-lg text-sm transition-all">
            {{ seGenereaza ? 'Se generează…' : 'Generează exercițiu' }}
          </button>
        </div>
      </div>

      <div>
        <h3 class="text-white font-semibold mb-3">Schițe în așteptare ({{ schite.length }})</h3>
        <p v-if="!schite.length" class="text-sm text-gray-500">Nimic de aprobat.</p>
        <div v-for="schita in schite" :key="schita.id"
             class="rounded-2xl border bg-[#101010] p-5 mb-3"
             :class="schita.validat ? 'border-white/10' : 'border-red-500/30'">
          <div class="flex items-center gap-2 text-xs mb-3">
            <span class="px-2 py-0.5 rounded-full bg-white/5 text-gray-400 uppercase tracking-wider font-bold">{{ schita.tip }}</span>
            <span class="text-gray-500">concept: {{ schita.concept_slug }}</span>
            <span class="px-2 py-0.5 rounded-full font-bold"
                  :class="schita.validat ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/15 text-red-400'">
              {{ schita.validat ? '✓ validat' : '✗ invalid' }}
            </span>
          </div>

          <template v-if="schita.tip === 'intrebare'">
            <p class="text-sm text-white">{{ schita.payload.text }}</p>
            <p class="text-xs text-emerald-400 mt-2">✓ {{ schita.payload.corecta }}</p>
            <p v-for="gresita in schita.payload.gresite" :key="gresita" class="text-xs text-gray-500 mt-0.5">✗ {{ gresita }}</p>
          </template>
          <template v-else>
            <p class="text-sm text-white font-semibold">{{ schita.payload.titlu }}</p>
            <p class="text-xs text-gray-400 mt-1 line-clamp-2">{{ schita.payload.enunt_md }}</p>
            <p class="text-xs text-gray-500 mt-2 font-mono">{{ (schita.payload.teste || []).length }} teste generate</p>
          </template>
          <p class="text-[11px] mt-2" :class="schita.validat ? 'text-gray-600' : 'text-red-400/80'">{{ schita.raport_validare }}</p>

          <div class="flex gap-2 mt-4">
            <button @click="decideSchita(schita, 'aproba')" :disabled="!schita.validat && schita.tip === 'exercitiu'"
                    class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-30 text-black font-bold px-4 py-1.5 rounded-lg text-xs transition-all">Aprobă</button>
            <button @click="decideSchita(schita, 'respinge')"
                    class="border border-white/15 text-gray-400 hover:text-red-400 hover:border-red-500/40 font-bold px-4 py-1.5 rounded-lg text-xs transition-all">Respinge</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ÎNTREBĂRI -->
    <div v-if="tab === 'intrebari'" class="mt-7 rounded-2xl border border-white/10 bg-[#101010] overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-white/10 bg-[#0d0d0d]">
            <th class="px-5 py-3">Întrebare</th>
            <th class="px-3 py-3">Capitol</th>
            <th class="px-3 py-3">Sursă</th>
            <th class="px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="intrebare in intrebari" :key="intrebare.id" class="border-b border-white/5 last:border-0">
            <td class="px-5 py-2.5 text-gray-200 max-w-md truncate" :title="intrebare.text">{{ intrebare.text }}</td>
            <td class="px-3 py-2.5 text-gray-500 text-xs">{{ intrebare.capitol }}</td>
            <td class="px-3 py-2.5">
              <span class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold"
                    :class="intrebare.sursa === 'ai' ? 'bg-purple-500/15 text-purple-300' : 'bg-white/5 text-gray-400'">
                {{ intrebare.sursa }}
              </span>
            </td>
            <td class="px-5 py-2.5 text-right">
              <button @click="dezactiveazaIntrebarea(intrebare)"
                      class="text-xs text-gray-500 hover:text-red-400 transition-colors">Retrage</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
