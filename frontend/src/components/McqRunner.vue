<script setup>
// Motorul de întrebări grilă, refolosit de quiz, recapitulare și testul adaptiv.
// Notarea o face SERVERUL: componenta primește o funcție `raspunde` care
// întoarce verdictul {corect, corecta, explicatie} abia după trimitere.
import { computed, ref } from 'vue'

const props = defineProps({
  intrebari: { type: Array, required: true },   // [{cheie, text, variante, meta?}]
  raspunde: { type: Function, required: true }, // async (intrebare, raspuns) => verdict
})
const emit = defineEmits(['terminat'])

const index = ref(0)
const verdict = ref(null)
const alegere = ref(null)
const seVerifica = ref(false)
const scor = ref(0)
const istoric = ref([])

const intrebarea = computed(() => props.intrebari[index.value])
const progres = computed(() => Math.round((index.value / props.intrebari.length) * 100))

async function alege(varianta) {
  if (verdict.value || seVerifica.value) return
  alegere.value = varianta
  seVerifica.value = true
  try {
    verdict.value = await props.raspunde(intrebarea.value, varianta)
    if (verdict.value.corect) scor.value++
    istoric.value.push({ intrebare: intrebarea.value, ...verdict.value })
  } finally {
    seVerifica.value = false
  }
}

function urmatoarea() {
  if (index.value < props.intrebari.length - 1) {
    index.value++
    verdict.value = null
    alegere.value = null
  } else {
    emit('terminat', { scor: scor.value, total: props.intrebari.length, istoric: istoric.value })
  }
}

function clasaVarianta(varianta) {
  if (!verdict.value) {
    return alegere.value === varianta && seVerifica.value
      ? 'border-[#42b883]/60 bg-[#42b883]/10'
      : 'border-white/10 bg-[#121212] hover:border-[#42b883]/50 hover:bg-[#42b883]/5 cursor-pointer'
  }
  if (varianta === verdict.value.corecta) return 'border-emerald-500/70 bg-emerald-500/10'
  if (varianta === alegere.value) return 'border-red-500/70 bg-red-500/10'
  return 'border-white/5 bg-[#101010] opacity-50'
}
</script>

<template>
  <div v-if="intrebarea">
    <!-- Bara de progres -->
    <div class="flex items-center gap-3 mb-5">
      <div class="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div class="h-full bg-[#42b883] transition-all duration-300" :style="{ width: progres + '%' }"></div>
      </div>
      <span class="text-xs text-gray-500 font-mono">{{ index + 1 }}/{{ intrebari.length }}</span>
    </div>

    <div class="rounded-2xl border border-white/10 bg-[#101010] p-6">
      <p v-if="intrebarea.meta" class="text-xs text-gray-500 uppercase tracking-wider mb-2">{{ intrebarea.meta }}</p>
      <p class="text-lg text-white font-medium leading-relaxed whitespace-pre-wrap">{{ intrebarea.text }}</p>

      <div class="mt-5 space-y-2.5">
        <button v-for="varianta in intrebarea.variante" :key="varianta"
                @click="alege(varianta)"
                class="w-full text-left px-4 py-3 rounded-xl border transition-all text-sm font-mono whitespace-pre-wrap"
                :class="clasaVarianta(varianta)">
          {{ varianta }}
        </button>
      </div>

      <!-- Feedback după răspuns -->
      <div v-if="verdict" class="mt-5 rounded-xl p-4 border"
           :class="verdict.corect ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-red-500/30 bg-red-500/5'">
        <p class="font-semibold" :class="verdict.corect ? 'text-emerald-400' : 'text-red-400'">
          {{ verdict.corect ? '✓ Corect!' : '✗ Greșit' }}
          <span v-if="!verdict.corect" class="text-gray-300 font-normal"> — răspunsul corect: <span class="font-mono">{{ verdict.corecta }}</span></span>
        </p>
        <p v-if="verdict.explicatie" class="text-sm text-gray-300 mt-1.5">{{ verdict.explicatie }}</p>
        <p v-if="verdict.detaliu" class="text-xs text-gray-400 mt-1.5">{{ verdict.detaliu }}</p>
        <button @click="urmatoarea"
                class="mt-3 bg-[#42b883] hover:bg-[#3aa876] text-black font-bold px-5 py-2 rounded-lg text-sm transition-all">
          {{ index < intrebari.length - 1 ? 'Întrebarea următoare →' : 'Vezi rezultatul' }}
        </button>
      </div>
    </div>
  </div>
</template>
