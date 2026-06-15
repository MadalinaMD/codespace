// Clientul HTTP central: bază comună, token automat, deconectare la 401.
import axios from 'axios'

export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: API_URL })

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (raspuns) => raspuns,
  (eroare) => {
    if (eroare.response?.status === 401 && !eroare.config?.url?.includes('/auth/login')) {
      // Token expirat sau invalid: curățăm sesiunea și revenim la login
      localStorage.removeItem('token')
      localStorage.removeItem('utilizator')
      if (window.location.pathname !== '/login') window.location.href = '/login'
    }
    return Promise.reject(eroare)
  },
)

// Extrage un mesaj de eroare lizibil din orice răspuns (inclusiv validări 422)
export function mesajEroare(eroare, implicit = 'A apărut o eroare. Încearcă din nou.') {
  const detaliu = eroare?.response?.data?.detail
  if (Array.isArray(detaliu)) {
    return detaliu.map((d) => (d.msg || '').replace(/^Value error,?\s*/i, '')).join(' ')
  }
  if (typeof detaliu === 'string') return detaliu
  return implicit
}

export default client
