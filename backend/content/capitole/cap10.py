# -*- coding: utf-8 -*-
"""Capitolul 10 — Erori și excepții.
Adaptat după The Python Tutorial §8 „Errors and Exceptions” și Think Python cap. 14 (Appendix A)."""

SURSA = "Python Software Foundation, The Python Tutorial — §8 „Errors and Exceptions”; A. B. Downey, Think Python (ed. 2), Appendix A „Debugging”."

CAPITOL = {
    "slug": "exceptii",
    "titlu": "Erori și excepții",
    "descriere": "Programele robuste nu se prăbușesc la prima problemă: try/except, raise și validarea datelor.",
    "ordine": 10,
    "lectii": [
        {
            "slug": "try-except",
            "titlu": "try / except: tratarea erorilor",
            "ordine": 1,
            "concepte": ["exceptii"],
            "sursa": SURSA,
            "continut_md": """## Erori de sintaxă vs. excepții

- **Eroarea de sintaxă** apare ÎNAINTE de rulare: Python nici nu pornește
  programul (`SyntaxError`).
- **Excepția** apare ÎN TIMPUL rulării: codul e valid, dar o operație devine
  imposibilă — `int("abc")`, `10 / 0`, `lista[99]`.

Netratată, o excepție **oprește programul** și afișează un *traceback*.
Citește-l de jos în sus: ultima linie spune tipul și mesajul, cele de
deasupra arată drumul până la linia vinovată.

## try / except

Codul „riscant” se pune în `try`; reacția la eșec, în `except`:

```python
try:
    varsta = int(input())
    print(f"Anul viitor vei avea {varsta + 1} ani.")
except ValueError:
    print("Te rog introdu un număr!")
```

Dacă blocul `try` reușește, `except` e sărit. Dacă apare excepția numită,
execuția sare direct în `except` — programul **continuă**, nu moare.

## Prinde precis, nu cu plasa mare

```python
except ValueError:        # BINE: știi exact ce tratezi
except (ValueError, ZeroDivisionError):   # mai multe tipuri
except Exception:         # DE EVITAT: ascunde și erorile-surpriză
```

Un `except` prea larg maschează inclusiv greșelile tale de programare —
cele pe care AI VREA să le vezi.

## else și finally

```python
try:
    numar = int(text)
except ValueError:
    print("invalid")
else:
    print("conversie reușită:", numar)   # doar dacă NU a fost excepție
finally:
    print("se execută mereu")            # curățenie, indiferent de rezultat
```

## De reținut

- excepțiile sunt erori de RULARE; try/except le transformă în cazuri tratate;
- prinde tipul exact (`ValueError`, `KeyError`…);
- traceback-ul se citește de jos în sus.""",
            "cod_exemplu": """# Conversie sigură: programul nu moare la date invalide
texte = ["42", "abc", "7.5", "100"]

for text in texte:
    try:
        numar = int(text)
        print(f"{text!r} -> {numar}")
    except ValueError:
        print(f"{text!r} nu este un întreg valid")

# Mai multe tipuri de excepții
perechi = [(10, 2), (5, 0), (8, "x")]
for a, b in perechi:
    try:
        print(f"{a} / {b} =", a / b)
    except ZeroDivisionError:
        print(f"{a} / {b}: împărțire la zero!")
    except TypeError:
        print(f"{a} / {b}: tipuri incompatibile!")""",
            "exercitii": [
                {
                    "titlu": "Conversie sigură",
                    "enunt_md": """Definește funcția `intreg_sigur(text, implicit)` care încearcă să convertească
`text` la `int`. Dacă reușește, returnează numărul; dacă nu (orice
`ValueError`), returnează valoarea `implicit`.

*Exemple: `intreg_sigur("42", 0)` → `42`; `intreg_sigur("abc", 0)` → `0`.*""",
                    "cod_start": "def intreg_sigur(text, implicit):\n    pass\n",
                    "solutie": "def intreg_sigur(text, implicit):\n    try:\n        return int(text)\n    except ValueError:\n        return implicit\n",
                    "mod": "functie",
                    "functie_nume": "intreg_sigur",
                    "dificultate": 1,
                    "concepte": ["exceptii"],
                    "teste": [
                        {"apel": "intreg_sigur('42', 0)", "asteptat": "42"},
                        {"apel": "intreg_sigur('abc', 0)", "asteptat": "0"},
                        {"apel": "intreg_sigur('-7', 99)", "asteptat": "-7"},
                        {"apel": "intreg_sigur('3.5', -1)", "asteptat": "-1"},
                    ],
                },
                {
                    "titlu": "Împărțire fără surprize",
                    "enunt_md": """Definește funcția `imparte(a, b)` care returnează `a / b`, iar dacă `b` este
zero returnează `None` (în loc să lase programul să moară cu
`ZeroDivisionError`).""",
                    "cod_start": "def imparte(a, b):\n    pass\n",
                    "solutie": "def imparte(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None\n",
                    "mod": "functie",
                    "functie_nume": "imparte",
                    "dificultate": 1,
                    "concepte": ["exceptii"],
                    "teste": [
                        {"apel": "imparte(10, 2)", "asteptat": "5.0"},
                        {"apel": "imparte(7, 0)", "asteptat": "None"},
                        {"apel": "imparte(-9, 3)", "asteptat": "-3.0"},
                    ],
                },
            ],
        },
        {
            "slug": "raise-si-validare",
            "titlu": "raise: semnalarea datelor invalide",
            "ordine": 2,
            "concepte": ["ridicarea_exceptiilor"],
            "sursa": SURSA,
            "continut_md": """## Tu poți ridica excepții

Când funcția TA primește date fără sens, cel mai curat răspuns e să ridici
o excepție cu `raise`:

```python
def radacina(x):
    if x < 0:
        raise ValueError("Nu pot calcula radicalul unui număr negativ")
    return x ** 0.5
```

Mesajul ajunge la cel care a apelat greșit — exact ca erorile built-in pe
care le-ai întâlnit deja.

## De ce nu `return -1` sau `print`?

- `return -1` se confundă ușor cu un rezultat legitim și eroarea trece
  neobservată mai departe;
- `print` nu oprește calculul greșit — doar îl comentează;
- `raise` oprește imediat, numește problema și NU poate fi ignorat din
  greșeală. Apelantul decide: tratează cu `try/except` sau lasă programul
  să se oprească.

## Tiparul „validează devreme”

Verificările stau la **începutul** funcției — restul codului rămâne curat,
știind că datele sunt valide:

```python
def nota_finala(laborator, examen):
    if not (0 <= laborator <= 10 and 0 <= examen <= 10):
        raise ValueError("Notele trebuie să fie între 0 și 10")
    return round(0.4 * laborator + 0.6 * examen, 2)
```

## Alegerea tipului de excepție

- `ValueError` — tipul e bun, valoarea n-are sens (nota 15);
- `TypeError` — tipul însuși e greșit (text în loc de număr);
- pentru început, aceste două acoperă aproape tot.

## De reținut

- `raise ValueError("mesaj clar")` — semnalezi, nu ascunzi;
- validează la intrarea în funcție;
- excepțiile ridicate de tine se tratează cu try/except ca oricare altele.""",
            "cod_exemplu": """def nota_finala(laborator, examen):
    if not (0 <= laborator <= 10):
        raise ValueError(f"Notă de laborator invalidă: {laborator}")
    if not (0 <= examen <= 10):
        raise ValueError(f"Notă de examen invalidă: {examen}")
    return round(0.4 * laborator + 0.6 * examen, 2)

# Apel corect
print(nota_finala(9, 8))      # 8.4

# Apel greșit, tratat elegant de apelant
try:
    print(nota_finala(9, 15))
except ValueError as eroare:
    print("Eroare prinsă:", eroare)""",
            "exercitii": [
                {
                    "titlu": "Validarea vârstei",
                    "enunt_md": """Definește funcția `valideaza_varsta(varsta)` care:

- ridică `ValueError` cu mesajul exact `Varsta nu poate fi negativa` dacă
  `varsta < 0`;
- ridică `ValueError` cu mesajul exact `Varsta nu este realista` dacă
  `varsta > 130`;
- altfel returnează vârsta neschimbată.""",
                    "cod_start": "def valideaza_varsta(varsta):\n    pass\n",
                    "solutie": "def valideaza_varsta(varsta):\n    if varsta < 0:\n        raise ValueError(\"Varsta nu poate fi negativa\")\n    if varsta > 130:\n        raise ValueError(\"Varsta nu este realista\")\n    return varsta\n",
                    "mod": "functie",
                    "functie_nume": "valideaza_varsta",
                    "dificultate": 2,
                    "concepte": ["ridicarea_exceptiilor"],
                    "teste": [
                        {"apel": "valideaza_varsta(20)", "asteptat": "20"},
                        {"apel": "valideaza_varsta(0)", "asteptat": "0"},
                        {"apel": "valideaza_varsta(-5)", "eroare": "ValueError"},
                        {"apel": "valideaza_varsta(200)", "eroare": "ValueError"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Care e diferența dintre o eroare de sintaxă și o excepție?",
         "corecta": "sintaxa se verifică înainte de rulare; excepțiile apar în timpul rulării",
         "gresite": ["sunt sinonime", "excepțiile apar doar la import", "sintaxa apare doar în funcții"],
         "explicatie": "SyntaxError împiedică pornirea; excepțiile opresc un program pornit, dacă nu sunt tratate.",
         "concepte": ["exceptii"], "dificultate": 1},
        {"text": "Ce excepție ridică `int(\"abc\")`?", "corecta": "ValueError",
         "gresite": ["TypeError", "SyntaxError", "KeyError"],
         "explicatie": "Tipul argumentului (str) e acceptabil, dar valoarea nu poate fi convertită.",
         "concepte": ["exceptii"], "dificultate": 1},
        {"text": "Când se execută blocul `except`?",
         "corecta": "doar dacă în try apare excepția numită",
         "gresite": ["întotdeauna, după try", "doar dacă try reușește", "înaintea blocului try"],
         "explicatie": "except e planul de rezervă: rulează numai la excepția potrivită.",
         "concepte": ["exceptii"], "dificultate": 1},
        {"text": "De ce e descurajat `except Exception:` generic?",
         "corecta": "ascunde și erorile de programare pe care ai vrea să le vezi",
         "gresite": ["e mai lent", "nu compilează în Python 3", "prinde doar ValueError"],
         "explicatie": "Plasa prea largă maschează bug-uri reale; prinde exact ce știi să tratezi.",
         "concepte": ["exceptii"], "dificultate": 2},
        {"text": "Blocul `finally`…", "corecta": "se execută indiferent dacă a apărut sau nu excepția",
         "gresite": ["se execută doar la eroare", "se execută doar la succes", "oprește excepțiile"],
         "explicatie": "finally e pentru curățenie garantată (închidere de resurse etc.).",
         "concepte": ["exceptii"], "dificultate": 2},
        {"text": "Ce face instrucțiunea `raise ValueError(\"mesaj\")`?",
         "corecta": "oprește funcția semnalând o excepție cu mesajul dat",
         "gresite": ["afișează mesajul și continuă", "returnează mesajul", "definește un nou tip de eroare"],
         "explicatie": "raise aruncă excepția; execuția sare la cel mai apropiat except potrivit.",
         "concepte": ["ridicarea_exceptiilor"], "dificultate": 1},
        {"text": "De ce e `raise` mai bun decât `return -1` pentru date invalide?",
         "corecta": "eroarea nu poate fi confundată cu un rezultat legitim",
         "gresite": ["raise e mai rapid", "return -1 e eroare de sintaxă", "raise păstrează valoarea"],
         "explicatie": "-1 poate fi un rezultat valid în multe probleme; excepția e imposibil de ignorat accidental.",
         "concepte": ["ridicarea_exceptiilor"], "dificultate": 2},
        {"text": "Unde e cel mai bine plasată validarea argumentelor unei funcții?",
         "corecta": "la începutul funcției", "gresite": ["la final, înainte de return", "în except", "în afara funcției, mereu"],
         "explicatie": "„Validează devreme”: restul corpului lucrează apoi cu date garantat valide.",
         "concepte": ["ridicarea_exceptiilor"], "dificultate": 1},
    ],
}
