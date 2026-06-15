<script setup>
// Vizualizatorul de execuție pas-cu-pas: linia activă, variabilele în timp
// real, adâncimea apelurilor și output-ul care crește — filmul programului.
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { traseazaCod, MAX_PASI } from '@/lib/tracer'

const props = defineProps({
  cod: { type: String, required: true },
  stdin: { type: String, default: '' },
})
const emit = defineEmits(['inchide'])

const raport = ref(null)
const index = ref(0)
const sePregateste = ref(true)
const eroareIncarcare = ref('')
const intrare = ref(props.stdin)
const arataIntrare = ref(false)
let cronometru = null
const ruleazaAuto = ref(false)

const pasi = computed(() => raport.value?.pasi || [])
const pas = computed(() => pasi.value[index.value] || null)
const liniiCod = computed(() => props.cod.replace(/\n$/, '').split('\n'))
const stdoutVizibil = computed(() => {
  if (!raport.value) return ''
  if (!pas.value) return raport.value.stdout
  return raport.value.stdout.slice(0, pas.value.stdout_len)
})

const ETICHETE_EVENIMENT = {
  line: ['execută linia', 'bg-[#42b883]/15 text-[#42b883]'],
  return: ['return din funcție', 'bg-blue-500/15 text-blue-300'],
  exception: ['excepție!', 'bg-red-500/15 text-red-300'],
}

async function traseaza() {
  oprireAuto()
  sePregateste.value = true
  eroareIncarcare.value = ''
  raport.value = null
  index.value = 0
  try {
    raport.value = await traseazaCod(props.cod, intrare.value)
    // Dacă programul cere input() și nu am dat date, deschidem caseta de intrare
    if (raport.value.eroare?.includes('EOFError')) arataIntrare.value = true
  } catch (e) {
    eroareIncarcare.value = String(e?.message || e)
  } finally {
    sePregateste.value = false
  }
}

watch(() => props.cod, traseaza, { immediate: true })

function laPasul(nou) {
  index.value = Math.min(Math.max(nou, 0), pasi.value.length - 1)
}

function comutaAuto() {
  if (ruleazaAuto.value) return oprireAuto()
  ruleazaAuto.value = true
  cronometru = setInterval(() => {
    if (index.value >= pasi.value.length - 1) return oprireAuto()
    index.value++
  }, 650)
}

function oprireAuto() {
  ruleazaAuto.value = false
  if (cronometru) { clearInterval(cronometru); cronometru = null }
}

onBeforeUnmount(oprireAuto)
</script>

<template>
  <div class="rounded-2xl border border-[#42b883]/25 bg-[#0c0c0c] overflow-hidden">
    <!-- Antet + controale -->
    <div class="flex items-center justify-between gap-3 px-4 py-2.5 border-b border-white/10 bg-[#0f0f0f] flex-wrap">
      <p class="text-sm font-semibold text-white">🔬 Execuție pas cu pas</p>
      <div class="flex items-center gap-1.5" v-if="pasi.length">
        <button @click="laPasul(0)" class="ctrl" title="Primul pas">⏮</button>
        <button @click="laPasul(index - 1)" class="ctrl" title="Pasul anterior">◀</button>
        <button @click="comutaAuto" class="ctrl w-16" :title="ruleazaAuto ? 'Pauză' : 'Redare automată'">
          {{ ruleazaAuto ? '⏸ stop' : '▶ auto' }}
        </button>
        <button @click="laPasul(index + 1)" class="ctrl" title="Pasul următor">▶</button>
        <button @click="laPasul(pasi.length - 1)" class="ctrl" title="Ultimul pas">⏭</button>
        <span class="text-xs text-gray-500 font-mono ml-2 w-20 text-center">pas {{ index + 1 }}/{{ pasi.length }}</span>
      </div>
      <button @click="emit('inchide')" class="text-gray-500 hover:text-gray-300 text-sm">✕ închide</button>
    </div>

    <!-- Slider -->
    <div v-if="pasi.length > 1" class="px-4 pt-3">
      <input type="range" min="0" :max="pasi.length - 1" :value="index"
             @input="oprireAuto(); laPasul(Number($event.target.value))"
             class="w-full accent-[#42b883]" />
    </div>

    <div v-if="sePregateste" class="p-6 text-sm text-amber-400/80">
      ⏳ Se trasează execuția (Pyodide)…
    </div>
    <div v-else-if="eroareIncarcare" class="p-6 text-sm text-red-400">{{ eroareIncarcare }}</div>

    <div v-else class="grid md:grid-cols-2 gap-0">
      <!-- Codul, cu linia activă evidențiată -->
      <div class="border-r border-white/10 overflow-x-auto">
        <pre class="text-[13px] font-mono leading-6 py-3"><template v-for="(linie, i) in liniiCod" :key="i"><div class="px-3 flex" :class="pas && pas.linie === i + 1 ? (pas.eveniment === 'exception' ? 'bg-red-500/15' : 'bg-[#42b883]/15') : ''"><span class="w-8 shrink-0 text-right pr-3 select-none" :class="pas && pas.linie === i + 1 ? 'text-[#42b883] font-bold' : 'text-gray-600'">{{ i + 1 }}</span><span class="text-gray-200 whitespace-pre">{{ linie || ' ' }}</span><span v-if="pas && pas.linie === i + 1" class="ml-2 select-none" :class="pas.eveniment === 'exception' ? 'text-red-400' : 'text-[#42b883]'">◀</span></div></template></pre>
      </div>

      <!-- Starea programului la pasul curent -->
      <div class="p-4 space-y-3 text-sm">
        <div v-if="pas" class="flex items-center gap-2 flex-wrap">
          <span class="text-[11px] uppercase tracking-wider px-2 py-0.5 rounded-full font-bold"
                :class="ETICHETE_EVENIMENT[pas.eveniment]?.[1]">
            {{ ETICHETE_EVENIMENT[pas.eveniment]?.[0] }} {{ pas.linie }}
          </span>
          <span v-if="pas.functie" class="text-xs text-gray-400">
            în <span class="font-mono text-amber-300">{{ pas.functie }}()</span>
            <span v-if="pas.adancime > 1" class="text-gray-600"> · nivel {{ pas.adancime }}</span>
          </span>
        </div>

        <p v-if="pas?.exceptie" class="text-red-300 font-mono text-xs bg-red-500/10 rounded-lg px-3 py-2">
          💥 {{ pas.exceptie }}
        </p>
        <p v-if="pas?.retur !== undefined" class="text-blue-300 font-mono text-xs bg-blue-500/10 rounded-lg px-3 py-2">
          ↩ returnează {{ pas.retur }}
        </p>

        <!-- Variabilele locale (în funcție) -->
        <div v-if="pas?.locale && Object.keys(pas.locale).length">
          <p class="text-[10px] uppercase tracking-wider text-amber-400/90 font-bold mb-1.5">
            Variabile locale ({{ pas.functie }})
          </p>
          <table class="w-full text-xs font-mono">
            <tr v-for="(valoare, nume) in pas.locale" :key="nume" class="border-b border-white/5">
              <td class="py-1 pr-3 text-gray-400 w-1/3">{{ nume }}</td>
              <td class="py-1 text-[#7ee0b0] break-all">{{ valoare }}</td>
            </tr>
          </table>
        </div>

        <!-- Variabilele globale -->
        <div v-if="pas && Object.keys(pas.globale).length">
          <p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1.5">Variabile globale</p>
          <table class="w-full text-xs font-mono">
            <tr v-for="(valoare, nume) in pas.globale" :key="nume" class="border-b border-white/5">
              <td class="py-1 pr-3 text-gray-400 w-1/3">{{ nume }}</td>
              <td class="py-1 text-gray-200 break-all">{{ valoare }}</td>
            </tr>
          </table>
        </div>
        <p v-else-if="pas && !pas.locale" class="text-xs text-gray-600">Nicio variabilă definită încă.</p>

        <!-- Output-ul de până acum -->
        <div>
          <p class="text-[10px] uppercase tracking-wider text-gray-500 font-bold mb-1.5">Output până la acest pas</p>
          <pre class="text-xs font-mono text-gray-200 bg-[#101010] border border-white/10 rounded-lg px-3 py-2 min-h-10 whitespace-pre-wrap">{{ stdoutVizibil || '(nimic încă)' }}</pre>
        </div>

        <p v-if="raport?.eroare && !pas?.exceptie" class="text-xs text-red-400">
          Programul s-a oprit: {{ raport.eroare }}
        </p>
        <p v-if="raport?.trunchiat" class="text-xs text-amber-400">
          ⚠ Trasare oprită după {{ MAX_PASI }} de pași (program lung sau buclă mare).
        </p>
      </div>
    </div>

    <!-- Intrarea pentru input() -->
    <div class="px-4 pb-4">
      <button @click="arataIntrare = !arataIntrare" class="text-[11px] text-gray-500 hover:text-gray-300">
        {{ arataIntrare ? '▾' : '▸' }} Intrare pentru input() (o valoare pe linie)
      </button>
      <div v-if="arataIntrare" class="mt-2 flex gap-2">
        <textarea v-model="intrare" rows="2" placeholder="ex: 5"
                  class="flex-1 bg-[#101010] border border-white/10 rounded-lg px-3 py-2 text-xs font-mono text-white placeholder-gray-600 focus:border-[#42b883]/60 focus:outline-none"></textarea>
        <button @click="traseaza"
                class="self-start bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-4 py-2 rounded-lg text-xs">
          Retrasează
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ctrl {
  width: 2.25rem;
  height: 2rem;
  display: grid;
  place-items: center;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #d1d5db;
  font-size: 0.75rem;
  transition: all 0.15s ease;
}
.ctrl:hover {
  border-color: rgba(66, 184, 131, 0.5);
  color: #42b883;
}
</style>
