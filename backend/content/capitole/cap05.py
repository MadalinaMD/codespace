# -*- coding: utf-8 -*-
"""Capitolul 5 — Recursivitate.
Adaptat după Think Python (Downey), cap. 5 §5.8–5.10 și cap. 6 §6.5."""

SURSA = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 5 §5.8 „Recursion” și cap. 6 §6.5."

CAPITOL = {
    "slug": "recursivitate",
    "titlu": "Recursivitate",
    "descriere": "Funcții care se apelează pe sine: un mod nou de a gândi problemele, descompunându-le în versiuni mai mici.",
    "ordine": 5,
    "lectii": [
        {
            "slug": "gandirea-recursiva",
            "titlu": "Gândirea recursivă: caz de bază și pas recursiv",
            "ordine": 1,
            "concepte": ["recursivitate"],
            "sursa": SURSA,
            "continut_md": """## O funcție care se apelează pe sine

E perfect legal — și surprinzător de puternic — ca o funcție să se apeleze
pe ea însăși. O astfel de funcție se numește **recursivă**:

```python
def numaratoare(n):
    if n <= 0:
        print("Start!")        # cazul de bază: aici NE OPRIM
    else:
        print(n)
        numaratoare(n - 1)     # pasul recursiv: o problemă MAI MICĂ

numaratoare(3)   # 3, 2, 1, Start!
```

## Cele două ingrediente obligatorii

Orice funcție recursivă corectă are:

1. **Cazul de bază** — situația simplă, rezolvată direct, fără alt apel
   recursiv. El oprește lanțul de apeluri.
2. **Pasul recursiv** — funcția se apelează pe o versiune **mai mică** a
   problemei, care se apropie garantat de cazul de bază.

Dacă lipsește cazul de bază (sau nu se ajunge la el), apelurile se adâncesc
la nesfârșit și Python oprește programul cu `RecursionError`.

## Cum „funcționează” — stiva de apeluri

La fiecare apel, Python pune apelul curent „în așteptare” pe o **stivă** și
pornește unul nou. Când cazul de bază returnează, apelurile în așteptare se
reiau, în ordine inversă. Pentru `factorial(3)`:

```
factorial(3) → 3 * factorial(2)
                     factorial(2) → 2 * factorial(1)
                                         factorial(1) → 1   (caz de bază)
                     factorial(2) = 2 * 1 = 2
factorial(3) = 3 * 2 = 6
```

## Șablonul de gândire

Întreabă-te două lucruri: *(1) care e cel mai simplu caz, pe care îl știu
direct?* și *(2) dacă cineva mi-ar rezolva problema pentru n-1, cum aș
construi din ea soluția pentru n?* Răspunsurile sunt cele două ramuri ale
funcției.

## De reținut

- caz de bază fără recursie + pas recursiv care micșorează problema;
- orice buclă se poate scrie recursiv și invers — unele probleme (arbori,
  fractali) sunt însă mult mai naturale recursiv.""",
            "cod_exemplu": """# Numărătoare inversă recursivă
def numaratoare(n):
    if n <= 0:
        print("Start!")
    else:
        print(n)
        numaratoare(n - 1)

numaratoare(3)

# Factorial: definiția matematică tradusă direct în cod
# 0! = 1 (caz de bază);  n! = n * (n-1)!  (pas recursiv)
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print("5! =", factorial(5))      # 120

# Experiment: ce se întâmplă fără caz de bază?
# def fara_oprire(n): return fara_oprire(n - 1)   # → RecursionError""",
            "exercitii": [
                {
                    "titlu": "Suma recursivă 1..n",
                    "enunt_md": """Definește funcția **recursivă** `suma_pana_la(n)` care returnează
`1 + 2 + … + n`.

- cazul de bază: `suma_pana_la(0)` este `0`;
- pasul recursiv: `suma_pana_la(n)` este `n + suma_pana_la(n - 1)`.

*Fără bucle — exercițiul antrenează recursivitatea.*""",
                    "cod_start": "def suma_pana_la(n):\n    # caz de bază, apoi pas recursiv\n    pass\n",
                    "solutie": "def suma_pana_la(n):\n    if n == 0:\n        return 0\n    return n + suma_pana_la(n - 1)\n",
                    "mod": "functie",
                    "functie_nume": "suma_pana_la",
                    "dificultate": 2,
                    "concepte": ["recursivitate"],
                    "teste": [
                        {"apel": "suma_pana_la(0)", "asteptat": "0"},
                        {"apel": "suma_pana_la(1)", "asteptat": "1"},
                        {"apel": "suma_pana_la(10)", "asteptat": "55"},
                        {"apel": "suma_pana_la(100)", "asteptat": "5050"},
                    ],
                },
            ],
        },
        {
            "slug": "exemple-clasice",
            "titlu": "Exemple clasice: factorial, Fibonacci, numărul de cifre",
            "ordine": 2,
            "concepte": ["recursivitate"],
            "sursa": SURSA,
            "continut_md": """## Factorial — modelul de bază

```python
def factorial(n):
    if n == 0:
        return 1                  # caz de bază
    return n * factorial(n - 1)   # pas recursiv
```

## Fibonacci — două apeluri recursive

Șirul lui Fibonacci: `0, 1, 1, 2, 3, 5, 8, 13, …` — fiecare termen e suma
celor doi dinainte. Definiția are **două** cazuri de bază și **două** apeluri
recursive:

```python
def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)
```

E elegant, dar ineficient pentru n mare: aceleași valori se recalculează de
multe ori (fibonacci(30) face peste un milion de apeluri!). Reține ideea —
există tehnici (memoizare) care repară exact această problemă.

## Recursivitate pe cifrele unui număr

Tăierea ultimei cifre cu `n // 10` micșorează problema — perfect pentru
recursie:

```python
def numar_cifre(n):
    if n < 10:
        return 1                       # o singură cifră
    return 1 + numar_cifre(n // 10)    # 1 + cifrele numărului scurtat
```

## Verificarea celor două ingrediente

La orice funcție recursivă scrisă de tine, bifează conștient: *am caz de
bază? fiecare apel recursiv se apropie de el?* Dacă primești `RecursionError`
sau timeout pe platformă, unul dintre cele două lipsește.

## De reținut

- pot exista mai multe cazuri de bază și mai multe apeluri recursive;
- recursivitatea elegantă nu e mereu eficientă — Fibonacci naiv e exemplul
  canonic;
- `n // 10`, `n - 1`, „jumătatea listei” — toate sunt moduri de a micșora
  problema.""",
            "cod_exemplu": """def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)

def numar_cifre(n):
    if n < 10:
        return 1
    return 1 + numar_cifre(n // 10)

print("6! =", factorial(6))            # 720
print("fibonacci(10) =", fibonacci(10))  # 55
print("cifre în 2026:", numar_cifre(2026))  # 4""",
            "exercitii": [
                {
                    "titlu": "Suma cifrelor, recursiv",
                    "enunt_md": """Definește funcția **recursivă** `suma_cifrelor(n)` care returnează suma
cifrelor numărului natural `n`.

- cazul de bază: dacă `n < 10`, suma e chiar `n`;
- pasul recursiv: ultima cifră (`n % 10`) plus suma cifrelor lui `n // 10`.

*Exemplu: `suma_cifrelor(2026)` → `10`.*""",
                    "cod_start": "def suma_cifrelor(n):\n    pass\n",
                    "solutie": "def suma_cifrelor(n):\n    if n < 10:\n        return n\n    return n % 10 + suma_cifrelor(n // 10)\n",
                    "mod": "functie",
                    "functie_nume": "suma_cifrelor",
                    "dificultate": 2,
                    "concepte": ["recursivitate", "operatori_aritmetici"],
                    "teste": [
                        {"apel": "suma_cifrelor(2026)", "asteptat": "10"},
                        {"apel": "suma_cifrelor(7)", "asteptat": "7"},
                        {"apel": "suma_cifrelor(999)", "asteptat": "27"},
                        {"apel": "suma_cifrelor(1000000)", "asteptat": "1"},
                    ],
                },
                {
                    "titlu": "Fibonacci",
                    "enunt_md": """Definește funcția recursivă `fibonacci(n)` care returnează al `n`-lea termen
al șirului Fibonacci (`fibonacci(0)` → `0`, `fibonacci(1)` → `1`).

Testele folosesc valori mici ale lui `n`, deci varianta naivă cu două apeluri
recursive este suficientă.""",
                    "cod_start": "def fibonacci(n):\n    pass\n",
                    "solutie": "def fibonacci(n):\n    if n == 0:\n        return 0\n    if n == 1:\n        return 1\n    return fibonacci(n - 1) + fibonacci(n - 2)\n",
                    "mod": "functie",
                    "functie_nume": "fibonacci",
                    "dificultate": 3,
                    "concepte": ["recursivitate"],
                    "teste": [
                        {"apel": "fibonacci(0)", "asteptat": "0"},
                        {"apel": "fibonacci(1)", "asteptat": "1"},
                        {"apel": "fibonacci(7)", "asteptat": "13"},
                        {"apel": "fibonacci(12)", "asteptat": "144"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce este cazul de bază al unei funcții recursive?",
         "corecta": "situația rezolvată direct, fără alt apel recursiv",
         "gresite": ["primul apel al funcției", "apelul cu argumentul cel mai mare", "instrucțiunea return"],
         "explicatie": "Cazul de bază oprește lanțul de apeluri — fără el, recursia nu se termină.",
         "concepte": ["recursivitate"], "dificultate": 1},
        {"text": "Ce eroare apare când o funcție recursivă nu are caz de bază accesibil?",
         "corecta": "RecursionError", "gresite": ["SyntaxError", "ValueError", "KeyError"],
         "explicatie": "Stiva de apeluri se umple și Python oprește programul cu RecursionError.",
         "concepte": ["recursivitate"], "dificultate": 1},
        {"text": "Pentru `def f(n): return 1 if n == 0 else n * f(n - 1)`, cât este `f(4)`?",
         "corecta": "24", "gresite": ["4", "10", "RecursionError"],
         "explicatie": "Este factorialul: 4 × 3 × 2 × 1 = 24.",
         "concepte": ["recursivitate"], "dificultate": 2},
        {"text": "Pasul recursiv trebuie să…", "corecta": "apropie problema de cazul de bază",
         "gresite": ["mărească argumentul", "conțină un print", "fie ultimul rând al funcției"],
         "explicatie": "Fiecare apel trebuie să lucreze pe o problemă strict mai mică, altfel recursia nu se oprește.",
         "concepte": ["recursivitate"], "dificultate": 1},
        {"text": "De ce e ineficient Fibonacci recursiv naiv?",
         "corecta": "recalculează aceleași valori de foarte multe ori",
         "gresite": ["folosește prea multă memorie pentru numere", "Python nu optimizează înmulțirile", "are prea multe cazuri de bază"],
         "explicatie": "fibonacci(n-1) și fibonacci(n-2) refac amândouă aceleași subprobleme — creștere exponențială.",
         "concepte": ["recursivitate"], "dificultate": 2},
        {"text": "Câte cazuri de bază are Fibonacci recursiv?", "corecta": "două (n = 0 și n = 1)",
         "gresite": ["unul singur", "niciunul", "câte unul pentru fiecare n"],
         "explicatie": "Pasul recursiv folosește n-1 și n-2, deci ai nevoie de două puncte de oprire.",
         "concepte": ["recursivitate"], "dificultate": 2},
    ],
}
