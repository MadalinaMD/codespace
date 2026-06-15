"""Evaluatorul de cod: rulează soluțiile studenților izolat și le notează pe teste.

Apărare pe straturi (defense in depth):
1. Execuția PRIMARĂ are loc în browser (Pyodide/WebAssembly) — serverul nu e expus.
2. La trimiterea oficială, serverul re-verifică codul:
   a. analiză statică AST: doar module din lista permisă, fără funcții de sistem
      (open, exec, eval, __import__ ...) și fără atribute interne periculoase;
   b. execuție într-un proces SEPARAT pornit cu `python -I` (mod izolat: fără
      site-packages, fără variabile de mediu), cu timeout dur și ieșire limitată.

Formatul testelor (vizibile studentului):
- mod "functie": {"apel": "suma_pare([1, 2, 3, 4])", "asteptat": "6"}
  → se evaluează apelul și se compară valoarea cu literalul așteptat
- mod "program": {"stdin": "5\\n", "asteptat": "120"}
  → programul rulează cu intrarea dată, se compară stdout-ul normalizat
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

from app import config
from app.engine import errors

MARCAJ = "===CODESPACE_REZULTATE==="

# Funcții interzise în soluții (nu sunt necesare exercițiilor; reduc suprafața de atac)
NUME_INTERZISE = {
    "exec", "eval", "compile", "__import__", "open",
    "globals", "locals", "vars", "breakpoint", "exit", "quit",
}
# Atribute interne prin care s-ar putea evada din mediul restrâns
ATRIBUTE_INTERZISE = {
    "__globals__", "__builtins__", "__subclasses__", "__bases__", "__mro__",
    "__code__", "__closure__", "__getattribute__", "__reduce__", "__reduce_ex__",
    "__import__", "__loader__", "__spec__",
}


@dataclass
class RezultatRulare:
    status: str                      # acceptat | teste_esuate | eroare | timeout | blocat
    teste_total: int = 0
    teste_trecute: int = 0
    rezultate: list = field(default_factory=list)
    eroare_categorie: str | None = None
    eroare_mesaj: str | None = None


# ── 1. Analiza statică (AST) ────────────────────────────────────
def verifica_ast(cod: str) -> tuple[str | None, str | None]:
    """Returnează (categorie, mesaj) dacă codul încalcă regulile, altfel (None, None)."""
    try:
        arbore = ast.parse(cod)
    except SyntaxError:
        # Sintaxa greșită nu e o problemă de securitate: o raportează execuția,
        # cu mesajul complet al interpretorului.
        return None, None

    for nod in ast.walk(arbore):
        if isinstance(nod, ast.Import):
            for alias in nod.names:
                radacina = alias.name.split(".")[0]
                if radacina not in config.MODULE_PERMISE:
                    return "import_blocat", f"Modulul „{radacina}” nu este permis în exerciții."
        elif isinstance(nod, ast.ImportFrom):
            radacina = (nod.module or "").split(".")[0]
            if nod.level != 0 or radacina not in config.MODULE_PERMISE:
                return "import_blocat", f"Modulul „{radacina or '.'}” nu este permis în exerciții."
        elif isinstance(nod, ast.Name) and nod.id in NUME_INTERZISE:
            return "cod_periculos", f"Funcția „{nod.id}” nu este permisă în exerciții."
        elif isinstance(nod, ast.Attribute) and nod.attr in ATRIBUTE_INTERZISE:
            return "cod_periculos", f"Atributul „{nod.attr}” nu este permis în exerciții."
    return None, None


# ── 2. Harness-ul de testare (script de sine stătător) ──────────
_SABLON_HARNESS = '''
import ast as _ast, io as _io, json as _json, sys as _sys, traceback as _tb

_COD = {cod_json}
_TESTE = {teste_json}
_MOD = {mod_json}
_LIMITA = {limita_iesire}

class _IesireLimitata(_io.StringIO):
    def write(self, s):
        if self.tell() > _LIMITA:
            raise RuntimeError("Programul a afișat prea mult text (posibilă buclă infinită).")
        return super().write(s)

def _egal(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b or a == b and type(a) == type(b)
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return type(a) == type(b) and len(a) == len(b) and all(_egal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return set(a) == set(b) and all(_egal(a[k], b[k]) for k in a)
    return a == b

def _normalizeaza(text):
    linii = [l.rstrip() for l in (text or "").strip().splitlines()]
    return "\\n".join(linii)

def _scurt(val):
    r = repr(val)
    return r if len(r) <= 300 else r[:300] + "…"

_rezultate = []
_eroare_globala = None
_stdout_real = _sys.stdout

try:
    _compilat = compile(_COD, "<solutia_ta>", "exec")
except SyntaxError as e:
    _eroare_globala = {{"tip": type(e).__name__, "mesaj": str(e), "linie": e.lineno}}
    _compilat = None

if _compilat is not None and _MOD == "functie":
    _ns = {{"__name__": "__main__"}}
    _sys.stdout = _IesireLimitata()
    try:
        exec(_compilat, _ns)
    except Exception as e:
        _tbe = _tb.extract_tb(e.__traceback__)
        _linie = next((f.lineno for f in reversed(_tbe) if f.filename == "<solutia_ta>"), None)
        _eroare_globala = {{"tip": type(e).__name__, "mesaj": str(e), "linie": _linie}}
    finally:
        _sys.stdout = _stdout_real
    if _eroare_globala is None:
        for _t in _TESTE:
            _err_dorit = _t.get("eroare")
            _eticheta = "ridică " + _err_dorit if _err_dorit else _t.get("asteptat")
            _sys.stdout = _IesireLimitata()
            try:
                _obtinut = eval(_t["apel"], _ns)
                if _err_dorit:
                    _rezultate.append({{
                        "descriere": _t["apel"], "asteptat": _eticheta,
                        "obtinut": _scurt(_obtinut), "trecut": False, "eroare": None,
                    }})
                else:
                    _asteptat = _ast.literal_eval(_t["asteptat"])
                    _rezultate.append({{
                        "descriere": _t["apel"], "asteptat": _t["asteptat"],
                        "obtinut": _scurt(_obtinut), "trecut": _egal(_obtinut, _asteptat),
                        "eroare": None,
                    }})
            except Exception as e:
                if _err_dorit and type(e).__name__ == _err_dorit:
                    _rezultate.append({{
                        "descriere": _t["apel"], "asteptat": _eticheta,
                        "obtinut": "ridică " + type(e).__name__, "trecut": True, "eroare": None,
                    }})
                else:
                    _rezultate.append({{
                        "descriere": _t["apel"], "asteptat": _eticheta,
                        "obtinut": None, "trecut": False,
                        "eroare": {{"tip": type(e).__name__, "mesaj": str(e)}},
                    }})
            finally:
                _sys.stdout = _stdout_real

if _compilat is not None and _MOD == "program":
    for _t in _TESTE:
        _ns = {{"__name__": "__main__"}}
        _sys.stdin = _io.StringIO(_t.get("stdin") or "")
        _captura = _IesireLimitata()
        _sys.stdout = _captura
        _er = None
        try:
            exec(_compilat, _ns)
        except SystemExit:
            pass
        except Exception as e:
            _tbe = _tb.extract_tb(e.__traceback__)
            _linie = next((f.lineno for f in reversed(_tbe) if f.filename == "<solutia_ta>"), None)
            _er = {{"tip": type(e).__name__, "mesaj": str(e), "linie": _linie}}
        finally:
            _sys.stdout = _stdout_real
        _obtinut = _captura.getvalue()
        _rezultate.append({{
            "descriere": "intrare: " + repr(_t.get("stdin") or "(fără)"),
            "asteptat": _t["asteptat"],
            "obtinut": _obtinut[:1000],
            "trecut": _er is None and _normalizeaza(_obtinut) == _normalizeaza(_t["asteptat"]),
            "eroare": _er,
        }})

print(MARCAJ_FINAL)
print(_json.dumps({{"rezultate": _rezultate, "eroare_globala": _eroare_globala}}))
'''


def construieste_harness(cod: str, teste: list[dict], mod: str) -> str:
    """Generează scriptul de testare; codul și testele intră serializate JSON,
    deci nu pot „evada” din șablonul harness-ului."""
    script = _SABLON_HARNESS.format(
        cod_json=json.dumps(cod),
        teste_json=json.dumps(teste),
        mod_json=json.dumps(mod),
        limita_iesire=config.SANDBOX_MAX_OUTPUT,
    )
    return script.replace("MARCAJ_FINAL", json.dumps(MARCAJ))


# ── 3. Execuția izolată + interpretarea rezultatelor ────────────
def ruleaza_teste(cod: str, teste: list[dict], mod: str = "functie",
                  timeout_s: int = config.SANDBOX_TIMEOUT_S) -> RezultatRulare:
    """Pipeline-ul complet: AST → proces izolat → rezultate structurate."""
    total = len(teste)

    categorie, mesaj = verifica_ast(cod)
    if categorie:
        return RezultatRulare(status="blocat", teste_total=total,
                              eroare_categorie=categorie, eroare_mesaj=mesaj)

    harness = construieste_harness(cod, teste, mod)
    cale = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write(harness)
            cale = f.name
        # -I: mod izolat (fără site-packages și fără variabile de mediu Python)
        # -X utf8: ieșire UTF-8 indiferent de codarea consolei Windows
        proces = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", cale],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout_s,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except subprocess.TimeoutExpired:
        return RezultatRulare(status="timeout", teste_total=total,
                              eroare_categorie="bucla_infinita",
                              eroare_mesaj=f"Execuția a depășit {timeout_s} secunde.")
    finally:
        if cale and os.path.exists(cale):
            try:
                os.unlink(cale)
            except OSError:
                pass

    if MARCAJ not in (proces.stdout or ""):
        # Procesul a murit înainte să raporteze (ex. memorie epuizată)
        coada_stderr = (proces.stderr or "").strip().splitlines()[-3:]
        return RezultatRulare(status="eroare", teste_total=total,
                              eroare_categorie="alta_eroare",
                              eroare_mesaj="\n".join(coada_stderr) or "Procesul s-a oprit neașteptat.")

    raport_brut = proces.stdout.split(MARCAJ, 1)[1].strip()
    try:
        raport = json.loads(raport_brut)
    except json.JSONDecodeError:
        return RezultatRulare(status="eroare", teste_total=total,
                              eroare_categorie="alta_eroare",
                              eroare_mesaj="Raportul de testare nu a putut fi citit.")

    if raport.get("eroare_globala"):
        eg = raport["eroare_globala"]
        categorie = errors.clasifica_exceptie(eg.get("tip", ""))
        mesaj = f"{eg.get('tip')}: {eg.get('mesaj')}"
        if eg.get("linie"):
            mesaj += f" (linia {eg['linie']})"
        return RezultatRulare(status="eroare", teste_total=total,
                              eroare_categorie=categorie, eroare_mesaj=mesaj)

    rezultate = raport.get("rezultate", [])
    trecute = sum(1 for r in rezultate if r.get("trecut"))
    if trecute == total and total > 0:
        return RezultatRulare(status="acceptat", teste_total=total,
                              teste_trecute=trecute, rezultate=rezultate)

    # Categoria erorii: prima excepție per-test, altfel "răspuns greșit"
    categorie = "raspuns_gresit"
    mesaj = None
    for r in rezultate:
        if r.get("eroare"):
            categorie = errors.clasifica_exceptie(r["eroare"].get("tip", ""))
            mesaj = f"{r['eroare'].get('tip')}: {r['eroare'].get('mesaj')}"
            break
    return RezultatRulare(status="teste_esuate", teste_total=total,
                          teste_trecute=trecute, rezultate=rezultate,
                          eroare_categorie=categorie, eroare_mesaj=mesaj)


def teste_din_model(teste_orm) -> list[dict]:
    """Convertește rândurile TestExercitiu în formatul așteptat de harness."""
    rezultat = []
    for t in teste_orm:
        if t.apel and t.asteptat_eroare:
            rezultat.append({"apel": t.apel, "eroare": t.asteptat_eroare})
        elif t.apel:
            rezultat.append({"apel": t.apel, "asteptat": t.asteptat})
        else:
            rezultat.append({"stdin": t.stdin or "", "asteptat": t.asteptat})
    return rezultat
