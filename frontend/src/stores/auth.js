// Sesiunea utilizatorului: token JWT + datele de profil.
import { defineStore } from 'pinia'
import client from '@/api/client'

export const useAuth = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    utilizator: JSON.parse(localStorage.getItem('utilizator') || 'null'),
  }),
  getters: {
    esteLogat: (state) => Boolean(state.token),
    esteProfesor: (state) => state.utilizator?.rol === 'profesor',
    nume: (state) => state.utilizator?.nume || '',
  },
  actions: {
    async login(email, parola) {
      const { data } = await client.post('/auth/login', { email, parola })
      this.token = data.token
      this.utilizator = { nume: data.nume, email: data.email, rol: data.rol }
      localStorage.setItem('token', data.token)
      localStorage.setItem('utilizator', JSON.stringify(this.utilizator))
    },
    async inregistrare(nume, email, parola) {
      await client.post('/auth/inregistrare', { nume, email, parola })
    },
    logout() {
      this.token = ''
      this.utilizator = null
      localStorage.removeItem('token')
      localStorage.removeItem('utilizator')
    },
  },
})
