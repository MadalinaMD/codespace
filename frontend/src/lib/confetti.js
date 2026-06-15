// Confetti minimalist pe canvas — micro-celebrare la reușite (fără dependențe).
const CULORI = ['#42b883', '#fbbf24', '#60a5fa', '#f87171', '#c084fc', '#ffffff']

export function confetti(numarParticule = 130) {
  const panza = document.createElement('canvas')
  panza.style.cssText = 'position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:9999'
  panza.width = window.innerWidth
  panza.height = window.innerHeight
  document.body.appendChild(panza)
  const context = panza.getContext('2d')

  const particule = Array.from({ length: numarParticule }, () => ({
    x: panza.width / 2 + (Math.random() - 0.5) * 200,
    y: panza.height * 0.35,
    vx: (Math.random() - 0.5) * 14,
    vy: -Math.random() * 13 - 4,
    marime: Math.random() * 7 + 4,
    culoare: CULORI[Math.floor(Math.random() * CULORI.length)],
    rotatie: Math.random() * Math.PI,
    vRotatie: (Math.random() - 0.5) * 0.3,
  }))

  const start = performance.now()
  const DURATA = 1600

  function deseneaza(acum) {
    const progres = (acum - start) / DURATA
    context.clearRect(0, 0, panza.width, panza.height)
    if (progres >= 1) {
      panza.remove()
      return
    }
    for (const p of particule) {
      p.x += p.vx
      p.y += p.vy
      p.vy += 0.45 // gravitație
      p.rotatie += p.vRotatie
      context.save()
      context.translate(p.x, p.y)
      context.rotate(p.rotatie)
      context.globalAlpha = Math.max(0, 1 - progres * 1.15)
      context.fillStyle = p.culoare
      context.fillRect(-p.marime / 2, -p.marime / 2, p.marime, p.marime * 0.6)
      context.restore()
    }
    requestAnimationFrame(deseneaza)
  }
  requestAnimationFrame(deseneaza)
}
