// Pyodide: interpretorul Python compilat în WebAssembly, încărcat o singură dată.
// Browserul este sandbox-ul: codul studentului nu atinge nici serverul, nici
// sistemul de fișiere real — execuția locală e instantanee și gratuită.
const VERSIUNE = 'v0.26.4'
const CDN = `https://cdn.jsdelivr.net/pyodide/${VERSIUNE}/full/`

let promisiune = null

export function incarcaPyodide() {
  if (promisiune) return promisiune
  promisiune = new Promise((rezolva, respinge) => {
    const porneste = () =>
      window.loadPyodide({ indexURL: CDN }).then(rezolva).catch(respinge)
    if (window.loadPyodide) return porneste()
    const script = document.createElement('script')
    script.src = `${CDN}pyodide.js`
    script.onload = porneste
    script.onerror = () =>
      respinge(new Error('Python nu s-a putut încărca — verifică conexiunea la internet.'))
    document.head.appendChild(script)
  })
  return promisiune
}

export function pyodideEsteGata() {
  return promisiune !== null
}

// Rulare simplă (playground): capturează stdout/stderr, întoarce textul.
export async function ruleazaCod(cod) {
  const py = await incarcaPyodide()
  let iesire = ''
  py.setStdout({ batched: (linie) => { iesire += linie + '\n' } })
  py.setStderr({ batched: (linie) => { iesire += linie + '\n' } })
  try {
    await py.runPythonAsync(cod)
    return { ok: true, iesire: iesire.trimEnd() }
  } catch (eroare) {
    return { ok: false, iesire: (iesire + String(eroare?.message || eroare)).trim() }
  }
}
