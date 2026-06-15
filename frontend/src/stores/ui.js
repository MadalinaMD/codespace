// Notificări efemere (toast-uri): realizări deblocate, XP câștigat, erori.
import { defineStore } from 'pinia'

let urmatorulId = 1

export const useUi = defineStore('ui', {
  state: () => ({ toasturi: [] }),
  actions: {
    toast(mesaj, tip = 'info', icon = '') {
      const id = urmatorulId++
      this.toasturi.push({ id, mesaj, tip, icon })
      setTimeout(() => this.inchide(id), 4000)
    },
    inchide(id) {
      this.toasturi = this.toasturi.filter((t) => t.id !== id)
    },
    // Folosit după orice acțiune care poate debloca realizări / acorda XP
    anuntaRezultate({ realizari_noi = [], xp_castigat = 0 } = {}) {
      if (xp_castigat > 0) this.toast(`+${xp_castigat} XP`, 'xp', '✨')
      for (const realizare of realizari_noi) {
        this.toast(`Realizare deblocată: ${realizare.titlu}`, 'realizare', realizare.icon)
      }
    },
  },
})
