<script setup>
// Tutorele AI: chat cu streaming SSE, ancorat în lecții, cu citări clickabile.
import { nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { API_URL } from '@/api/client'
import { randeazaMarkdown } from '@/lib/markdown'

const route = useRoute()
const mesaje = ref([])
const intrebare = ref('')
const seRaspunde = ref(false)
const zonaChat = ref(null)
const lectieContext = ref(route.query.lectie || null)

onMounted(async () => {
  const raspuns = await fetch(`${API_URL}/tutor/istoric`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  if (raspuns.ok) mesaje.value = await raspuns.json()
  deruleaza()
})

function deruleaza() {
  nextTick(() => { zonaChat.value && (zonaChat.value.scrollTop = zonaChat.value.scrollHeight) })
}

async function trimite() {
  const text = intrebare.value.trim()
  if (!text || seRaspunde.value) return
  intrebare.value = ''
  seRaspunde.value = true
  mesaje.value.push({ rol: 'user', continut: text, surse: [] })
  const mesajAsistent = { rol: 'asistent', continut: '', surse: [] }
  mesaje.value.push(mesajAsistent)
  deruleaza()

  try {
    // SSE prin fetch: axios nu suportă streaming în browser
    const raspuns = await fetch(`${API_URL}/tutor/intreaba`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ intrebare: text, lectie_slug: lectieContext.value }),
    })
    if (!raspuns.ok) {
      const date = await raspuns.json().catch(() => null)
      mesajAsistent.continut = date?.detail || `Eroare ${raspuns.status} — încearcă din nou.`
      return
    }

    const cititor = raspuns.body.getReader()
    const decodor = new TextDecoder()
    let tampon = ''
    let evenimentCurent = ''

    while (true) {
      const { done, value } = await cititor.read()
      if (done) break
      tampon += decodor.decode(value, { stream: true })

      let pozitie
      while ((pozitie = tampon.indexOf('\n')) !== -1) {
        const linie = tampon.slice(0, pozitie).trimEnd()
        tampon = tampon.slice(pozitie + 1)
        if (linie.startsWith('event:')) {
          evenimentCurent = linie.slice(6).trim()
        } else if (linie.startsWith('data:')) {
          const date = linie.slice(5).trim()
          if (date === '[DONE]') continue
          if (evenimentCurent === 'surse') {
            mesajAsistent.surse = JSON.parse(date)
            evenimentCurent = ''
          } else {
            const fragment = JSON.parse(date)
            mesajAsistent.continut += fragment.text || ''
            deruleaza()
          }
        }
      }
    }
  } catch (e) {
    mesajAsistent.continut += `\n\n(Conexiunea s-a întrerupt: ${e.message})`
  } finally {
    seRaspunde.value = false
    deruleaza()
  }
}

async function stergeIstoric() {
  if (!confirm('Ștergi toată conversația cu tutorele?')) return
  await fetch(`${API_URL}/tutor/istoric`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  mesaje.value = []
}
</script>

<template>
  <div class="h-screen flex flex-col max-w-4xl mx-auto px-8 py-8">
    <div class="flex items-center justify-between shrink-0">
      <div>
        <h1 class="text-2xl font-bold text-white">Tutore AI</h1>
        <p class="text-gray-400 text-sm mt-1">
          Răspunde din lecțiile cursului, cu citări — și te ghidează socratic, nu îți dă soluțiile de-a gata.
        </p>
      </div>
      <button v-if="mesaje.length" @click="stergeIstoric"
              class="text-xs text-gray-500 hover:text-red-400 border border-white/10 rounded-lg px-3 py-2 transition-colors shrink-0">
        Șterge conversația
      </button>
    </div>

    <p v-if="lectieContext" class="shrink-0 mt-3 text-xs text-[#42b883] bg-[#42b883]/10 border border-[#42b883]/20 rounded-lg px-3 py-2">
      Context activ: lecția „{{ lectieContext }}”
      <button @click="lectieContext = null" class="ml-2 text-gray-400 hover:text-white">✕</button>
    </p>

    <!-- Conversația -->
    <div ref="zonaChat" class="flex-1 overflow-y-auto mt-5 space-y-4 pr-1">
      <div v-if="!mesaje.length" class="text-center text-gray-600 text-sm mt-16">
        <p class="text-4xl mb-3">💬</p>
        <p>Întreabă orice despre Python — de exemplu:</p>
        <p class="mt-2 text-gray-500">„Care e diferența dintre listă și tuplu?” · „De ce primesc IndexError?”</p>
      </div>

      <div v-for="(mesaj, index) in mesaje" :key="index"
           class="flex" :class="mesaj.rol === 'user' ? 'justify-end' : 'justify-start'">
        <div class="max-w-[85%] rounded-2xl px-4 py-3"
             :class="mesaj.rol === 'user'
               ? 'bg-[#42b883]/15 border border-[#42b883]/25'
               : 'bg-[#121212] border border-white/10'">
          <div v-if="mesaj.rol === 'asistent'" class="markdown text-sm" v-html="randeazaMarkdown(mesaj.continut || '…')"></div>
          <p v-else class="text-sm text-gray-100 whitespace-pre-wrap">{{ mesaj.continut }}</p>

          <!-- Citările -->
          <div v-if="mesaj.surse?.length" class="flex flex-wrap gap-1.5 mt-2.5 pt-2.5 border-t border-white/5">
            <router-link v-for="sursa in mesaj.surse" :key="sursa.lectie_slug"
                         :to="`/lectii/${sursa.lectie_slug}`"
                         class="text-[11px] px-2 py-1 rounded-md bg-white/5 text-gray-400 hover:text-[#42b883] hover:bg-[#42b883]/10 transition-colors">
              📖 {{ sursa.lectie }}
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Caseta de scris -->
    <form @submit.prevent="trimite" class="shrink-0 mt-4 flex gap-2">
      <input v-model="intrebare" :disabled="seRaspunde"
             placeholder="Scrie întrebarea ta…"
             class="flex-1 bg-[#101010] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:border-[#42b883]/60 focus:outline-none transition-colors" />
      <button type="submit" :disabled="seRaspunde || !intrebare.trim()"
              class="bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-40 text-black font-bold px-6 rounded-xl text-sm transition-all">
        {{ seRaspunde ? '…' : 'Trimite' }}
      </button>
    </form>
  </div>
</template>
