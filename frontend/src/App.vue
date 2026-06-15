<script setup>
// Shell-ul aplicației: bara laterală de navigație + conținutul rutei active.
// Un SINGUR router-view, mereu montat — bara laterală apare doar autentificat
// (două router-view-uri în ramuri v-if separate ar crea o cursă la login).
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/stores/auth'
import ToastStack from '@/components/ToastStack.vue'

const auth = useAuth()
const route = useRoute()

const meniu = computed(() => {
  const baza = [
    { nume: 'Acasă', ruta: '/', icon: '🏠' },
    { nume: 'Curs', ruta: '/curs', icon: '📚' },
    { nume: 'Recapitulare', ruta: '/recapitulare', icon: '🔁' },
    { nume: 'Test adaptiv', ruta: '/test-adaptiv', icon: '🎯' },
    { nume: 'Tutore AI', ruta: '/tutore', icon: '💬' },
    { nume: 'Playground', ruta: '/playground', icon: '⚡' },
    { nume: 'Clasament', ruta: '/clasament', icon: '🏆' },
    { nume: 'Profil', ruta: '/profil', icon: '👤' },
  ]
  if (auth.esteProfesor) baza.push({ nume: 'Panou profesor', ruta: '/profesor', icon: '🎓' })
  return baza
})

const esteActiv = (ruta) =>
  ruta === '/' ? route.path === '/' : route.path.startsWith(ruta)
</script>

<template>
  <div class="min-h-screen">
    <!-- Bara laterală: doar pentru utilizatori autentificați -->
    <aside v-if="auth.esteLogat"
           class="w-60 border-r border-white/10 bg-[#0d0d0d] flex flex-col fixed inset-y-0 z-10">
      <router-link to="/" class="flex items-center gap-2.5 px-5 h-16 border-b border-white/10">
        <span class="w-8 h-8 rounded-lg bg-[#42b883] text-black font-black grid place-items-center text-base">C</span>
        <span class="font-bold text-white tracking-tight text-lg">CodeSpace</span>
      </router-link>

      <nav class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
        <router-link v-for="element in meniu" :key="element.ruta" :to="element.ruta"
                     class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all"
                     :class="esteActiv(element.ruta)
                       ? 'bg-[#42b883]/15 text-[#42b883] font-semibold'
                       : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'">
          <span class="text-base">{{ element.icon }}</span>
          {{ element.nume }}
        </router-link>
      </nav>

      <div class="p-4 border-t border-white/10">
        <p class="text-sm text-white font-medium truncate">{{ auth.nume }}</p>
        <p class="text-xs text-gray-500 capitalize">{{ auth.utilizator?.rol }}</p>
        <button @click="auth.logout(); $router.push('/login')"
                class="mt-3 w-full text-xs text-gray-400 hover:text-red-400 border border-white/10 hover:border-red-500/40 rounded-lg py-2 transition-all">
          Deconectare
        </button>
      </div>
    </aside>

    <main :class="auth.esteLogat ? 'ml-60' : ''" class="min-h-screen">
      <router-view />
    </main>

    <ToastStack />
  </div>
</template>
