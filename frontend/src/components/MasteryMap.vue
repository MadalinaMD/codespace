<script setup>
// Harta măiestriei: graful de concepte ca DAG pe straturi, colorat după
// probabilitatea BKT de cunoaștere. Nodurile sunt clickabile → lecția-sursă.
import { computed } from 'vue'

const props = defineProps({ concepte: { type: Array, required: true } })
const emit = defineEmits(['selecteaza'])

const LATIME = 880
const PAS_Y = 92

const CULORI = {
  nestudiat: { fill: '#262626', stroke: '#404040', text: '#737373' },
  slab: { fill: '#3d1412', stroke: '#ef4444', text: '#fca5a5' },
  in_lucru: { fill: '#3a2a10', stroke: '#f59e0b', text: '#fcd34d' },
  stapanit: { fill: '#0e2e1f', stroke: '#10b981', text: '#6ee7b7' },
}

const aranjament = computed(() => {
  const dupaSlug = Object.fromEntries(props.concepte.map((c) => [c.slug, c]))
  const adancimi = {}
  const adancime = (slug, vizitate = new Set()) => {
    if (slug in adancimi) return adancimi[slug]
    if (vizitate.has(slug)) return 0 // protecție la cicluri accidentale
    vizitate.add(slug)
    const nod = dupaSlug[slug]
    const parinti = (nod?.prerechizite || []).filter((p) => dupaSlug[p])
    adancimi[slug] = parinti.length
      ? 1 + Math.max(...parinti.map((p) => adancime(p, vizitate)))
      : 0
    return adancimi[slug]
  }
  props.concepte.forEach((c) => adancime(c.slug))

  // Grupare pe straturi, ordonate pedagogic
  const straturi = {}
  for (const concept of props.concepte) {
    const nivel = adancimi[concept.slug]
    ;(straturi[nivel] ||= []).push(concept)
  }
  const pozitii = {}
  for (const [nivel, noduri] of Object.entries(straturi)) {
    noduri.sort((a, b) => a.ordine - b.ordine)
    noduri.forEach((nod, index) => {
      pozitii[nod.slug] = {
        x: ((index + 1) * LATIME) / (noduri.length + 1),
        y: 46 + Number(nivel) * PAS_Y,
      }
    })
  }

  const muchii = []
  for (const concept of props.concepte) {
    for (const prerechizit of concept.prerechizite) {
      if (pozitii[prerechizit]) {
        muchii.push({ din: pozitii[prerechizit], spre: pozitii[concept.slug] })
      }
    }
  }
  const inaltime = 46 + (Math.max(...Object.values(adancimi), 0) + 1) * PAS_Y
  return { pozitii, muchii, inaltime }
})

function scurteaza(nume) {
  return nume.length > 18 ? nume.slice(0, 17) + '…' : nume
}
</script>

<template>
  <div class="rounded-2xl border border-white/10 bg-[#0d0d0d] overflow-x-auto">
    <svg :viewBox="`0 0 ${LATIME} ${aranjament.inaltime}`" class="w-full min-w-[760px]">
      <!-- Muchiile de prerechizit -->
      <path v-for="(muchie, index) in aranjament.muchii" :key="index"
            :d="`M ${muchie.din.x} ${muchie.din.y + 17} C ${muchie.din.x} ${muchie.din.y + 50}, ${muchie.spre.x} ${muchie.spre.y - 50}, ${muchie.spre.x} ${muchie.spre.y - 17}`"
            fill="none" stroke="#2a2a2a" stroke-width="1.2" />

      <!-- Nodurile -->
      <g v-for="concept in concepte" :key="concept.slug"
         class="cursor-pointer"
         @click="emit('selecteaza', concept)">
        <title>{{ concept.nume }} — stăpânire {{ Math.round(concept.p * 100) }}% ({{ concept.observatii }} observații)</title>
        <circle :cx="aranjament.pozitii[concept.slug].x" :cy="aranjament.pozitii[concept.slug].y" r="17"
                :fill="CULORI[concept.stare].fill" :stroke="CULORI[concept.stare].stroke" stroke-width="1.6" />
        <text :x="aranjament.pozitii[concept.slug].x" :y="aranjament.pozitii[concept.slug].y + 3.5"
              text-anchor="middle" font-size="9.5" font-weight="700"
              :fill="CULORI[concept.stare].text">{{ Math.round(concept.p * 100) }}</text>
        <text :x="aranjament.pozitii[concept.slug].x" :y="aranjament.pozitii[concept.slug].y + 31"
              text-anchor="middle" font-size="9" fill="#8a8a8a">{{ scurteaza(concept.nume) }}</text>
      </g>
    </svg>

    <div class="flex flex-wrap items-center gap-4 px-5 py-3 border-t border-white/10 text-[11px] text-gray-500">
      <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full border" style="background:#262626;border-color:#404040"></span> nestudiat</span>
      <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full border" style="background:#3d1412;border-color:#ef4444"></span> slab (&lt;60%)</span>
      <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full border" style="background:#3a2a10;border-color:#f59e0b"></span> în lucru</span>
      <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-full border" style="background:#0e2e1f;border-color:#10b981"></span> stăpânit (≥95%)</span>
      <span class="ml-auto">cifra din nod = p(cunoaștere) estimată de modelul BKT · click pe nod → lecția lui</span>
    </div>
  </div>
</template>
