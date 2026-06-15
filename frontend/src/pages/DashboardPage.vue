<script setup>
// Acasă: starea zilei + recomandările explicabile ale sistemului.
import { onMounted, ref } from 'vue'
import client from '@/api/client'
import { useAuth } from '@/stores/auth'

const auth = useAuth()
const recomandari = ref([])
const continua = ref(null)
const statistici = ref(null)
const seIncarca = ref(true)

const ICONITE = { recapitulare: '🔁', exercitiu: '🧩', lectie: '📖', test_adaptiv: '🎯' }
const RUTE = {
  recapitulare: () => '/recapitulare',
  test_adaptiv: () => '/test-adaptiv',
  lectie: (r) => `/lectii/${r.lectie_slug}`,
  exercitiu: (r) => `/exercitii/${r.exercitiu_id}`,
}

onMounted(async () => {
  try {
    const [rec, stat] = await Promise.all([
      client.get('/progres/recomandari'),
      client.get('/progres/statistici'),
    ])
    recomandari.value = rec.data.recomandari
    continua.value = rec.data.continua
    statistici.value = stat.data
  } finally {
    seIncarca.value = false
  }
})
</script>

<template>
  <div class="max-w-5xl mx-auto px-8 py-10">
    <h1 class="text-2xl font-bold text-white">Salut, {{ auth.nume.split(' ')[0] }} 👋</h1>
    <p class="text-gray-400 text-sm mt-1">Sistemul ți-a pregătit pașii de azi — fiecare cu motivul lui.</p>

    <!-- Statistici rapide -->
    <div v-if="statistici" class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-7">
      <div class="rounded-2xl border border-white/10 bg-[#101010] p-4">
        <p class="text-2xl font-bold text-white">🔥 {{ statistici.streak }}</p>
        <p class="text-xs text-gray-500 mt-1">zile la rând</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-[#101010] p-4">
        <p class="text-2xl font-bold text-[#42b883]">{{ statistici.nivel.nivel }}</p>
        <p class="text-xs text-gray-500 mt-1">nivel · {{ statistici.xp_total }} XP</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-[#101010] p-4">
        <p class="text-2xl font-bold text-white">{{ statistici.concepte.stapanite }}<span class="text-sm text-gray-500">/{{ statistici.concepte.total }}</span></p>
        <p class="text-xs text-gray-500 mt-1">concepte stăpânite</p>
      </div>
      <router-link to="/recapitulare" class="rounded-2xl border p-4 transition-all"
                   :class="statistici.recapitulari_scadente > 0
                     ? 'border-amber-500/40 bg-amber-500/5 hover:bg-amber-500/10'
                     : 'border-white/10 bg-[#101010]'">
        <p class="text-2xl font-bold" :class="statistici.recapitulari_scadente > 0 ? 'text-amber-400' : 'text-white'">
          {{ statistici.recapitulari_scadente }}
        </p>
        <p class="text-xs text-gray-500 mt-1">recapitulări scadente</p>
      </router-link>
    </div>

    <!-- Calibrarea inițială, pentru conturile noi -->
    <router-link v-if="statistici && statistici.concepte.studiate === 0" to="/plasament"
                 class="mt-7 flex items-center justify-between rounded-2xl border border-amber-500/40 bg-amber-500/5 hover:bg-amber-500/10 p-5 transition-all group">
      <div class="flex items-center gap-4">
        <span class="text-3xl">🧭</span>
        <div>
          <p class="text-xs text-amber-400 font-bold uppercase tracking-wider">Recomandat înainte de orice</p>
          <p class="text-white font-semibold mt-1">Fă testul de calibrare (~5 minute)</p>
          <p class="text-sm text-gray-400 mt-0.5">10 întrebări care învață sistemul de unde să înceapă cu tine — poate sări lecțiile pe care le știi deja.</p>
        </div>
      </div>
      <span class="text-amber-400 text-xl group-hover:translate-x-1 transition-transform shrink-0">→</span>
    </router-link>

    <!-- Continuă de unde ai rămas -->
    <router-link v-if="continua" :to="`/lectii/${continua.lectie_slug}`"
                 class="mt-7 flex items-center justify-between rounded-2xl border border-[#42b883]/30 bg-[#42b883]/5 hover:bg-[#42b883]/10 p-5 transition-all group">
      <div>
        <p class="text-xs text-[#42b883] font-bold uppercase tracking-wider">Continuă de unde ai rămas</p>
        <p class="text-white font-semibold mt-1">{{ continua.titlu }}</p>
      </div>
      <span class="text-[#42b883] text-xl group-hover:translate-x-1 transition-transform">→</span>
    </router-link>

    <!-- Recomandările sistemului -->
    <h2 class="text-lg font-semibold text-white mt-9 mb-4">Recomandat pentru tine</h2>
    <div v-if="seIncarca" class="text-gray-500 text-sm">Se încarcă…</div>
    <div v-else-if="!recomandari.length" class="text-gray-500 text-sm rounded-xl border border-white/10 p-5">
      Totul la zi! Explorează cursul în ritmul tău. 🎉
    </div>
    <div v-else class="space-y-3">
      <router-link v-for="(rec, index) in recomandari" :key="index"
                   :to="RUTE[rec.tip]?.(rec) || '/curs'"
                   class="flex gap-4 rounded-2xl border border-white/10 bg-[#101010] hover:border-[#42b883]/40 p-5 transition-all group">
        <span class="text-2xl shrink-0 mt-0.5">{{ ICONITE[rec.tip] }}</span>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <p class="text-white font-semibold">{{ rec.titlu }}</p>
            <span v-if="index === 0" class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#42b883]/15 text-[#42b883] font-bold">prioritar</span>
          </div>
          <p class="text-sm text-gray-400 mt-1 leading-relaxed">
            <span class="text-gray-500 font-medium">De ce:</span> {{ rec.motiv }}
          </p>
        </div>
        <span class="text-gray-600 group-hover:text-[#42b883] group-hover:translate-x-1 transition-all self-center">→</span>
      </router-link>
    </div>

    <!-- Greșelile frecvente -->
    <div v-if="statistici?.erori_frecvente?.length" class="mt-9">
      <h2 class="text-lg font-semibold text-white mb-4">Greșelile tale frecvente</h2>
      <div class="rounded-2xl border border-white/10 bg-[#101010] divide-y divide-white/5">
        <div v-for="eroare in statistici.erori_frecvente" :key="eroare.categorie"
             class="flex items-center justify-between px-5 py-3">
          <span class="text-sm text-gray-300">{{ eroare.titlu }}</span>
          <span class="text-xs text-gray-500 font-mono">{{ eroare.numar }}×</span>
        </div>
      </div>
    </div>
  </div>
</template>
