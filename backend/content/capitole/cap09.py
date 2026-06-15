# -*- coding: utf-8 -*-
"""Capitolul 9 — Dicționare și mulțimi.
Adaptat după Think Python (Downey), cap. 11 „Dictionaries” și The Python Tutorial §5.4–5.5."""

SURSA_DICT = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 11 „Dictionaries”."
SURSA_SET = "Python Software Foundation, The Python Tutorial — §5.4 „Sets”, §5.5 „Dictionaries”."

CAPITOL = {
    "slug": "dictionare-si-multimi",
    "titlu": "Dicționare și mulțimi",
    "descriere": "Structuri cheie–valoare și colecții de elemente unice: uneltele de organizare a datelor.",
    "ordine": 9,
    "lectii": [
        {
            "slug": "dictionare",
            "titlu": "Dicționare: perechi cheie–valoare",
            "ordine": 1,
            "concepte": ["dictionare"],
            "sursa": SURSA_DICT,
            "continut_md": """## De la index la cheie

Lista găsește elementele după **poziție**; dicționarul le găsește după
**cheie** — orice etichetă imuabilă aleasă de tine:

```python
varste = {"Ana": 20, "Dan": 22, "Ema": 19}
print(varste["Dan"])      # 22

stoc = {}                  # dicționar gol
stoc["mere"] = 10          # adaugă perechea mere → 10
stoc["mere"] = 7           # cheia există → înlocuiește valoarea
```

Cheile sunt unice: a doua atribuire pe aceeași cheie **suprascrie**.

## Cheia lipsă: eroare sau valoare implicită

```python
varste["Ion"]              # KeyError!
varste.get("Ion")          # None — fără eroare
varste.get("Ion", 0)       # 0 — valoarea ta implicită
"Ion" in varste            # False — verificare de existență
```

Aceste trei unelte (`get`, `in`, `[cheie] =`) acoperă aproape tot lucrul
de zi cu zi cu dicționarele.

## Ștergerea

```python
del varste["Dan"]          # KeyError dacă nu există
varste.pop("Dan", None)    # variantă „blândă”
```

## Ce poate fi cheie?

Doar valori **imuabile**: șiruri, numere, tupluri. Listele NU pot fi chei
(se pot schimba, deci „eticheta” și-ar pierde sensul) — încă un motiv pentru
care există tuplurile.

## De reținut

- `d[cheie]` cere existența; `d.get(cheie, implicit)` e varianta sigură;
- `in` testează CHEILE, nu valorile;
- chei imuabile, valori orice.""",
            "cod_exemplu": """# Agenda de note
note = {"Ana": 9, "Dan": 7, "Ema": 10}

print(note["Ana"])             # acces direct
print(note.get("Ion"))         # None — fără eroare
print(note.get("Ion", "n/a"))  # valoare implicită
print("Dan" in note)           # True — caută printre CHEI

# Adăugare și actualizare
note["Ion"] = 8
note["Dan"] = note["Dan"] + 1
print(note)

# Ștergere
del note["Ema"]
print(note)

# Chei de orice tip imuabil
puncte = {(0, 0): "origine", (1, 2): "A"}
print(puncte[(0, 0)])""",
            "exercitii": [
                {
                    "titlu": "Catalogul clasei",
                    "enunt_md": """Definește funcția `nota_studentului(catalog, nume)` care returnează nota
din dicționarul `catalog` pentru studentul `nume`, sau **`-1`** dacă studentul
nu există în catalog.

*Exemplu: `nota_studentului({"Ana": 9}, "Ana")` → `9`;
`nota_studentului({"Ana": 9}, "Ion")` → `-1`.*""",
                    "cod_start": "def nota_studentului(catalog, nume):\n    pass\n",
                    "solutie": "def nota_studentului(catalog, nume):\n    return catalog.get(nume, -1)\n",
                    "mod": "functie",
                    "functie_nume": "nota_studentului",
                    "dificultate": 1,
                    "concepte": ["dictionare"],
                    "teste": [
                        {"apel": "nota_studentului({'Ana': 9, 'Dan': 7}, 'Ana')", "asteptat": "9"},
                        {"apel": "nota_studentului({'Ana': 9}, 'Ion')", "asteptat": "-1"},
                        {"apel": "nota_studentului({}, 'X')", "asteptat": "-1"},
                    ],
                },
            ],
        },
        {
            "slug": "parcurgere-si-frecvente",
            "titlu": "Parcurgerea dicționarelor și numărarea frecvențelor",
            "ordine": 2,
            "concepte": ["dictionare_parcurgere"],
            "sursa": SURSA_DICT,
            "continut_md": """## Trei feluri de a parcurge

```python
note = {"Ana": 9, "Dan": 7}

for nume in note:                  # cheile (implicit)
    print(nume, note[nume])

for nota in note.values():         # doar valorile
    print(nota)

for nume, nota in note.items():    # perechile, despachetate
    print(f"{nume}: {nota}")
```

`items()` + despachetarea în două variabile e forma cea mai des folosită.

## Tiparul REGE: numărarea frecvențelor

„De câte ori apare fiecare element?” — problema asta apare peste tot
(litere într-un text, cuvinte într-un document, voturi, loguri). Soluția
standard cu dicționar:

```python
text = "abracadabra"
frecvente = {}
for litera in text:
    frecvente[litera] = frecvente.get(litera, 0) + 1
# {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
```

Linia-cheie: `get(litera, 0)` întoarce contorul curent **sau 0 dacă litera
apare prima dată** — apoi adunăm 1. Memorează acest idiom; e întrebare
clasică de interviu.

## Cine are valoarea maximă?

```python
cel_mai_frecvent = max(frecvente, key=frecvente.get)
```

`max` pe un dicționar compară cheile; cu `key=frecvente.get` compară
**valorile** și returnează cheia câștigătoare.

## De reținut

- `for k, v in d.items()` — parcurgerea standard;
- `d[x] = d.get(x, 0) + 1` — numărarea frecvențelor;
- `max(d, key=d.get)` — cheia cu valoarea maximă.""",
            "cod_exemplu": """# Frecvența literelor
text = "abracadabra"
frecvente = {}
for litera in text:
    frecvente[litera] = frecvente.get(litera, 0) + 1
print(frecvente)

# Parcurgerea perechilor
for litera, numar in frecvente.items():
    print(f"'{litera}' apare de {numar} ori")

# Litera cea mai frecventă
campioana = max(frecvente, key=frecvente.get)
print("Cea mai frecventă:", campioana)

# Suma valorilor
print("Total litere:", sum(frecvente.values()))""",
            "exercitii": [
                {
                    "titlu": "Frecvența cuvintelor",
                    "enunt_md": """Definește funcția `frecventa_cuvinte(text)` care returnează un dicționar
cu frecvența fiecărui cuvânt din text (cuvintele sunt separate prin spații).

*Exemplu: `frecventa_cuvinte("ana are ana")` → `{"ana": 2, "are": 1}`.*

Folosește idiomul `get(cuvant, 0) + 1`.""",
                    "cod_start": "def frecventa_cuvinte(text):\n    frecvente = {}\n    # numără fiecare cuvânt din text.split()\n    return frecvente\n",
                    "solutie": "def frecventa_cuvinte(text):\n    frecvente = {}\n    for cuvant in text.split():\n        frecvente[cuvant] = frecvente.get(cuvant, 0) + 1\n    return frecvente\n",
                    "mod": "functie",
                    "functie_nume": "frecventa_cuvinte",
                    "dificultate": 2,
                    "concepte": ["dictionare_parcurgere", "siruri_metode"],
                    "teste": [
                        {"apel": "frecventa_cuvinte('ana are ana')", "asteptat": "{'ana': 2, 'are': 1}"},
                        {"apel": "frecventa_cuvinte('a a a')", "asteptat": "{'a': 3}"},
                        {"apel": "frecventa_cuvinte('')", "asteptat": "{}"},
                    ],
                },
                {
                    "titlu": "Inversarea dicționarului",
                    "enunt_md": """Definește funcția `inverseaza(d)` care returnează dicționarul cu cheile și
valorile **interschimbate**.

*Exemplu: `inverseaza({"a": 1, "b": 2})` → `{1: "a", 2: "b"}`.*

Valorile din `d` sunt unice (nu există dubluri).""",
                    "cod_start": "def inverseaza(d):\n    pass\n",
                    "solutie": "def inverseaza(d):\n    invers = {}\n    for cheie, valoare in d.items():\n        invers[valoare] = cheie\n    return invers\n",
                    "mod": "functie",
                    "functie_nume": "inverseaza",
                    "dificultate": 2,
                    "concepte": ["dictionare_parcurgere"],
                    "teste": [
                        {"apel": "inverseaza({'a': 1, 'b': 2})", "asteptat": "{1: 'a', 2: 'b'}"},
                        {"apel": "inverseaza({})", "asteptat": "{}"},
                        {"apel": "inverseaza({'x': 'y'})", "asteptat": "{'y': 'x'}"},
                    ],
                },
            ],
        },
        {
            "slug": "multimi",
            "titlu": "Mulțimi: colecții de elemente unice",
            "ordine": 3,
            "concepte": ["multimi"],
            "sursa": SURSA_SET,
            "continut_md": """## Set: doar elemente distincte, fără ordine

O **mulțime** (`set`) ține fiecare element o singură dată:

```python
culori = {"roșu", "verde", "roșu", "albastru"}
print(culori)            # {'roșu', 'verde', 'albastru'} — dublura a dispărut
print(len(culori))       # 3
```

Atenție: `{}` creează un **dicționar** gol; mulțimea goală se scrie `set()`.

## Folosirea tipică: deduplicare și apartenență

```python
numere = [3, 8, 3, 5, 8]
distincte = set(numere)          # {3, 8, 5}
cate_distincte = len(set(numere))

8 in distincte                   # apartenență FOARTE rapidă
```

Conversia listă → set → listă elimină duplicatele (dar pierde ordinea;
dacă ordinea contează, folosește `sorted(set(...))`).

## Operații de mulțimi

```python
a = {1, 2, 3}
b = {2, 3, 4}
a | b      # reuniune: {1, 2, 3, 4}
a & b      # intersecție: {2, 3}
a - b      # diferență: {1}
```

Acestea răspund elegant la întrebări ca „ce studenți au răspuns la AMBELE
quiz-uri?” (intersecție) sau „cine lipsește?” (diferență).

## De reținut

- set = unicitate garantată + apartenență rapidă + operații de mulțimi;
- mulțimile NU au ordine și NU se indexează (`s[0]` → eroare);
- `set()` pentru mulțimea goală, nu `{}`.""",
            "cod_exemplu": """# Deduplicare
voturi = ["ana", "dan", "ana", "ema", "dan", "ana"]
votanti = set(voturi)
print(votanti, "->", len(votanti), "votanți unici")

# Operații de mulțimi
quiz1 = {"ana", "dan", "ema"}
quiz2 = {"dan", "ema", "ion"}
print("Ambele quiz-uri:", quiz1 & quiz2)
print("Doar primul:", quiz1 - quiz2)
print("Toți studenții:", quiz1 | quiz2)

# Apartenență
print("ana" in quiz1)    # True

# Atenție: {} e dicționar gol, set() e mulțime goală
print(type({}), type(set()))""",
            "exercitii": [
                {
                    "titlu": "Elemente comune",
                    "enunt_md": """Definește funcția `comune(lista1, lista2)` care returnează **lista sortată**
a elementelor care apar în ambele liste (fiecare element o singură dată).

*Exemplu: `comune([1, 2, 2, 3], [2, 3, 4])` → `[2, 3]`.*

*Indiciu: intersecția mulțimilor + `sorted`.*""",
                    "cod_start": "def comune(lista1, lista2):\n    pass\n",
                    "solutie": "def comune(lista1, lista2):\n    return sorted(set(lista1) & set(lista2))\n",
                    "mod": "functie",
                    "functie_nume": "comune",
                    "dificultate": 2,
                    "concepte": ["multimi"],
                    "teste": [
                        {"apel": "comune([1, 2, 2, 3], [2, 3, 4])", "asteptat": "[2, 3]"},
                        {"apel": "comune([1, 2], [3, 4])", "asteptat": "[]"},
                        {"apel": "comune(['a', 'b'], ['b', 'a'])", "asteptat": "['a', 'b']"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce se întâmplă la accesarea unei chei inexistente cu `d[\"cheie\"]`?",
         "corecta": "se ridică KeyError", "gresite": ["rezultă None", "rezultă 0", "cheia se creează automat"],
         "explicatie": "Accesul cu paranteze drepte cere existența cheii; varianta sigură e d.get().",
         "concepte": ["dictionare"], "dificultate": 1},
        {"text": "Ce returnează `d.get(\"x\", 0)` când cheia \"x\" lipsește?", "corecta": "0",
         "gresite": ["KeyError", "None, întotdeauna", "\"x\""],
         "explicatie": "get returnează al doilea argument (valoarea implicită) când cheia lipsește.",
         "concepte": ["dictionare"], "dificultate": 1},
        {"text": "Expresia `\"Ana\" in note` (unde note e dicționar) verifică dacă…",
         "corecta": "\"Ana\" este o CHEIE în dicționar",
         "gresite": ["\"Ana\" este o valoare", "\"Ana\" e cheie sau valoare", "dicționarul e gol"],
         "explicatie": "Operatorul in pe dicționare caută doar printre chei; pentru valori: in d.values().",
         "concepte": ["dictionare"], "dificultate": 2},
        {"text": "De ce o listă NU poate fi cheie de dicționar?",
         "corecta": "pentru că e mutabilă", "gresite": ["pentru că e prea lungă", "pentru că nu se poate compara", "poate fi, fără restricții"],
         "explicatie": "Cheile trebuie să fie imuabile (stabile); tuplurile pot fi chei, listele nu.",
         "concepte": ["dictionare"], "dificultate": 2},
        {"text": "Ce produce idiomul `d[x] = d.get(x, 0) + 1` aplicat repetat?",
         "corecta": "numără de câte ori apare fiecare x",
         "gresite": ["șterge duplicatele", "sortează dicționarul", "inversează cheile cu valorile"],
         "explicatie": "E tiparul standard al frecvențelor: pornește de la 0 și incrementează.",
         "concepte": ["dictionare_parcurgere"], "dificultate": 1},
        {"text": "Cum parcurgi perechile cheie–valoare ale unui dicționar?",
         "corecta": "for k, v in d.items():", "gresite": ["for k, v in d:", "for k, v in d.pairs():", "for v in d.keys():"],
         "explicatie": "items() produce tupluri (cheie, valoare) care se despachetează în k, v.",
         "concepte": ["dictionare_parcurgere"], "dificultate": 1},
        {"text": "Ce returnează `max(d, key=d.get)`?", "corecta": "cheia cu valoarea cea mai mare",
         "gresite": ["valoarea cea mai mare", "perechea (cheie, valoare) maximă", "numărul de chei"],
         "explicatie": "max iterează cheile, dar le compară prin d.get(cheie) — deci câștigă cheia valorii maxime.",
         "concepte": ["dictionare_parcurgere"], "dificultate": 2},
        {"text": "Ce conține `set([1, 2, 2, 3, 3, 3])`?", "corecta": "{1, 2, 3}",
         "gresite": ["[1, 2, 3]", "{1, 2, 2, 3, 3, 3}", "{3}"],
         "explicatie": "Mulțimea păstrează fiecare element o singură dată.",
         "concepte": ["multimi"], "dificultate": 1},
        {"text": "Cum creezi o mulțime GOALĂ?", "corecta": "set()",
         "gresite": ["{}", "[]", "empty_set"],
         "explicatie": "{} creează un dicționar gol — capcana clasică.",
         "concepte": ["multimi"], "dificultate": 2},
        {"text": "Ce calculează `a & b` pentru două mulțimi?", "corecta": "intersecția — elementele comune",
         "gresite": ["reuniunea", "diferența", "produsul cartezian"],
         "explicatie": "& = intersecție, | = reuniune, - = diferență.",
         "concepte": ["multimi"], "dificultate": 1},
    ],
}
