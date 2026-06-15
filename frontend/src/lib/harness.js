// Harness-ul de teste din browser: oglindește logica evaluatorului de pe server,
// dar rulează instant în Pyodide. Verdictul OFICIAL rămâne al serverului — aici
// studentul primește feedback imediat, gratuit, fără să consume nimic.
import { incarcaPyodide } from './pyodide'

function construiesteScript(cod, teste, mod) {
  // JSON.stringify produce literali compatibili cu sintaxa Python pentru șiruri;
  // testele trec prin json.loads ca să devină structuri Python.
  return `
import ast as _ast, io as _io, json as _json, sys as _sys, traceback as _tb, builtins as _b

_COD = ${JSON.stringify(cod)}
_TESTE = _json.loads(${JSON.stringify(JSON.stringify(teste))})
_MOD = ${JSON.stringify(mod)}

def _egal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or (a == b and type(a) == type(b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return type(a) == type(b) and len(a) == len(b) and all(_egal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_egal(a[k], b[k]) for k in a)
    return a == b

def _normalizeaza(text):
    return "\\n".join(l.rstrip() for l in (text or "").strip().splitlines())

def _scurt(v):
    r = repr(v)
    return r if len(r) <= 300 else r[:300] + "…"

_rezultate = []
_eroare_globala = None

try:
    _compilat = compile(_COD, "<solutia_ta>", "exec")
except SyntaxError as e:
    _eroare_globala = {"tip": type(e).__name__, "mesaj": str(e), "linie": e.lineno}
    _compilat = None

if _compilat is not None and _MOD == "functie":
    _ns = {"__name__": "__main__"}
    _stdout_vechi = _sys.stdout
    _sys.stdout = _io.StringIO()
    try:
        exec(_compilat, _ns)
    except Exception as e:
        _tbe = _tb.extract_tb(e.__traceback__)
        _linie = next((f.lineno for f in reversed(_tbe) if f.filename == "<solutia_ta>"), None)
        _eroare_globala = {"tip": type(e).__name__, "mesaj": str(e), "linie": _linie}
    finally:
        _sys.stdout = _stdout_vechi
    if _eroare_globala is None:
        for _t in _TESTE:
            _err_dorit = _t.get("eroare")
            _eticheta = ("ridică " + _err_dorit) if _err_dorit else _t.get("asteptat")
            _sys.stdout = _io.StringIO()
            try:
                _obtinut = eval(_t["apel"], _ns)
                if _err_dorit:
                    _rezultate.append({"descriere": _t["apel"], "asteptat": _eticheta,
                                       "obtinut": _scurt(_obtinut), "trecut": False, "eroare": None})
                else:
                    _asteptat = _ast.literal_eval(_t["asteptat"])
                    _rezultate.append({"descriere": _t["apel"], "asteptat": _t["asteptat"],
                                       "obtinut": _scurt(_obtinut),
                                       "trecut": _egal(_obtinut, _asteptat), "eroare": None})
            except Exception as e:
                if _err_dorit and type(e).__name__ == _err_dorit:
                    _rezultate.append({"descriere": _t["apel"], "asteptat": _eticheta,
                                       "obtinut": "ridică " + type(e).__name__,
                                       "trecut": True, "eroare": None})
                else:
                    _rezultate.append({"descriere": _t["apel"], "asteptat": _eticheta,
                                       "obtinut": None, "trecut": False,
                                       "eroare": {"tip": type(e).__name__, "mesaj": str(e)}})
            finally:
                _sys.stdout = _stdout_vechi

if _compilat is not None and _MOD == "program":
    _input_vechi = _b.input
    for _t in _TESTE:
        _linii = _io.StringIO(_t.get("stdin") or "")
        _b.input = lambda prompt="": _linii.readline().rstrip("\\n")
        _captura = _io.StringIO()
        _stdout_vechi = _sys.stdout
        _sys.stdout = _captura
        _er = None
        _ns = {"__name__": "__main__"}
        try:
            exec(_compilat, _ns)
        except SystemExit:
            pass
        except Exception as e:
            _tbe = _tb.extract_tb(e.__traceback__)
            _linie = next((f.lineno for f in reversed(_tbe) if f.filename == "<solutia_ta>"), None)
            _er = {"tip": type(e).__name__, "mesaj": str(e), "linie": _linie}
        finally:
            _sys.stdout = _stdout_vechi
            _b.input = _input_vechi
        _obtinut = _captura.getvalue()
        _rezultate.append({
            "descriere": "intrare: " + repr(_t.get("stdin") or "(fără)"),
            "asteptat": _t["asteptat"], "obtinut": _obtinut[:1000],
            "trecut": _er is None and _normalizeaza(_obtinut) == _normalizeaza(_t["asteptat"]),
            "eroare": _er,
        })

_json.dumps({"rezultate": _rezultate, "eroare_globala": _eroare_globala})
`
}

// Rulează testele unui exercițiu în browser; întoarce aceeași structură ca serverul.
export async function ruleazaTesteLocal(cod, teste, mod) {
  const py = await incarcaPyodide()
  const brut = await py.runPythonAsync(construiesteScript(cod, teste, mod))
  const raport = JSON.parse(brut)
  const trecute = raport.rezultate.filter((r) => r.trecut).length
  let status = 'teste_esuate'
  if (raport.eroare_globala) status = 'eroare'
  else if (trecute === teste.length && teste.length > 0) status = 'acceptat'
  return {
    status,
    teste_total: teste.length,
    teste_trecute: trecute,
    rezultate: raport.rezultate,
    eroare_globala: raport.eroare_globala,
  }
}
