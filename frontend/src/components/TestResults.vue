<script setup>
// Tabelul cu verdictul testelor unui exercițiu (local sau oficial).
defineProps({
  rezultat: { type: Object, required: true }, // {status, teste_trecute, teste_total, rezultate, eroare?, eroare_mesaj?, eroare_globala?}
  oficial: { type: Boolean, default: false },
})

const ETICHETE = {
  acceptat: ['✓ Toate testele trec', 'text-emerald-400'],
  teste_esuate: ['✗ Unele teste pică', 'text-red-400'],
  eroare: ['✗ Eroare la execuție', 'text-red-400'],
  timeout: ['⏱ Timpul a expirat', 'text-amber-400'],
  blocat: ['🛑 Cod nepermis', 'text-red-400'],
}
</script>

<template>
  <div class="rounded-xl border border-white/10 bg-[#101010] overflow-hidden">
    <div class="flex items-center justify-between px-4 py-2.5 border-b border-white/10 bg-[#0c0c0c]">
      <span class="text-sm font-semibold" :class="ETICHETE[rezultat.status]?.[1] || 'text-gray-300'">
        {{ ETICHETE[rezultat.status]?.[0] || rezultat.status }}
        <span class="text-gray-500 font-normal ml-2">{{ rezultat.teste_trecute }}/{{ rezultat.teste_total }} teste</span>
      </span>
      <span v-if="oficial" class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#42b883]/15 text-[#42b883] font-bold">verdict oficial</span>
      <span v-else class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-white/5 text-gray-400 font-bold">rulare locală</span>
    </div>

    <!-- Eroare globală (sintaxă, excepție la definire) -->
    <div v-if="rezultat.eroare_globala || rezultat.eroare_mesaj" class="px-4 py-3 border-b border-white/10">
      <p class="text-sm text-red-300 font-mono whitespace-pre-wrap">{{ rezultat.eroare_globala ? `${rezultat.eroare_globala.tip}: ${rezultat.eroare_globala.mesaj}` + (rezultat.eroare_globala.linie ? ` (linia ${rezultat.eroare_globala.linie})` : '') : rezultat.eroare_mesaj }}</p>
      <div v-if="rezultat.eroare" class="mt-2 text-sm bg-[#161616] rounded-lg p-3 border border-white/5">
        <p class="font-semibold text-amber-300">{{ rezultat.eroare.titlu }}</p>
        <p class="text-gray-300 mt-1">{{ rezultat.eroare.explicatie }}</p>
        <p class="text-gray-400 mt-1">💡 {{ rezultat.eroare.sfat }}</p>
      </div>
    </div>

    <table v-if="rezultat.rezultate?.length" class="w-full text-sm">
      <tbody>
        <tr v-for="(test, index) in rezultat.rezultate" :key="index"
            class="border-b border-white/5 last:border-0">
          <td class="px-4 py-2 w-8">
            <span :class="test.trecut ? 'text-emerald-400' : 'text-red-400'">{{ test.trecut ? '✓' : '✗' }}</span>
          </td>
          <td class="px-2 py-2 font-mono text-xs text-gray-300 whitespace-pre-wrap break-all">{{ test.descriere }}</td>
          <td class="px-2 py-2 font-mono text-xs text-gray-400">
            <span class="text-gray-500">așteptat:</span> {{ test.asteptat }}
          </td>
          <td class="px-4 py-2 font-mono text-xs" :class="test.trecut ? 'text-gray-400' : 'text-red-300'">
            <template v-if="test.eroare"><span class="text-gray-500">eroare:</span> {{ test.eroare.tip }}: {{ test.eroare.mesaj }}</template>
            <template v-else><span class="text-gray-500">obținut:</span> {{ test.obtinut ?? '—' }}</template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
