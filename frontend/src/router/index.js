// Rutele aplicației + gardurile de acces (autentificare, rol de profesor).
import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/stores/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('@/pages/LoginPage.vue'),
    meta: { public: true } },
  { path: '/', name: 'dashboard', component: () => import('@/pages/DashboardPage.vue') },
  { path: '/curs', name: 'curs', component: () => import('@/pages/CursPage.vue') },
  { path: '/lectii/:slug', name: 'lectie', component: () => import('@/pages/LectiePage.vue') },
  { path: '/exercitii/:id', name: 'exercitiu', component: () => import('@/pages/ExercitiuPage.vue') },
  { path: '/quiz/:capitolSlug', name: 'quiz', component: () => import('@/pages/QuizPage.vue') },
  { path: '/recapitulare', name: 'recapitulare', component: () => import('@/pages/RecapitularePage.vue') },
  { path: '/test-adaptiv', name: 'test-adaptiv', component: () => import('@/pages/TestAdaptivPage.vue') },
  { path: '/plasament', name: 'plasament', component: () => import('@/pages/PlasamentPage.vue') },
  { path: '/tutore', name: 'tutore', component: () => import('@/pages/TutorePage.vue') },
  { path: '/playground', name: 'playground', component: () => import('@/pages/PlaygroundPage.vue') },
  { path: '/profil', name: 'profil', component: () => import('@/pages/ProfilPage.vue') },
  { path: '/clasament', name: 'clasament', component: () => import('@/pages/ClasamentPage.vue') },
  { path: '/profesor', name: 'profesor', component: () => import('@/pages/ProfesorPage.vue'),
    meta: { rol: 'profesor' } },
  { path: '/:catchAll(.*)', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  const auth = useAuth()
  if (!to.meta.public && !auth.esteLogat) return { name: 'login' }
  if (to.name === 'login' && auth.esteLogat) return { name: 'dashboard' }
  if (to.meta.rol === 'profesor' && !auth.esteProfesor) return { name: 'dashboard' }
  return true
})

export default router
