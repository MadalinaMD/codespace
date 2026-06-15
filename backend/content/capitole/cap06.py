# -*- coding: utf-8 -*-
"""Capitolul 6 — Șiruri de caractere.
Adaptat după Think Python (Downey), cap. 8 „Strings”."""

SURSA = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 8 „Strings”."

CAPITOL = {
    "slug": "siruri",
    "titlu": "Șiruri de caractere",
    "descriere": "Textul ca secvență: indexare, feliere, metode și parcurgerea caracter cu caracter.",
    "ordine": 6,
    "lectii": [
        {
            "slug": "indexare-si-feliere",
            "titlu": "Indexare și feliere (slicing)",
            "ordine": 1,
            "concepte": ["siruri_indexare"],
            "sursa": SURSA,
            "continut_md": """## Șirul ca secvență

Un șir e o **secvență de caractere**. Fiecare caracter are o poziție (index),
numerotată **de la 0**:

```python
cuvant = "Python"
#         P  y  t  h  o  n
# index   0  1  2  3  4  5
print(cuvant[0])    # P
print(cuvant[5])    # n
```

`len()` dă lungimea șirului, deci ultimul caracter e la `len(s) - 1`.
Accesarea unui index inexistent → `IndexError`.

## Indecși negativi

Python permite numărarea de la coadă: `s[-1]` e ultimul caracter, `s[-2]`
penultimul.

## Felierea: s[start:stop]

O **felie** extrage o sub-secvență. Ca la `range`, capătul `stop` **nu se
include**:

```python
s = "programare"
print(s[0:3])    # pro
print(s[3:7])    # gram
print(s[:5])     # progr   (de la început)
print(s[5:])     # amare   (până la final)
print(s[::-1])   # eramargorp  (pasul -1 = inversare)
```

## Imutabilitate

Șirurile **nu se pot modifica** pe loc: `s[0] = "X"` → `TypeError`. Orice
„modificare” construiește de fapt un șir **nou**:

```python
s = "python"
s = "P" + s[1:]    # "Python" — șir nou, reatribuit
```

## De reținut

- indexarea începe de la 0; `s[-1]` e ultimul caracter;
- felia `s[a:b]` are exact `b - a` caractere;
- șirurile sunt imuabile — metodele și felierea produc șiruri noi.""",
            "cod_exemplu": """cuvant = "programare"

# Indexare: pozitiv și negativ
print(cuvant[0], cuvant[4], cuvant[-1])   # p r e

# Felii
print(cuvant[0:3])     # pro
print(cuvant[:5])      # progr
print(cuvant[5:])      # amare
print(cuvant[::-1])    # inversarea șirului

# len și ultimul caracter
print(len(cuvant), cuvant[len(cuvant) - 1])

# Imutabilitate: construim un șir NOU
s = "python"
s = s[0].upper() + s[1:]
print(s)               # Python""",
            "exercitii": [
                {
                    "titlu": "Palindrom",
                    "enunt_md": """Definește funcția `este_palindrom(s)` care returnează `True` dacă șirul `s`
se citește identic în ambele sensuri, altfel `False`.

*Exemple: `"cojoc"` → `True`; `"python"` → `False`.*

*Indiciu: felia cu pas negativ `s[::-1]` inversează șirul.*""",
                    "cod_start": "def este_palindrom(s):\n    pass\n",
                    "solutie": "def este_palindrom(s):\n    return s == s[::-1]\n",
                    "mod": "functie",
                    "functie_nume": "este_palindrom",
                    "dificultate": 1,
                    "concepte": ["siruri_indexare"],
                    "teste": [
                        {"apel": "este_palindrom('cojoc')", "asteptat": "True"},
                        {"apel": "este_palindrom('python')", "asteptat": "False"},
                        {"apel": "este_palindrom('a')", "asteptat": "True"},
                        {"apel": "este_palindrom('')", "asteptat": "True"},
                    ],
                },
                {
                    "titlu": "Inițialele numelui",
                    "enunt_md": """Definește funcția `initiale(prenume, nume)` care returnează inițialele
celor două cuvinte, despărțite prin punct și urmate de punct.

*Exemplu: `initiale("Ada", "Lovelace")` → `"A.L."`.*""",
                    "cod_start": "def initiale(prenume, nume):\n    pass\n",
                    "solutie": "def initiale(prenume, nume):\n    return f\"{prenume[0]}.{nume[0]}.\"\n",
                    "mod": "functie",
                    "functie_nume": "initiale",
                    "dificultate": 1,
                    "concepte": ["siruri_indexare", "fstring"],
                    "teste": [
                        {"apel": "initiale('Ada', 'Lovelace')", "asteptat": "'A.L.'"},
                        {"apel": "initiale('Grace', 'Hopper')", "asteptat": "'G.H.'"},
                    ],
                },
            ],
        },
        {
            "slug": "metodele-sirurilor",
            "titlu": "Metodele șirurilor",
            "ordine": 2,
            "concepte": ["siruri_metode"],
            "sursa": SURSA,
            "continut_md": """## Metode: funcții „atașate” valorilor

O **metodă** se apelează cu punct: `valoare.metoda(argumente)`. Șirurile vin
cu o colecție bogată:

| Metodă | Efect | Exemplu |
|--------|-------|---------|
| `upper()` / `lower()` | majuscule / minuscule | `"Ana".upper()` → `"ANA"` |
| `strip()` | taie spațiile de la capete | `"  da  ".strip()` → `"da"` |
| `replace(a, b)` | înlocuiește a cu b | `"a-b".replace("-", "+")` → `"a+b"` |
| `count(x)` | de câte ori apare x | `"banana".count("a")` → `3` |
| `find(x)` | indexul primei apariții (-1 dacă lipsește) | `"banana".find("na")` → `2` |
| `startswith(x)` / `endswith(x)` | începe/se termină cu x | `"foto.png".endswith(".png")` → `True` |

Pentru că șirurile sunt imuabile, **toate metodele returnează un șir nou** —
originalul rămâne neatins:

```python
s = "Ana"
s.upper()
print(s)          # tot "Ana"!
s = s.upper()     # abia reatribuirea păstrează rezultatul
```

## split și join — text ↔ listă

```python
"mere pere prune".split()         # ['mere', 'pere', 'prune']
"2026-06-12".split("-")           # ['2026', '06', '12']
", ".join(["mere", "pere"])       # 'mere, pere'
```

`split` sparge un șir în bucăți; `join` le lipește la loc cu un separator.
Împreună sunt cele mai folosite unelte de prelucrare a textului.

## De reținut

- metodele NU modifică șirul — salvează rezultatul (`s = s.strip()`);
- `find` returnează `-1` pentru „nu există”, nu eroare;
- combinația `lower()` + comparație e standard pentru căutări fără
  sensibilitate la majuscule.""",
            "cod_exemplu": """mesaj = "  Buna ziua, CodeSpace!  "

# Curățare și transformare (fiecare produce un șir NOU)
print(mesaj.strip())
print(mesaj.strip().upper())
print(mesaj.strip().replace("ziua", "seara"))

# Căutare și numărare
print("banana".count("a"))      # 3
print("banana".find("na"))      # 2
print("banana".find("xyz"))     # -1 — „nu există”

# split și join
data = "2026-06-12"
parti = data.split("-")
print(parti)                    # ['2026', '06', '12']
print("/".join(parti))          # 2026/06/12""",
            "exercitii": [
                {
                    "titlu": "Normalizarea emailului",
                    "enunt_md": """Definește funcția `normalizeaza(email)` care returnează adresa curățată:
fără spații la capete și cu litere mici.

*Exemplu: `normalizeaza("  Ana.POP@Mail.com ")` → `"ana.pop@mail.com"`.*""",
                    "cod_start": "def normalizeaza(email):\n    pass\n",
                    "solutie": "def normalizeaza(email):\n    return email.strip().lower()\n",
                    "mod": "functie",
                    "functie_nume": "normalizeaza",
                    "dificultate": 1,
                    "concepte": ["siruri_metode"],
                    "teste": [
                        {"apel": "normalizeaza('  Ana.POP@Mail.com ')", "asteptat": "'ana.pop@mail.com'"},
                        {"apel": "normalizeaza('TEST@TEST.RO')", "asteptat": "'test@test.ro'"},
                        {"apel": "normalizeaza('ok@ok.ro')", "asteptat": "'ok@ok.ro'"},
                    ],
                },
                {
                    "titlu": "Numărul de cuvinte",
                    "enunt_md": """Definește funcția `numar_cuvinte(text)` care returnează câte cuvinte conține
textul. Cuvintele sunt separate de spații (unul sau mai multe).

*Indiciu: `split()` fără argumente tratează corect spațiile multiple.
Pentru șirul gol, rezultatul e 0.*""",
                    "cod_start": "def numar_cuvinte(text):\n    pass\n",
                    "solutie": "def numar_cuvinte(text):\n    return len(text.split())\n",
                    "mod": "functie",
                    "functie_nume": "numar_cuvinte",
                    "dificultate": 2,
                    "concepte": ["siruri_metode"],
                    "teste": [
                        {"apel": "numar_cuvinte('ana are mere')", "asteptat": "3"},
                        {"apel": "numar_cuvinte('  un    test  ')", "asteptat": "2"},
                        {"apel": "numar_cuvinte('')", "asteptat": "0"},
                        {"apel": "numar_cuvinte('cuvant')", "asteptat": "1"},
                    ],
                },
            ],
        },
        {
            "slug": "parcurgerea-sirurilor",
            "titlu": "Parcurgerea șirurilor și operatorul in",
            "ordine": 3,
            "concepte": ["parcurgerea_sirurilor"],
            "sursa": SURSA,
            "continut_md": """## Caracter cu caracter

Bucla `for` parcurge un șir direct, fără indecși:

```python
for litera in "Python":
    print(litera)
```

Combinată cu tiparul acumulatorului, parcurgerea rezolvă o întreagă familie
de probleme:

```python
# Câte vocale are un cuvânt?
vocale = 0
for litera in "programare":
    if litera in "aeiou":
        vocale += 1
```

## Operatorul in

`x in s` întreabă dacă `x` apare în `s` — funcționează pentru un caracter sau
un sub-șir întreg:

```python
"gram" in "programare"    # True
"z" in "programare"       # False
```

## Construirea unui șir nou

Acumulatorul poate fi și un șir — pornești de la `""` și lipești:

```python
fara_vocale = ""
for litera in "programare":
    if litera not in "aeiou":
        fara_vocale += litera
print(fara_vocale)    # prgrmr
```

## Cu index, când chiar ai nevoie: enumerate

Uneori vrei și poziția, nu doar caracterul:

```python
for index, litera in enumerate("abc"):
    print(index, litera)    # 0 a / 1 b / 2 c
```

## De reținut

- `for litera in s` e mai curat decât `for i in range(len(s))`;
- `in` / `not in` verifică apartenența — și pentru sub-șiruri;
- șirul-acumulator pornește de la `""`.""",
            "cod_exemplu": """text = "Programarea în Python"

# Numărăm vocalele
vocale = 0
for litera in text.lower():
    if litera in "aeiouăâî":
        vocale += 1
print("Vocale:", vocale)

# Construim un șir nou: doar consoanele
consoane = ""
for litera in text.lower():
    if litera.isalpha() and litera not in "aeiouăâî":
        consoane += litera
print("Consoane:", consoane)

# Apartenența sub-șirurilor
print("Python" in text)     # True
print("Java" in text)       # False

# enumerate: index + caracter
for index, litera in enumerate("cod"):
    print(index, litera)""",
            "exercitii": [
                {
                    "titlu": "Numărarea vocalelor",
                    "enunt_md": """Definește funcția `numara_vocale(text)` care returnează câte vocale
(`a, e, i, o, u`) conține textul, **indiferent de majuscule**.

*Exemplu: `numara_vocale("Programare")` → `4` (o, a, a, e).*""",
                    "cod_start": "def numara_vocale(text):\n    pass\n",
                    "solutie": "def numara_vocale(text):\n    numar = 0\n    for litera in text.lower():\n        if litera in \"aeiou\":\n            numar += 1\n    return numar\n",
                    "mod": "functie",
                    "functie_nume": "numara_vocale",
                    "dificultate": 2,
                    "concepte": ["parcurgerea_sirurilor", "acumulatori"],
                    "teste": [
                        {"apel": "numara_vocale('Programare')", "asteptat": "4"},
                        {"apel": "numara_vocale('AEIOU')", "asteptat": "5"},
                        {"apel": "numara_vocale('brr')", "asteptat": "0"},
                        {"apel": "numara_vocale('')", "asteptat": "0"},
                    ],
                },
                {
                    "titlu": "Cenzura",
                    "enunt_md": """Definește funcția `cenzureaza(text, litera)` care returnează textul în care
**toate** aparițiile literei date (atât mică, cât și mare) sunt înlocuite cu `*`.

*Exemplu: `cenzureaza("Banana", "a")` → `"B*n*n*"`.*

*Rezolvă prin parcurgere cu `for` și un șir-acumulator (nu cu `replace`),
ca să exersezi tiparul.*""",
                    "cod_start": "def cenzureaza(text, litera):\n    rezultat = \"\"\n    # parcurge textul și construiește rezultatul\n    return rezultat\n",
                    "solutie": "def cenzureaza(text, litera):\n    rezultat = \"\"\n    for c in text:\n        if c.lower() == litera.lower():\n            rezultat += \"*\"\n        else:\n            rezultat += c\n    return rezultat\n",
                    "mod": "functie",
                    "functie_nume": "cenzureaza",
                    "dificultate": 2,
                    "concepte": ["parcurgerea_sirurilor", "instructiunea_if"],
                    "teste": [
                        {"apel": "cenzureaza('Banana', 'a')", "asteptat": "'B*n*n*'"},
                        {"apel": "cenzureaza('Ana', 'A')", "asteptat": "'*n*'"},
                        {"apel": "cenzureaza('xyz', 'a')", "asteptat": "'xyz'"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce afișează `print(\"Python\"[1])`?", "corecta": "y",
         "gresite": ["P", "Py", "eroare"],
         "explicatie": "Indexarea începe de la 0, deci poziția 1 e al doilea caracter.",
         "concepte": ["siruri_indexare"], "dificultate": 1},
        {"text": "Ce returnează `\"programare\"[0:3]`?", "corecta": "pro",
         "gresite": ["prog", "rog", "p"],
         "explicatie": "Felia ia indecșii 0, 1, 2 — capătul 3 nu se include.",
         "concepte": ["siruri_indexare"], "dificultate": 1},
        {"text": "Ce înseamnă `s[-1]`?", "corecta": "ultimul caracter din s",
         "gresite": ["eroare de sintaxă", "primul caracter", "șirul fără primul caracter"],
         "explicatie": "Indecșii negativi numără de la coadă: -1 e ultimul, -2 penultimul.",
         "concepte": ["siruri_indexare"], "dificultate": 1},
        {"text": "Șirurile în Python sunt…", "corecta": "imuabile — nu pot fi modificate pe loc",
         "gresite": ["mutabile — s[0] = 'X' funcționează", "imuabile doar dacă sunt constante", "mutabile doar în funcții"],
         "explicatie": "Orice „modificare” creează un șir nou; s[0] = 'X' ridică TypeError.",
         "concepte": ["siruri_indexare"], "dificultate": 2},
        {"text": "Ce afișează: `s = \"ana\"; s.upper(); print(s)`?", "corecta": "ana",
         "gresite": ["ANA", "Ana", "eroare"],
         "explicatie": "upper() returnează un șir NOU; fără reatribuire, s rămâne neschimbat.",
         "concepte": ["siruri_metode"], "dificultate": 2},
        {"text": "Ce returnează `\"banana\".find(\"xyz\")`?", "corecta": "-1",
         "gresite": ["None", "0", "ridică ValueError"],
         "explicatie": "find semnalează absența prin -1 (spre deosebire de index(), care ridică eroare).",
         "concepte": ["siruri_metode"], "dificultate": 2},
        {"text": "Ce produce `\"a,b,c\".split(\",\")`?", "corecta": "['a', 'b', 'c']",
         "gresite": ["'abc'", "('a', 'b', 'c')", "['a,b,c']"],
         "explicatie": "split sparge șirul la fiecare separator și returnează o listă.",
         "concepte": ["siruri_metode"], "dificultate": 1},
        {"text": "Ce valoare are `\"gram\" in \"programare\"`?", "corecta": "True",
         "gresite": ["False", "2", "eroare — in merge doar pe litere"],
         "explicatie": "Operatorul in caută și sub-șiruri întregi, nu doar caractere.",
         "concepte": ["parcurgerea_sirurilor"], "dificultate": 1},
        {"text": "Câte iterații face `for c in \"abc\":`?", "corecta": "3",
         "gresite": ["1", "2", "depinde de len()"],
         "explicatie": "Bucla for parcurge șirul caracter cu caracter: a, b, c.",
         "concepte": ["parcurgerea_sirurilor"], "dificultate": 1},
    ],
}
