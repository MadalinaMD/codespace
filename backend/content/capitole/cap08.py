# -*- coding: utf-8 -*-
"""Capitolul 8 — Tupluri și comprehensii.
Adaptat după Think Python (Downey), cap. 12 „Tuples” și The Python Tutorial §5.1.3."""

SURSA_TUPLE = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 12 „Tuples”."
SURSA_COMPR = "Python Software Foundation, The Python Tutorial — §5.1.3 „List Comprehensions”."

CAPITOL = {
    "slug": "tupluri-si-comprehensii",
    "titlu": "Tupluri și comprehensii",
    "descriere": "Secvențe imuabile, împachetare/despachetare și forma concisă de a construi liste.",
    "ordine": 8,
    "lectii": [
        {
            "slug": "tupluri",
            "titlu": "Tupluri: secvențe imuabile",
            "ordine": 1,
            "concepte": ["tupluri"],
            "sursa": SURSA_TUPLE,
            "continut_md": """## Ce e un tuplu?

Un **tuplu** e ca o listă care nu se mai poate schimba după creare —
o secvență **imuabilă**:

```python
punct = (3, 4)
culoare = (255, 128, 0)
unul = (42,)        # tuplu cu un element: virgula e obligatorie!
```

Indexarea, felierea, `len` și parcurgerea cu `for` funcționează ca la liste.
Doar modificarea e interzisă: `punct[0] = 5` → `TypeError`.

## La ce folosesc, dacă listele pot „mai mult”?

- **Date care nu trebuie să se schimbe**: coordonate, RGB, (zi, lună, an);
- pot fi **chei de dicționar** (listele nu pot — vezi capitolul următor);
- semnalează intenția: „acest grup de valori e o unitate fixă”.

## Împachetare și despachetare

Python împachetează automat valorile separate prin virgulă și le poate
despacheta înapoi în variabile:

```python
punct = 3, 4              # împachetare (parantezele-s opționale)
x, y = punct              # despachetare: x=3, y=4
a, b = b, a               # de aceea funcționează schimbul de valori!
```

## Funcții care returnează „mai multe valori”

Trucul standard: returnezi un tuplu și îl despachetezi la apel:

```python
def min_max(numere):
    return min(numere), max(numere)

cel_mic, cel_mare = min_max([3, 8, 1])
```

## De reținut

- `(x,)` cu virgulă pentru tuplul cu un singur element;
- despachetarea cere același număr de variabile câte elemente are tuplul;
- listă = colecție care evoluează; tuplu = grup fix de valori legate.""",
            "cod_exemplu": """# Tupluri: create, indexate, parcurse
punct = (3, 4)
print(punct[0], punct[1])

# Despachetare
x, y = punct
print(f"x={x}, y={y}")

# Schimbul de valori = împachetare + despachetare
a, b = 1, 2
a, b = b, a
print(a, b)        # 2 1

# Funcție cu „două rezultate”
def min_max(numere):
    return min(numere), max(numere)

cel_mic, cel_mare = min_max([7, 2, 9, 4])
print(cel_mic, cel_mare)

# enumerate produce tupluri (index, element)
for index, nume in enumerate(["Ana", "Dan"]):
    print(index, nume)""",
            "exercitii": [
                {
                    "titlu": "Statistici dintr-o listă",
                    "enunt_md": """Definește funcția `statistici(numere)` care returnează un **tuplu cu trei
valori**: `(minim, maxim, suma)` pentru lista primită.

*Exemplu: `statistici([3, 8, 1])` → `(1, 8, 12)`.*""",
                    "cod_start": "def statistici(numere):\n    pass\n",
                    "solutie": "def statistici(numere):\n    return (min(numere), max(numere), sum(numere))\n",
                    "mod": "functie",
                    "functie_nume": "statistici",
                    "dificultate": 1,
                    "concepte": ["tupluri", "liste_metode"],
                    "teste": [
                        {"apel": "statistici([3, 8, 1])", "asteptat": "(1, 8, 12)"},
                        {"apel": "statistici([5])", "asteptat": "(5, 5, 5)"},
                        {"apel": "statistici([-2, 0, 2])", "asteptat": "(-2, 2, 0)"},
                    ],
                },
            ],
        },
        {
            "slug": "comprehensii",
            "titlu": "Comprehensii de liste",
            "ordine": 2,
            "concepte": ["comprehensii"],
            "sursa": SURSA_COMPR,
            "continut_md": """## Filtrare + transformare, într-un singur rând

Tiparele de la listele cu bucle au o formă concisă, foarte folosită în Python:

```python
# Transformare — bucla:               # Comprehensia:
patrate = []
for n in range(5):                    patrate = [n * n for n in range(5)]
    patrate.append(n * n)
```

Citește comprehensia de la stânga: „construiește lista cu `n * n`, pentru
fiecare `n` din `range(5)`”.

## Cu filtru

```python
pare = [n for n in numere if n % 2 == 0]
```

Forma generală: `[expresie for element in secventa if conditie]` —
exact `transformare` + `filtrare` din capitolul trecut, comprimate.

## Exemple care apar peste tot

```python
litere_mari = [s.upper() for s in ["ana", "dan"]]      # ['ANA', 'DAN']
lungimi = [len(s) for s in ["mere", "pere", "kiwi"]]   # [4, 4, 4]
numere = [int(x) for x in "3 8 5".split()]             # [3, 8, 5]
```

Ultima linie e idiomul standard pentru „citește mai multe numere de pe o
linie” — îl vei folosi des.

## Când NU folosești comprehensii

Dacă logica are nevoie de mai mulți pași, de `elif`-uri sau de efecte
secundare, bucla clasică e mai lizibilă. Comprehensia e pentru cazurile
simple: o expresie, eventual un filtru.

## De reținut

- `[expr for x in secv]` = transformare; adaugă `if` pentru filtrare;
- rezultatul e întotdeauna o listă NOUĂ;
- lizibilitatea bate concizia — nu înghesui logică complicată.""",
            "cod_exemplu": """numere = [3, 8, 5, 12, 7, 4]

# Transformare
patrate = [n * n for n in numere]
print(patrate)

# Filtrare
pare = [n for n in numere if n % 2 == 0]
print(pare)

# Ambele deodată
patrate_pare = [n * n for n in numere if n % 2 == 0]
print(patrate_pare)

# Idiomuri frecvente
print([s.upper() for s in ["ana", "dan", "ema"]])
print([int(x) for x in "10 20 30".split()])
print(sum(n for n in range(101) if n % 3 == 0))  # suma multiplilor lui 3""",
            "exercitii": [
                {
                    "titlu": "Lungimile cuvintelor",
                    "enunt_md": """Definește funcția `lungimi(cuvinte)` care returnează lista lungimilor
fiecărui cuvânt, **scrisă ca o comprehensie** (un singur `return`).

*Exemplu: `lungimi(["mere", "ace", "pix"])` → `[4, 3, 3]`.*""",
                    "cod_start": "def lungimi(cuvinte):\n    return []  # înlocuiește cu o comprehensie\n",
                    "solutie": "def lungimi(cuvinte):\n    return [len(c) for c in cuvinte]\n",
                    "mod": "functie",
                    "functie_nume": "lungimi",
                    "dificultate": 1,
                    "concepte": ["comprehensii"],
                    "teste": [
                        {"apel": "lungimi(['mere', 'ace', 'pix'])", "asteptat": "[4, 3, 3]"},
                        {"apel": "lungimi([])", "asteptat": "[]"},
                        {"apel": "lungimi([''])", "asteptat": "[0]"},
                    ],
                },
                {
                    "titlu": "Doar cuvintele lungi",
                    "enunt_md": """Definește funcția `cuvinte_lungi(cuvinte, minim)` care returnează lista
cuvintelor cu lungimea **cel puțin** `minim`, transformate în litere mari.

*Exemplu: `cuvinte_lungi(["ac", "mere", "pix", "banana"], 4)` →
`["MERE", "BANANA"]`.*

Folosește o singură comprehensie cu transformare + filtru.""",
                    "cod_start": "def cuvinte_lungi(cuvinte, minim):\n    pass\n",
                    "solutie": "def cuvinte_lungi(cuvinte, minim):\n    return [c.upper() for c in cuvinte if len(c) >= minim]\n",
                    "mod": "functie",
                    "functie_nume": "cuvinte_lungi",
                    "dificultate": 2,
                    "concepte": ["comprehensii", "siruri_metode"],
                    "teste": [
                        {"apel": "cuvinte_lungi(['ac', 'mere', 'pix', 'banana'], 4)", "asteptat": "['MERE', 'BANANA']"},
                        {"apel": "cuvinte_lungi(['a', 'b'], 1)", "asteptat": "['A', 'B']"},
                        {"apel": "cuvinte_lungi(['scurt'], 10)", "asteptat": "[]"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Cum scrii un tuplu cu un singur element?", "corecta": "(42,)",
         "gresite": ["(42)", "tuple[42]", "{42}"],
         "explicatie": "Fără virgulă, (42) e doar numărul 42 între paranteze.",
         "concepte": ["tupluri"], "dificultate": 2},
        {"text": "Ce se întâmplă la `t = (1, 2); t[0] = 5`?", "corecta": "TypeError — tuplurile sunt imuabile",
         "gresite": ["t devine (5, 2)", "se creează un tuplu nou", "IndexError"],
         "explicatie": "Tuplurile nu pot fi modificate după creare.",
         "concepte": ["tupluri"], "dificultate": 1},
        {"text": "Ce face linia `x, y = y, x`?", "corecta": "interschimbă valorile lui x și y",
         "gresite": ["produce eroare", "creează o listă", "compară x cu y"],
         "explicatie": "Dreapta se împachetează într-un tuplu, apoi se despachetează în noile x, y.",
         "concepte": ["tupluri"], "dificultate": 1},
        {"text": "Cum returnează elegant o funcție Python „două valori”?",
         "corecta": "returnează un tuplu, despachetat la apel",
         "gresite": ["folosește două return-uri consecutive", "scrie în două variabile globale", "nu se poate"],
         "explicatie": "return a, b creează un tuplu; la apel: x, y = functie().",
         "concepte": ["tupluri"], "dificultate": 1},
        {"text": "Ce produce `[n * 2 for n in range(3)]`?", "corecta": "[0, 2, 4]",
         "gresite": ["[2, 4, 6]", "[0, 1, 2]", "(0, 2, 4)"],
         "explicatie": "range(3) = 0, 1, 2, fiecare dublat: 0, 2, 4.",
         "concepte": ["comprehensii"], "dificultate": 1},
        {"text": "Ce produce `[c for c in \"abcd\" if c in \"aeiou\"]`?", "corecta": "['a']",
         "gresite": ["'a'", "['a', 'b', 'c', 'd']", "[]"],
         "explicatie": "Filtrul păstrează doar vocalele; rezultatul e o listă cu un element.",
         "concepte": ["comprehensii"], "dificultate": 2},
        {"text": "Care buclă e echivalentă cu `r = [f(x) for x in s if c(x)]`?",
         "corecta": "r = []; for x in s: if c(x): r.append(f(x))",
         "gresite": ["r = []; for x in s: r.append(f(x))", "for x in s: r = f(x)", "r = f(s) if c(s) else []"],
         "explicatie": "Comprehensia = filtrare (if) + transformare (expresia) + append, comprimate.",
         "concepte": ["comprehensii"], "dificultate": 2},
        {"text": "Idiomul `[int(x) for x in linie.split()]` servește la…",
         "corecta": "transformarea unei linii de text în listă de numere",
         "gresite": ["sortarea numerelor dintr-o linie", "eliminarea spațiilor dintr-un șir", "validarea unui număr"],
         "explicatie": "split() rupe linia în bucăți, int() convertește fiecare bucată.",
         "concepte": ["comprehensii", "conversii_tip"], "dificultate": 2},
    ],
}
