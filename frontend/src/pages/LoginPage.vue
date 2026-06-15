<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/stores/auth'
import client, { mesajEroare } from '@/api/client'

const router = useRouter()
const auth = useAuth()

const mod = ref('login') // login | inregistrare | reset
const nume = ref('')
const email = ref('')
const parola = ref('')
const eroare = ref('')
const mesaj = ref('')
const seTrimite = ref(false)

// Rezultatul resetării: parola temporară primită
const parolaTemporara = ref('')
const parolaCopiata = ref(false)

function schimbaMod(nou) {
  mod.value = nou
  eroare.value = ''
  mesaj.value = ''
  parolaTemporara.value = ''
  parolaCopiata.value = false
}

async function trimite() {
  eroare.value = ''
  mesaj.value = ''
  seTrimite.value = true
  try {
    if (mod.value === 'login') {
      await auth.login(email.value, parola.value)
      router.push('/')
    } else if (mod.value === 'inregistrare') {
      await auth.inregistrare(nume.value, email.value, parola.value)
      mesaj.value = 'Cont creat! Acum te poți autentifica.'
      mod.value = 'login'
      parola.value = ''
    } else {
      // mod === 'reset'
      const { data } = await client.post('/auth/reset-parola', { email: email.value })
      parolaTemporara.value = data.parola_temporara
    }
  } catch (e) {
    eroare.value = mesajEroare(e, 'Conexiunea la server a eșuat. Backend-ul rulează?')
  } finally {
    seTrimite.value = false
  }
}

async function copiaza() {
  try {
    await navigator.clipboard.writeText(parolaTemporara.value)
    parolaCopiata.value = true
    setTimeout(() => (parolaCopiata.value = false), 2000)
  } catch { /* clipboard indisponibil — utilizatorul o poate selecta manual */ }
}

function mergiLaLogin() {
  // Pre-completăm parola temporară ca să se poată loga dintr-un click
  parola.value = parolaTemporara.value
  schimbaMod('login')
}
</script>

<template>
  <div class="min-h-screen grid place-items-center px-4">
    <div class="w-full max-w-md">
      <!-- Logo -->
      <div class="flex items-center justify-center gap-3 mb-8">
        <span class="w-12 h-12 rounded-2xl bg-[#42b883] text-black font-black grid place-items-center text-2xl">C</span>
        <div>
          <h1 class="text-2xl font-bold text-white tracking-tight">CodeSpace</h1>
          <p class="text-xs text-gray-500">Sistem inteligent pentru învățarea programării</p>
        </div>
      </div>

      <div class="rounded-2xl border border-white/10 bg-[#101010] p-7">
        <!-- Taburi (ascunse în modul resetare) -->
        <div v-if="mod !== 'reset'" class="grid grid-cols-2 gap-1 p-1 rounded-xl bg-[#0a0a0a] border border-white/5 mb-6">
          <button @click="schimbaMod('login')"
                  class="py-2 rounded-lg text-sm font-semibold transition-all"
                  :class="mod === 'login' ? 'bg-[#42b883] text-black' : 'text-gray-400 hover:text-gray-200'">
            Autentificare
          </button>
          <button @click="schimbaMod('inregistrare')"
                  class="py-2 rounded-lg text-sm font-semibold transition-all"
                  :class="mod === 'inregistrare' ? 'bg-[#42b883] text-black' : 'text-gray-400 hover:text-gray-200'">
            Cont nou
          </button>
        </div>

        <!-- Antetul modului de resetare -->
        <div v-if="mod === 'reset'" class="mb-5">
          <button @click="schimbaMod('login')" class="text-xs text-gray-500 hover:text-gray-300 transition-colors">← Înapoi la autentificare</button>
          <h2 class="text-lg font-semibold text-white mt-2">Ai uitat parola?</h2>
          <p class="text-sm text-gray-400 mt-1">Introdu emailul contului și îți generăm pe loc o parolă temporară.</p>
        </div>

        <!-- Rezultatul resetării: parola temporară -->
        <div v-if="mod === 'reset' && parolaTemporara">
          <div class="rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4">
            <p class="text-sm text-emerald-300 font-semibold">✓ Parolă temporară generată</p>
            <p class="text-xs text-gray-400 mt-1">Pentru contul <span class="text-gray-200">{{ email }}</span>:</p>
            <div class="flex items-center gap-2 mt-3">
              <code class="flex-1 bg-[#0a0a0a] border border-white/10 rounded-lg px-3 py-2.5 text-base font-mono text-[#7ee0b0] tracking-wide select-all">{{ parolaTemporara }}</code>
              <button @click="copiaza"
                      class="shrink-0 border border-white/15 text-gray-300 hover:text-[#42b883] hover:border-[#42b883]/50 rounded-lg px-3 py-2.5 text-sm transition-all">
                {{ parolaCopiata ? '✓ copiat' : 'copiază' }}
              </button>
            </div>
            <p class="text-[11px] text-amber-400/90 mt-3">
              ⚠ Notează-o acum — nu o mai putem afișa din nou. După autentificare, schimb-o din contul tău (Profil → schimbă parola).
            </p>
          </div>
          <button @click="mergiLaLogin"
                  class="w-full bg-[#42b883] hover:bg-[#3aa876] text-black font-bold py-2.5 rounded-xl text-sm transition-all mt-4">
            Continuă spre autentificare →
          </button>
        </div>

        <!-- Formularul (login / înregistrare / cerere resetare) -->
        <form v-else @submit.prevent="trimite" class="space-y-4">
          <div v-if="mod === 'inregistrare'">
            <label class="text-xs text-gray-400 block mb-1.5">Nume complet</label>
            <input v-model="nume" type="text" required placeholder="Ana Popescu"
                   class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:border-[#42b883]/60 focus:outline-none transition-colors" />
          </div>
          <div>
            <label class="text-xs text-gray-400 block mb-1.5">Email</label>
            <input v-model="email" type="email" required placeholder="ana@exemplu.ro"
                   class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:border-[#42b883]/60 focus:outline-none transition-colors" />
          </div>
          <div v-if="mod !== 'reset'">
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs text-gray-400">Parolă</label>
              <button v-if="mod === 'login'" type="button" @click="schimbaMod('reset')"
                      class="text-xs text-[#42b883] hover:text-[#5fd0a0] transition-colors">Ai uitat parola?</button>
            </div>
            <input v-model="parola" type="password" required placeholder="••••••••"
                   class="w-full bg-[#0a0a0a] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-600 focus:border-[#42b883]/60 focus:outline-none transition-colors" />
            <p v-if="mod === 'inregistrare'" class="text-[11px] text-gray-600 mt-1.5">
              Minim 8 caractere, literă mare, literă mică, cifră și caracter special.
            </p>
          </div>

          <p v-if="eroare" class="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">{{ eroare }}</p>
          <p v-if="mesaj" class="text-sm text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">{{ mesaj }}</p>

          <button type="submit" :disabled="seTrimite"
                  class="w-full bg-[#42b883] hover:bg-[#3aa876] disabled:opacity-50 text-black font-bold py-2.5 rounded-xl text-sm transition-all">
            {{ seTrimite ? 'Se procesează…'
              : mod === 'login' ? 'Intră în cont'
              : mod === 'inregistrare' ? 'Creează contul'
              : 'Trimite-mi o parolă temporară' }}
          </button>
        </form>
      </div>

      <p class="text-center text-xs text-gray-600 mt-5">
        Demo: student@codespace.ro / Student123! · profesor@codespace.ro / Profesor123!
      </p>
    </div>
  </div>
</template>
