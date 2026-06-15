# -*- coding: utf-8 -*-
"""Capitolul 2 — Decizii: ramificarea programelor.
Adaptat după Think Python (Downey), cap. 5 „Conditionals and recursion”."""

SURSA = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 5 „Conditionals and recursion”."

CAPITOL = {
    "slug": "decizii",
    "titlu": "Decizii: if, elif, else",
    "descriere": "Programele devin interesante când aleg singure ce să facă: expresii logice și ramificare.",
    "ordine": 2,
    "lectii": [
        {
            "slug": "expresii-logice",
            "titlu": "Expresii logice și comparații",
            "ordine": 1,
            "concepte": ["expresii_logice"],
            "sursa": SURSA,
            "continut_md": """## Adevărat sau fals

O **expresie logică** (booleană) are una dintre două valori: `True` sau `False`.
Cele mai simple expresii logice sunt **comparațiile**:

```python
5 > 3       # True
5 == 5      # True   (egalitate: DOUĂ semne egal!)
5 != 4      # True   (diferit)
5 <= 4      # False
```

Atenție la confuzia clasică: `=` atribuie, `==` compară. `x = 5` pune valoarea 5
în x; `x == 5` întreabă dacă x este 5.

## Operatorii logici: and, or, not

Combinăm condiții simple în condiții compuse:

| Expresie | Este `True` când… |
|----------|-------------------|
| `a and b` | ambele sunt adevărate |
| `a or b` | cel puțin una e adevărată |
| `not a` | a este falsă |

```python
varsta = 20
are_bilet = True
poate_intra = varsta >= 18 and are_bilet   # True
```

În Python poți înlănțui comparațiile ca în matematică: `0 <= nota <= 10` verifică
dintr-o singură mișcare dacă nota e în interval.

## De reținut

- `==` pentru comparare, `=` pentru atribuire;
- `n % 2 == 0` este testul standard de paritate;
- expresiile logice pot fi salvate în variabile (`este_par = n % 2 == 0`) —
  sunt valori ca oricare altele.""",
            "cod_exemplu": """# Comparații — fiecare produce True sau False
print(5 > 3)        # True
print(5 == 5.0)     # True  (valori egale, deși tipuri diferite)
print("ana" == "Ana")  # False — contează literele mari/mici

# Operatori logici
varsta = 20
are_bilet = False
print(varsta >= 18 and are_bilet)   # False — ambele trebuie să fie True
print(varsta >= 18 or are_bilet)    # True  — ajunge una

# Înlănțuirea comparațiilor
nota = 8
print(0 <= nota <= 10)              # True

# Testul de paritate
n = 14
print(n % 2 == 0)                   # True → n e par""",
            "exercitii": [
                {
                    "titlu": "An bisect",
                    "enunt_md": """Programul citește un an (număr întreg) și afișează `True` dacă anul este
bisect, altfel `False`.

Regula completă: anul e bisect dacă **se împarte la 4**, cu excepția anilor
care se împart la 100 — aceia sunt bisecți **doar** dacă se împart și la 400.

*Exemple: 2024 → True; 1900 → False (divizibil cu 100, nu cu 400); 2000 → True.*

*Indiciu: construiește o singură expresie logică cu `and`, `or` și `%`, apoi
afișeaz-o direct cu `print()`.*""",
                    "cod_start": "an = int(input())\n# afișează True dacă anul e bisect, altfel False\n",
                    "solutie": "an = int(input())\nprint(an % 4 == 0 and (an % 100 != 0 or an % 400 == 0))\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["expresii_logice"],
                    "teste": [
                        {"stdin": "2024\n", "asteptat": "True"},
                        {"stdin": "1900\n", "asteptat": "False"},
                        {"stdin": "2000\n", "asteptat": "True"},
                        {"stdin": "2023\n", "asteptat": "False"},
                    ],
                },
            ],
        },
        {
            "slug": "if-elif-else",
            "titlu": "if, elif, else: programul alege",
            "ordine": 2,
            "concepte": ["instructiunea_if"],
            "sursa": SURSA,
            "continut_md": """## Execuția condiționată

Instrucțiunea `if` execută un bloc de cod **doar dacă** o condiție e adevărată:

```python
if temperatura > 30:
    print("E caniculă!")
```

Două detalii de sintaxă, ambele obligatorii:
1. condiția se termină cu **două puncte** `:`;
2. blocul de dedesubt e **indentat** (4 spații) — așa știe Python ce aparține if-ului.

## Alternativa: else

```python
if n % 2 == 0:
    print("par")
else:
    print("impar")
```

## Lanțuri de condiții: elif

Când există mai mult de două cazuri, folosim `elif` („else if”). Python evaluează
condițiile **de sus în jos** și execută **doar prima** ramură adevărată:

```python
if nota >= 9:
    print("excelent")
elif nota >= 5:
    print("promovat")
else:
    print("nepromovat")
```

Ordinea contează! Dacă ai fi verificat întâi `nota >= 5`, un 10 ar fi primit
„promovat”, pentru că prima condiție adevărată câștigă.

## Condiții imbricate

Un `if` poate sta în interiorul altui `if` — fiecare nivel adaugă o indentare.
Deseori însă un lanț `elif` sau un operator `and` e mai lizibil decât imbricarea.

## De reținut

- exact o ramură a unui lanț `if/elif/else` se execută;
- `else` nu are condiție — prinde „tot restul”;
- indentarea NU e decorativă: ea definește structura programului.""",
            "cod_exemplu": """# Clasificarea unei note — lanț if/elif/else
nota = 8.6

if nota >= 9:
    calificativ = "excelent"
elif nota >= 7:
    calificativ = "bine"
elif nota >= 5:
    calificativ = "suficient"
else:
    calificativ = "nepromovat"

print(f"Nota {nota} → {calificativ}")

# Ordinea ramurilor contează: prima condiție adevărată câștigă.
# Încearcă să muți `elif nota >= 5` pe primul loc și vezi ce se strică.

# Condiție compusă în loc de if imbricat
varsta = 16
insotit = True
if varsta >= 18 or insotit:
    print("Acces permis")
else:
    print("Acces interzis")""",
            "exercitii": [
                {
                    "titlu": "Maximul a trei numere",
                    "enunt_md": """Programul citește **trei numere întregi**, fiecare pe o linie, și afișează
cel mai mare dintre ele.

Rezolvă cu `if`/`elif`/`else` — **fără** funcția `max()` (exercițiul antrenează
ramificarea, nu funcțiile gata făcute).""",
                    "cod_start": "a = int(input())\nb = int(input())\nc = int(input())\n# afișează cel mai mare dintre a, b, c (fără max!)\n",
                    "solutie": "a = int(input())\nb = int(input())\nc = int(input())\nif a >= b and a >= c:\n    print(a)\nelif b >= c:\n    print(b)\nelse:\n    print(c)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["instructiunea_if", "expresii_logice"],
                    "teste": [
                        {"stdin": "3\n9\n5\n", "asteptat": "9"},
                        {"stdin": "10\n2\n7\n", "asteptat": "10"},
                        {"stdin": "1\n1\n8\n", "asteptat": "8"},
                        {"stdin": "4\n4\n4\n", "asteptat": "4"},
                        {"stdin": "-5\n-2\n-9\n", "asteptat": "-2"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Care operator verifică egalitatea a două valori?", "corecta": "==",
         "gresite": ["=", "!=", "==="],
         "explicatie": "`=` atribuie o valoare; `==` compară două valori; `===` nu există în Python.",
         "concepte": ["expresii_logice"], "dificultate": 1},
        {"text": "Ce valoare are expresia `True and False`?", "corecta": "False",
         "gresite": ["True", "None", "eroare"],
         "explicatie": "`and` cere ca AMBELE părți să fie adevărate.",
         "concepte": ["expresii_logice"], "dificultate": 1},
        {"text": "Ce valoare are expresia `not (3 > 5)`?", "corecta": "True",
         "gresite": ["False", "3", "eroare"],
         "explicatie": "3 > 5 este False, iar not False este True.",
         "concepte": ["expresii_logice"], "dificultate": 1},
        {"text": "Cum verifici dintr-o singură expresie că `n` este în intervalul [1, 10]?",
         "corecta": "1 <= n <= 10", "gresite": ["1 <= n or n <= 10", "n in (1, 10)", "1 < n > 10"],
         "explicatie": "Python permite înlănțuirea comparațiilor; varianta cu `or` e mereu adevărată.",
         "concepte": ["expresii_logice"], "dificultate": 2},
        {"text": "Într-un lanț `if/elif/else`, câte ramuri se execută?", "corecta": "exact una",
         "gresite": ["toate cele adevărate", "cel puțin una", "depinde de indentare"],
         "explicatie": "Python execută PRIMA ramură cu condiție adevărată (sau else) și sare peste rest.",
         "concepte": ["instructiunea_if"], "dificultate": 1},
        {"text": "Ce lipsește din codul `if x > 0\\n    print(x)`?", "corecta": "două puncte după condiție",
         "gresite": ["paranteze în jurul condiției", "cuvântul then", "acolade în jurul blocului"],
         "explicatie": "Sintaxa cere `if conditie:` — fără `:` apare SyntaxError.",
         "concepte": ["instructiunea_if"], "dificultate": 1},
        {"text": "Ce afișează codul: `nota = 10` … `if nota >= 5: print(\"promovat\")` `elif nota >= 9: print(\"excelent\")`?",
         "corecta": "promovat", "gresite": ["excelent", "ambele mesaje", "nimic"],
         "explicatie": "Prima condiție adevărată câștigă — de aceea cazurile specifice se pun PRIMELE.",
         "concepte": ["instructiunea_if"], "dificultate": 2},
        {"text": "Ce rol are indentarea în Python?", "corecta": "definește blocurile de cod",
         "gresite": ["e doar estetică", "accelerează execuția", "marchează comentariile"],
         "explicatie": "Spre deosebire de alte limbaje, Python folosește indentarea în loc de acolade.",
         "concepte": ["instructiunea_if"], "dificultate": 1},
    ],
}
