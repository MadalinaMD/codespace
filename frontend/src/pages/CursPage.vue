<script setup>
// Harta cursului: capitole → lecții, cu starea fiecărei lecții pentru student.
import { onMounted, ref } from 'vue'
import client from '@/api/client'

const capitole = ref([])
const seIncarca = ref(true)

onMounted(async () => {
  try {
    const { data } = await client.get('/curs')
    capitole.value = data
  } finally {
    seIncarca.value = false
  }
})
</script>

<template>
  <div class="max-w-5xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Cursul de Python</h1>
    <p class="text-gray-400 text-sm mt-1">
      Sistemul îți recomandă ordinea, dar nu te încuie: lecțiile cu fundament nepregătit sunt doar marcate.
    </p>

    <div v-if="seIncarca" class="text-gray-500 text-sm mt-8">Se încarcă…</div>

    <div v-else class="mt-8 space-y-6">
      <section v-for="capitol in capitole" :key="capitol.slug"
               class="rounded-2xl border border-white/10 bg-[#101010] overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#0d0d0d]">
          <div>
            <h2 class="text-white font-semibold">{{ capitol.titlu }}</h2>
            <p class="text-xs text-gray-500 mt-0.5">{{ capitol.descriere }}</p>
          </div>
          <router-link :to="`/quiz/${capitol.slug}`"
                       class="shrink-0 text-xs font-bold px-4 py-2 rounded-lg border transition-all"
                       :class="capitol.quiz
                         ? 'border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10'
                         : 'border-[#42b883]/40 text-[#42b883] hover:bg-[#42b883]/10'">
            {{ capitol.quiz ? `Quiz: ${capitol.quiz.scor}/${capitol.quiz.total} · reia` : 'Quiz capitol' }}
          </router-link>
        </div>

        <div class="divide-y divide-white/5">
          <router-link v-for="lectie in capitol.lectii" :key="lectie.slug"
                       :to="`/lectii/${lectie.slug}`"
                       class="flex items-center gap-4 px-6 py-3.5 hover:bg-white/[0.03] transition-colors group">
            <!-- Starea lecției -->
            <span class="w-7 h-7 rounded-full grid place-items-center text-xs shrink-0 border"
                  :class="lectie.vizitata
                    ? 'bg-[#42b883]/15 border-[#42b883]/40 text-[#42b883]'
                    : lectie.fundament_gata
                      ? 'bg-white/5 border-white/15 text-gray-400'
                      : 'bg-amber-500/10 border-amber-500/30 text-amber-400'">
              {{ lectie.vizitata ? '✓' : (lectie.fundament_gata ? '○' : '!') }}
            </span>

            <div class="flex-1 min-w-0">
              <p class="text-sm text-gray-200 group-hover:text-white transition-colors">{{ lectie.titlu }}</p>
              <p v-if="!lectie.fundament_gata" class="text-[11px] text-amber-400/90 mt-0.5">
                Recomandat întâi: {{ lectie.prerechizite_lipsa.join(', ') }}
              </p>
              <p v-else-if="lectie.concepte.length" class="text-[11px] text-gray-600 mt-0.5">
                {{ lectie.concepte.join(' · ') }}
              </p>
            </div>

            <span v-if="lectie.exercitii_total" class="text-[11px] font-mono shrink-0"
                  :class="lectie.exercitii_rezolvate === lectie.exercitii_total ? 'text-emerald-400' : 'text-gray-500'">
              {{ lectie.exercitii_rezolvate }}/{{ lectie.exercitii_total }} ex.
            </span>
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>
