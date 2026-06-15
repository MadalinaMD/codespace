# -*- coding: utf-8 -*-
"""Capitolul 7 — Liste.
Adaptat după Think Python (Downey), cap. 10 „Lists"."""

SURSA = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 10 „Lists”."

CAPITOL = {
    "slug": "liste",
    "titlu": "Liste",
    "descriere": "Colecția fundamentală a limbajului: creare, modificare, metode și parcurgere.",
    "ordine": 7,
    "lectii": [
        {
            "slug": "liste-bazele",
            "titlu": "Liste: crearea, indexarea, modificarea",
            "ordine": 1,
            "concepte": ["liste_baza"],
            "sursa": SURSA,
            "continut_md": """## O secvență de orice

O **listă** ține mai multe valori, în ordine, sub un singur nume:

```python
note = [9, 7, 10, 8]
cuvinte = ["mere", "pere"]
amestec = [1, "doi", 3.0, True]
goala = []
```

Indexarea și felierea funcționează **exact ca la șiruri**: `note[0]` → `9`,
`note[-1]` → `8`, `note[1:3]` → `[7, 10]`, `len(note)` → `4`.

## Diferența-cheie: listele sunt MUTABILE

Spre deosebire de șiruri, o listă **poate fi modificată pe loc**:

```python
note = [9, 7, 10, 8]
note[1] = 5          # acum [9, 5, 10, 8]
note.append(6)       # adaugă la final: [9, 5, 10, 8, 6]
```

`append` e cea mai folosită metodă: construiește liste element cu element,
exact ca șirul-acumulator de la capitolul trecut, dar cu `append` în loc de `+=`.

## Atenție la aliasing

Atribuirea NU copiază lista — ambele nume arată spre **aceeași** listă:

```python
a = [1, 2, 3]
b = a            # b e UN ALT NUME pentru aceeași listă
b.append(4)
print(a)         # [1, 2, 3, 4] — „s-a modificat” și a!
```

Pentru o copie reală: `b = a.copy()` (sau `b = a[:]`).

## De reținut

- liste = secvențe mutabile; șiruri = secvențe imuabile;
- `append` adaugă la final, `lista[i] = x` înlocuiește;
- `b = a` creează un alias, nu o copie.""",
            "cod_exemplu": """note = [9, 7, 10, 8]

# Indexare și feliere — ca la șiruri
print(note[0], note[-1])     # 9 8
print(note[1:3])             # [7, 10]
print(len(note))             # 4

# Mutabilitate: modificăm pe loc
note[1] = 5
note.append(6)
print(note)                  # [9, 5, 10, 8, 6]

# Aliasing vs. copiere — experimentul-cheie
a = [1, 2, 3]
b = a            # alias
c = a.copy()     # copie reală
b.append(99)
print("a =", a)  # [1, 2, 3, 99] — modificat prin b!
print("c =", c)  # [1, 2, 3]     — copia e separată""",
            "exercitii": [
                {
                    "titlu": "Primul și ultimul",
                    "enunt_md": """Definește funcția `capete(lista)` care returnează o **listă nouă** cu exact
două elemente: primul și ultimul element al listei primite.

*Exemplu: `capete([3, 8, 5, 12])` → `[3, 12]`.*

Poți presupune că lista are cel puțin un element (pentru o listă cu unul
singur, rezultatul îl conține de două ori).""",
                    "cod_start": "def capete(lista):\n    pass\n",
                    "solutie": "def capete(lista):\n    return [lista[0], lista[-1]]\n",
                    "mod": "functie",
                    "functie_nume": "capete",
                    "dificultate": 1,
                    "concepte": ["liste_baza"],
                    "teste": [
                        {"apel": "capete([3, 8, 5, 12])", "asteptat": "[3, 12]"},
                        {"apel": "capete([7])", "asteptat": "[7, 7]"},
                        {"apel": "capete(['a', 'b', 'c'])", "asteptat": "['a', 'c']"},
                    ],
                },
            ],
        },
        {
            "slug": "metodele-listelor",
            "titlu": "Metodele listelor și funcțiile pe liste",
            "ordine": 2,
            "concepte": ["liste_metode"],
            "sursa": SURSA,
            "continut_md": """## Metodele care modifică lista (pe loc)

| Metodă | Efect |
|--------|-------|
| `append(x)` | adaugă x la final |
| `insert(i, x)` | inserează x la poziția i |
| `remove(x)` | șterge PRIMA apariție a lui x (ValueError dacă lipsește) |
| `pop()` / `pop(i)` | scoate și RETURNEAZĂ ultimul element / cel de la i |
| `sort()` | sortează lista pe loc (returnează None!) |
| `reverse()` | inversează ordinea pe loc |

Capcana clasică: `lista = lista.sort()` distruge lista (sort returnează
`None`). Corect: `lista.sort()` simplu.

## Funcții care NU modifică lista

```python
numere = [3, 8, 1]
sorted(numere)     # [1, 3, 8] — listă NOUĂ, originalul neschimbat
sum(numere)        # 12
min(numere), max(numere)
len(numere)
```

Regulă de orientare: **metodele** listei o modifică de obicei pe loc;
**funcțiile** (`sorted`, `sum`, …) returnează rezultate noi.

## Căutare

```python
8 in numere            # True / False
numere.index(8)        # poziția primei apariții (ValueError dacă lipsește)
numere.count(8)        # de câte ori apare
```

## De reținut

- `sort()` modifică și returnează None; `sorted()` returnează o listă nouă;
- `pop()` e singura care și modifică, și returnează ceva util;
- `remove` șterge după valoare, `pop` după poziție.""",
            "cod_exemplu": """numere = [3, 8, 1, 8, 5]

# Modificare pe loc
numere.append(10)
numere.remove(8)        # doar PRIMA apariție a lui 8
print(numere)           # [3, 1, 8, 5, 10]

ultimul = numere.pop()  # scoate și returnează 10
print(ultimul, numere)

# sort vs sorted — diferența esențială
a = [3, 1, 2]
b = sorted(a)           # b = [1, 2, 3], a neschimbat
print(a, b)
a.sort()                # a devine [1, 2, 3], pe loc
print(a)

# Agregate
note = [9, 7, 10, 8]
print(sum(note), min(note), max(note))
print("Media:", sum(note) / len(note))""",
            "exercitii": [
                {
                    "titlu": "Media fără extreme",
                    "enunt_md": """Definește funcția `media_fara_extreme(note)` care returnează media
aritmetică a listei **după eliminarea unei singure apariții** a notei minime
și a celei maxime (sistemul de jurizare din concursuri).

Rezultatul se rotunjește la 2 zecimale cu `round(x, 2)`.
Lista are mereu cel puțin 3 elemente.

*Exemplu: `media_fara_extreme([9, 4, 10, 8])` → media lui `[9, 8]` → `8.5`.*""",
                    "cod_start": "def media_fara_extreme(note):\n    # copiază lista, scoate min și max, calculează media\n    pass\n",
                    "solutie": "def media_fara_extreme(note):\n    ramase = note.copy()\n    ramase.remove(min(ramase))\n    ramase.remove(max(ramase))\n    return round(sum(ramase) / len(ramase), 2)\n",
                    "mod": "functie",
                    "functie_nume": "media_fara_extreme",
                    "dificultate": 2,
                    "concepte": ["liste_metode"],
                    "teste": [
                        {"apel": "media_fara_extreme([9, 4, 10, 8])", "asteptat": "8.5"},
                        {"apel": "media_fara_extreme([5, 5, 5])", "asteptat": "5.0"},
                        {"apel": "media_fara_extreme([1, 2, 3, 4, 100])", "asteptat": "3.0"},
                    ],
                },
            ],
        },
        {
            "slug": "liste-si-bucle",
            "titlu": "Liste și bucle: filtrare și transformare",
            "ordine": 3,
            "concepte": ["liste_si_bucle"],
            "sursa": SURSA,
            "continut_md": """## Parcurgerea listelor

```python
note = [9, 7, 10, 8]
for nota in note:
    print(nota)
```

Toate tiparele cu acumulatori de la capitolul 3 funcționează identic — doar
că acum sursa e o listă.

## Tiparul FILTRARE: lista elementelor care îndeplinesc o condiție

```python
pare = []
for n in [3, 8, 5, 12, 7, 4]:
    if n % 2 == 0:
        pare.append(n)
# pare = [8, 12, 4]
```

## Tiparul TRANSFORMARE: aplici o operație fiecărui element

```python
dublate = []
for n in [1, 2, 3]:
    dublate.append(n * 2)
# dublate = [2, 4, 6]
```

Filtrarea + transformarea se pot combina într-o singură buclă. Acestea două
tipare acoperă o proporție uriașă din codul de prelucrare a datelor — și au
o formă prescurtată (comprehensiile) pe care o înveți în capitolul următor.

## Greșeala de evitat

Nu modifica lista PE CARE o parcurgi (remove/append în timpul lui `for` pe
aceeași listă) — elementele „se mută” sub picioarele buclei și rezultatele
devin imprevizibile. Construiește o **listă nouă** în schimb.

## De reținut

- filtrare: `if` + `append` într-o buclă, rezultat = listă nouă;
- transformare: operație + `append`;
- nu modifica lista parcursă — construiește alta.""",
            "cod_exemplu": """numere = [3, 8, 5, 12, 7, 4, 9]

# FILTRARE: doar numerele pare
pare = []
for n in numere:
    if n % 2 == 0:
        pare.append(n)
print("Pare:", pare)

# TRANSFORMARE: pătratele tuturor numerelor
patrate = []
for n in numere:
    patrate.append(n * n)
print("Pătrate:", patrate)

# Combinate: pătratele numerelor impare
patrate_impare = []
for n in numere:
    if n % 2 == 1:
        patrate_impare.append(n * n)
print("Pătratele imparelor:", patrate_impare)""",
            "exercitii": [
                {
                    "titlu": "Filtrarea promovaților",
                    "enunt_md": """Definește funcția `promovati(note)` care primește o listă de note și
returnează **lista notelor de trecere** (≥ 5), în ordinea originală.

*Exemplu: `promovati([3, 7, 4, 9, 5])` → `[7, 9, 5]`.*""",
                    "cod_start": "def promovati(note):\n    rezultat = []\n    # filtrează notele >= 5\n    return rezultat\n",
                    "solutie": "def promovati(note):\n    rezultat = []\n    for nota in note:\n        if nota >= 5:\n            rezultat.append(nota)\n    return rezultat\n",
                    "mod": "functie",
                    "functie_nume": "promovati",
                    "dificultate": 1,
                    "concepte": ["liste_si_bucle"],
                    "teste": [
                        {"apel": "promovati([3, 7, 4, 9, 5])", "asteptat": "[7, 9, 5]"},
                        {"apel": "promovati([1, 2, 3])", "asteptat": "[]"},
                        {"apel": "promovati([10, 10])", "asteptat": "[10, 10]"},
                        {"apel": "promovati([])", "asteptat": "[]"},
                    ],
                },
                {
                    "titlu": "Al doilea maxim",
                    "enunt_md": """Definește funcția `al_doilea_maxim(numere)` care returnează **a doua cea mai
mare valoare distinctă** din listă.

*Exemplu: `al_doilea_maxim([3, 8, 8, 5])` → `5` (valorile distincte sunt
3, 5, 8).*

Lista conține cel puțin două valori distincte.

*Indiciu: parcurge lista ținând „recordul” și „vice-recordul”, sau gândește-te
cum te poate ajuta `set` + `sorted`.*""",
                    "cod_start": "def al_doilea_maxim(numere):\n    pass\n",
                    "solutie": "def al_doilea_maxim(numere):\n    distincte = sorted(set(numere))\n    return distincte[-2]\n",
                    "mod": "functie",
                    "functie_nume": "al_doilea_maxim",
                    "dificultate": 3,
                    "concepte": ["liste_si_bucle", "liste_metode"],
                    "teste": [
                        {"apel": "al_doilea_maxim([3, 8, 8, 5])", "asteptat": "5"},
                        {"apel": "al_doilea_maxim([1, 2])", "asteptat": "1"},
                        {"apel": "al_doilea_maxim([10, 9, 10, 8])", "asteptat": "9"},
                        {"apel": "al_doilea_maxim([-1, -5, -3])", "asteptat": "-3"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Care e diferența fundamentală dintre liste și șiruri?",
         "corecta": "listele sunt mutabile, șirurile imuabile",
         "gresite": ["listele țin doar numere", "șirurile nu se pot indexa", "listele nu au lungime fixă, șirurile da"],
         "explicatie": "lista[0] = x funcționează; sir[0] = 'x' ridică TypeError.",
         "concepte": ["liste_baza"], "dificultate": 1},
        {"text": "Ce afișează: `a = [1, 2]; b = a; b.append(3); print(a)`?",
         "corecta": "[1, 2, 3]", "gresite": ["[1, 2]", "[3]", "eroare"],
         "explicatie": "b = a creează un alias — ambele nume arată spre aceeași listă.",
         "concepte": ["liste_baza"], "dificultate": 2},
        {"text": "Cum obții o copie independentă a listei `a`?", "corecta": "b = a.copy()",
         "gresite": ["b = a", "b = list(a, copy=True)", "b = a.clone()"],
         "explicatie": "a.copy() sau a[:] creează o listă nouă cu aceleași elemente.",
         "concepte": ["liste_baza"], "dificultate": 1},
        {"text": "Ce valoare are `x` după `x = [3, 1, 2].sort()`?", "corecta": "None",
         "gresite": ["[1, 2, 3]", "[3, 1, 2]", "eroare"],
         "explicatie": "sort() sortează PE LOC și returnează None — capcana clasică. Pentru o listă nouă: sorted().",
         "concepte": ["liste_metode"], "dificultate": 2},
        {"text": "Care e diferența dintre `remove` și `pop`?",
         "corecta": "remove șterge după valoare; pop scoate după poziție și returnează elementul",
         "gresite": ["sunt identice", "pop șterge toate aparițiile", "remove returnează elementul șters"],
         "explicatie": "remove(x) caută valoarea x; pop(i) lucrează cu indexul și îți dă elementul înapoi.",
         "concepte": ["liste_metode"], "dificultate": 2},
        {"text": "Ce returnează `sum([1, 2, 3]) / len([1, 2, 3])`?", "corecta": "2.0",
         "gresite": ["2", "6", "eroare"],
         "explicatie": "6 / 3 = 2.0 — împărțirea cu / produce mereu float.",
         "concepte": ["liste_metode"], "dificultate": 1},
        {"text": "Tiparul „filtrare” construiește…",
         "corecta": "o listă nouă cu elementele care trec o condiție",
         "gresite": ["aceeași listă, sortată", "un număr — câte elemente trec", "un bool"],
         "explicatie": "if + append într-o buclă = filtrare; numărarea e alt tipar (acumulator numeric).",
         "concepte": ["liste_si_bucle"], "dificultate": 1},
        {"text": "De ce e periculos să faci `remove` pe lista pe care o parcurgi cu for?",
         "corecta": "elementele se deplasează și bucla sare peste unele",
         "gresite": ["Python interzice și dă SyntaxError", "lista devine imuabilă", "se consumă multă memorie"],
         "explicatie": "Ștergerea în timpul iterării decalează indecșii — construiește o listă nouă în loc.",
         "concepte": ["liste_si_bucle"], "dificultate": 2},
    ],
}
