// Vizualizatorul de execuție: trasează programul Python LINIE CU LINIE în
// Pyodide (sys.settrace) și întoarce o cronologie de pași — linia activă,
// variabilele din fiecare moment, adâncimea apelurilor, output-ul progresiv.
// Inspirat de Python Tutor (Philip Guo), implementat integral în browser.
import { incarcaPyodide } from './pyodide'

const MAX_PASI = 400

function construiesteScript(cod, stdin) {
  return `
import sys as _sys, io as _io, json as _json, builtins as _b

_COD = ${JSON.stringify(cod)}
_STDIN = ${JSON.stringify(stdin || '')}
_MAX = ${MAX_PASI}

_pasii = []
_stdout = _io.StringIO()
_eroare = None
_trunchiat = False

class _Scriitor:
    def write(self, s):
        _stdout.write(s)
        return len(s)
    def flush(self):
        pass

def _scurt(v):
    try:
        r = repr(v)
    except Exception:
        r = "<valoare neafișabilă>"
    return r if len(r) <= 80 else r[:77] + "…"

_TIPURI_ASCUNSE = ("module", "function", "builtin_function_or_method",
                   "type", "method", "classmethod", "staticmethod")

def _variabile(spatiu):
    rezultat = {}
    for nume, valoare in spatiu.items():
        if nume.startswith("_"):
            continue
        if type(valoare).__name__ in _TIPURI_ASCUNSE:
            continue
        rezultat[nume] = _scurt(valoare)
    return rezultat

def _adancime(frame):
    nivel = 0
    f = frame
    while f is not None:
        if f.f_code.co_filename == "<cod>":
            nivel += 1
        f = f.f_back
    return nivel

class _PreaMultiPasi(Exception):
    pass

def _urmareste(frame, eveniment, arg):
    if frame.f_code.co_filename != "<cod>":
        return None
    if eveniment in ("line", "return", "exception"):
        if len(_pasii) >= _MAX:
            raise _PreaMultiPasi()
        in_functie = frame.f_code.co_name != "<module>"
        pas = {
            "linie": frame.f_lineno,
            "eveniment": eveniment,
            "functie": frame.f_code.co_name if in_functie else None,
            "adancime": _adancime(frame),
            "globale": _variabile(frame.f_globals),
            "locale": _variabile(frame.f_locals) if in_functie else None,
            "stdout_len": _stdout.tell(),
        }
        if eveniment == "return":
            pas["retur"] = _scurt(arg)
        if eveniment == "exception" and isinstance(arg, tuple):
            pas["exceptie"] = arg[0].__name__ + ": " + str(arg[1])[:120]
        _pasii.append(pas)
    return _urmareste

_intrare = _io.StringIO(_STDIN)
_input_vechi = _b.input
def _input_nou(prompt=""):
    if prompt:
        _stdout.write(str(prompt))
    linie = _intrare.readline()
    if not linie:
        raise EOFError("input(): nu mai există date de intrare")
    return linie.rstrip("\\n")
_b.input = _input_nou

_stdout_vechi = _sys.stdout
_sys.stdout = _Scriitor()
try:
    _compilat = compile(_COD, "<cod>", "exec")
    _sys.settrace(_urmareste)
    exec(_compilat, {"__name__": "__main__"})
except _PreaMultiPasi:
    _trunchiat = True
except SyntaxError as e:
    _eroare = f"SyntaxError: {e.msg} (linia {e.lineno})"
except BaseException as e:
    _eroare = type(e).__name__ + ": " + str(e)[:200]
finally:
    _sys.settrace(None)
    _sys.stdout = _stdout_vechi
    _b.input = _input_vechi

_json.dumps({
    "pasi": _pasii,
    "stdout": _stdout.getvalue()[:5000],
    "eroare": _eroare,
    "trunchiat": _trunchiat,
})
`
}

// Trasează codul; întoarce {pasi, stdout, eroare, trunchiat}.
export async function traseazaCod(cod, stdin = '') {
  const py = await incarcaPyodide()
  const brut = await py.runPythonAsync(construiesteScript(cod, stdin))
  return JSON.parse(brut)
}

export { MAX_PASI }
