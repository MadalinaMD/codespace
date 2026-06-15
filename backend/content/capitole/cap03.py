# -*- coding: utf-8 -*-
"""Capitolul 3 — Repetiție: bucle.
Adaptat după Think Python (Downey), cap. 7 „Iteration” și cap. 4;
The Python Tutorial, §4 „More Control Flow Tools”."""

SURSA_WHILE = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 7 „Iteration”."
SURSA_FOR = "Adaptat după A. B. Downey, Think Python (ed. 2), cap. 4; Python Tutorial, §4.1–4.3."

CAPITOL = {
    "slug": "bucle",
    "titlu": "Repetiție: while și for",
    "descriere": "Puterea calculatorului stă în repetiție: bucle while, for, range și tiparele cu acumulatori.",
    "ordine": 3,
    "lectii": [
        {
            "slug": "bucla-while",
            "titlu": "Bucla while: repetă cât timp",
            "ordine": 1,
            "concepte": ["bucla_while", "break_continue"],
            "sursa": SURSA_WHILE,
            "continut_md": """## Repetiția condiționată

Bucla `while` repetă un bloc de cod **cât timp** condiția e adevărată:

```python
numaratoare = 5
while numaratoare > 0:
    print(numaratoare)
    numaratoare = numaratoare - 1
print("Start!")
```

La fiecare **iterație** Python: (1) evaluează condiția; (2) dacă e `True`,
execută blocul și revine la pasul 1; (3) dacă e `False`, sare după buclă.

## Bucla infinită — eroarea clasică

Dacă variabila din condiție **nu se schimbă** în corpul buclei, condiția nu
devine niciodată falsă și programul rulează la nesfârșit:

```python
n = 5
while n > 0:
    print(n)      # n nu scade niciodată → buclă infinită!
```

Regula de aur: în corpul unui `while`, ceva din condiție **trebuie** să se
modifice spre oprire.

## break și continue

- `break` — iese din buclă imediat, indiferent de condiție;
- `continue` — sare restul iterației curente și trece la următoarea.

```python
while True:                  # buclă intenționat infinită…
    comanda = input()
    if comanda == "stop":
        break                # …cu ieșire explicită
    print(f"Execut: {comanda}")
```

Tiparul `while True` + `break` e idiomatic pentru „repetă până când utilizatorul
spune stop”.

## De reținut

- `while` se folosește când NU știi dinainte de câte ori repeți;
- verifică mental: „condiția ajunge vreodată falsă?”;
- sandbox-ul platformei oprește buclele infinite după câteva secunde —
  dacă primești „timeout”, exact asta s-a întâmplat.""",
            "cod_exemplu": """# Numărătoare inversă
n = 5
while n > 0:
    print(n)
    n = n - 1          # pasul care duce bucla spre oprire
print("Start!")

# Suma cifrelor unui număr — while clasic
numar = 2026
suma = 0
while numar > 0:
    suma = suma + numar % 10   # ultima cifră
    numar = numar // 10        # taie ultima cifră
print("Suma cifrelor lui 2026:", suma)

# break: căutăm primul divizor > 1
n = 91
d = 2
while d <= n:
    if n % d == 0:
        print("Primul divizor al lui", n, "este", d)
        break
    d = d + 1""",
            "exercitii": [
                {
                    "titlu": "Suma cifrelor",
                    "enunt_md": """Programul citește un număr natural și afișează **suma cifrelor** lui.

Folosește bucla `while` cu operatorii `% 10` (ultima cifră) și `// 10`
(numărul fără ultima cifră), ca în exemplul lecției.

*Exemplu: 2026 → 2+0+2+6 = 10.*""",
                    "cod_start": "n = int(input())\nsuma = 0\n# adună cifrele lui n folosind while, % și //\n\nprint(suma)\n",
                    "solutie": "n = int(input())\nsuma = 0\nwhile n > 0:\n    suma = suma + n % 10\n    n = n // 10\nprint(suma)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["bucla_while"],
                    "teste": [
                        {"stdin": "2026\n", "asteptat": "10"},
                        {"stdin": "999\n", "asteptat": "27"},
                        {"stdin": "5\n", "asteptat": "5"},
                        {"stdin": "0\n", "asteptat": "0"},
                    ],
                },
            ],
        },
        {
            "slug": "bucla-for",
            "titlu": "Bucla for și range()",
            "ordine": 2,
            "concepte": ["bucla_for"],
            "sursa": SURSA_FOR,
            "continut_md": """## Repetiția numărată

Când știi **de câte ori** repeți (sau parcurgi o colecție element cu element),
bucla `for` e unealta potrivită:

```python
for i in range(5):
    print(i)        # 0, 1, 2, 3, 4
```

`range()` generează un interval de numere și are trei forme:

| Apel | Produce |
|------|---------|
| `range(5)` | 0, 1, 2, 3, 4 |
| `range(2, 6)` | 2, 3, 4, 5 |
| `range(10, 0, -2)` | 10, 8, 6, 4, 2 |

Regula de memorat: capătul din dreapta **nu este inclus** — `range(1, 11)`
înseamnă 1…10.

## for peste orice secvență

`for` nu e doar pentru numere — parcurge direct orice secvență:

```python
for litera in "Python":
    print(litera)

for culoare in ["roșu", "verde", "albastru"]:
    print(culoare)
```

Citește-l ca pe o propoziție: „pentru fiecare literă din «Python»…”.

## while sau for?

- numărul de pași e cunoscut sau parcurgi o colecție → `for`;
- repeți „până se întâmplă ceva” (condiție) → `while`.

## De reținut

- `range(n)` începe de la 0 și se oprește la n-1;
- variabila buclei (`i`, `litera`…) primește pe rând fiecare valoare;
- `break` și `continue` funcționează identic și în `for`.""",
            "cod_exemplu": """# Cele trei forme ale lui range
print(list(range(5)))         # [0, 1, 2, 3, 4]
print(list(range(2, 6)))      # [2, 3, 4, 5]
print(list(range(10, 0, -2))) # [10, 8, 6, 4, 2]

# Tabla înmulțirii cu 7
for i in range(1, 11):
    print(f"7 x {i} = {7 * i}")

# for parcurge direct un șir de caractere
vocale = 0
for litera in "programare":
    if litera in "aeiou":
        vocale = vocale + 1
print("Vocale în «programare»:", vocale)""",
            "exercitii": [
                {
                    "titlu": "Factorial",
                    "enunt_md": """Programul citește un număr natural `n` și afișează `n!` (factorialul):
produsul `1 × 2 × … × n`.

Folosește un `for` peste `range(1, n + 1)` și o variabilă-produs care pornește
de la 1. Prin convenție, `0! = 1`.""",
                    "cod_start": "n = int(input())\nprodus = 1\n# înmulțește produs cu fiecare i din range(1, n + 1)\n\nprint(produs)\n",
                    "solutie": "n = int(input())\nprodus = 1\nfor i in range(1, n + 1):\n    produs = produs * i\nprint(produs)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["bucla_for"],
                    "teste": [
                        {"stdin": "5\n", "asteptat": "120"},
                        {"stdin": "1\n", "asteptat": "1"},
                        {"stdin": "0\n", "asteptat": "1"},
                        {"stdin": "10\n", "asteptat": "3628800"},
                    ],
                },
            ],
        },
        {
            "slug": "acumulatori",
            "titlu": "Tipare cu acumulatori: sume, numărări, maxim",
            "ordine": 3,
            "concepte": ["acumulatori"],
            "sursa": SURSA_FOR,
            "continut_md": """## Tiparul acumulatorului

O mulțime de probleme au aceeași formă: parcurgi o secvență și **construiești
un rezultat pas cu pas** într-o variabilă numită *acumulator*:

```python
suma = 0                  # 1. inițializezi acumulatorul
for n in range(1, 101):
    suma = suma + n       # 2. îl actualizezi la fiecare pas
print(suma)               # 3. îl folosești după buclă
```

Cele trei tipare fundamentale:

**Suma / produsul** — acumulatorul pornește de la `0` (sumă) sau `1` (produs).

**Numărarea** — acumulatorul numără elementele care îndeplinesc o condiție:

```python
pare = 0
for n in [3, 8, 5, 12, 7, 4]:
    if n % 2 == 0:
        pare = pare + 1
```

**Maximul / minimul** — acumulatorul ține „recordul de până acum”:

```python
maxim = None
for n in [3, 8, 5, 12, 7]:
    if maxim is None or n > maxim:
        maxim = n
```

Pornirea de la `None` (în loc de 0) e importantă: cu numere negative,
`maxim = 0` ar da un rezultat greșit.

## Scurtătura: operatorii compuși

`suma += n` e prescurtarea lui `suma = suma + n`. Există și `-=`, `*=`, `//=`.

## De reținut

- inițializarea acumulatorului se face **înainte** de buclă, o singură dată;
- valoarea inițială depinde de operație: 0 pentru sumă, 1 pentru produs,
  `None` pentru maxim/minim;
- acest tipar reapare la șiruri, liste și dicționare — învață-l bine aici.""",
            "cod_exemplu": """# Suma 1 + 2 + ... + 100 (legenda lui Gauss)
suma = 0
for n in range(1, 101):
    suma += n
print("1 + 2 + ... + 100 =", suma)

# Numărare condiționată: câte numere pare?
numere = [3, 8, 5, 12, 7, 4, 9]
pare = 0
for n in numere:
    if n % 2 == 0:
        pare += 1
print("Numere pare:", pare)

# Maximul "manual" — recordul de până acum
maxim = None
for n in numere:
    if maxim is None or n > maxim:
        maxim = n
print("Maximul:", maxim)""",
            "exercitii": [
                {
                    "titlu": "Numărarea notelor de trecere",
                    "enunt_md": """Programul citește pe prima linie un număr `n`, apoi `n` note (câte una pe
linie). Afișează **două valori, pe linii separate**:

1. câte note sunt de trecere (≥ 5);
2. cea mai mare notă citită.

Folosește tiparul numărării și tiparul maximului, într-o singură buclă.""",
                    "cod_start": "n = int(input())\ntrecute = 0\nmaxim = None\nfor i in range(n):\n    nota = int(input())\n    # actualizează trecute și maxim\n\nprint(trecute)\nprint(maxim)\n",
                    "solutie": "n = int(input())\ntrecute = 0\nmaxim = None\nfor i in range(n):\n    nota = int(input())\n    if nota >= 5:\n        trecute += 1\n    if maxim is None or nota > maxim:\n        maxim = nota\nprint(trecute)\nprint(maxim)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["acumulatori", "bucla_for", "instructiunea_if"],
                    "teste": [
                        {"stdin": "4\n7\n4\n9\n5\n", "asteptat": "3\n9"},
                        {"stdin": "3\n2\n3\n4\n", "asteptat": "0\n4"},
                        {"stdin": "1\n10\n", "asteptat": "1\n10"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce produce `range(1, 5)`?", "corecta": "1, 2, 3, 4",
         "gresite": ["1, 2, 3, 4, 5", "0, 1, 2, 3, 4", "2, 3, 4, 5"],
         "explicatie": "Capătul din dreapta nu este inclus niciodată în range.",
         "concepte": ["bucla_for"], "dificultate": 1},
        {"text": "De câte ori se execută corpul buclei `for i in range(3):`?", "corecta": "de 3 ori",
         "gresite": ["de 4 ori", "de 2 ori", "la nesfârșit"],
         "explicatie": "range(3) produce 0, 1, 2 — trei valori, deci trei iterații.",
         "concepte": ["bucla_for"], "dificultate": 1},
        {"text": "Ce este o buclă infinită?", "corecta": "o buclă a cărei condiție nu devine niciodată falsă",
         "gresite": ["o buclă cu range foarte mare", "o buclă imbricată în alta", "o buclă fără variabilă"],
         "explicatie": "Dacă nimic din condiție nu se schimbă în corpul buclei, programul nu se mai oprește.",
         "concepte": ["bucla_while"], "dificultate": 1},
        {"text": "Ce face instrucțiunea `break`?", "corecta": "iese imediat din buclă",
         "gresite": ["sare la iterația următoare", "oprește tot programul", "șterge variabila buclei"],
         "explicatie": "break părăsește bucla curentă; continue sare doar iterația curentă.",
         "concepte": ["break_continue"], "dificultate": 1},
        {"text": "Care e diferența dintre `break` și `continue`?",
         "corecta": "break părăsește bucla; continue trece la iterația următoare",
         "gresite": ["sunt sinonime", "continue părăsește bucla; break o reia", "break funcționează doar în while"],
         "explicatie": "break = ieșire definitivă; continue = „sari peste restul acestei iterații”.",
         "concepte": ["break_continue"], "dificultate": 2},
        {"text": "Pentru suma elementelor, acumulatorul se inițializează cu…", "corecta": "0",
         "gresite": ["1", "None", "primul element, obligatoriu"],
         "explicatie": "0 e elementul neutru la adunare; 1 e pentru produs; None se folosește la max/min.",
         "concepte": ["acumulatori"], "dificultate": 1},
        {"text": "De ce e riscant să cauți maximul pornind de la `maxim = 0`?",
         "corecta": "dă rezultat greșit dacă toate numerele sunt negative",
         "gresite": ["e mai lent", "0 nu se poate compara cu int", "maximul devine mereu 0"],
         "explicatie": "Pentru [-7, -3], maximul real e -3, dar comparația cu 0 l-ar raporta pe 0.",
         "concepte": ["acumulatori"], "dificultate": 2},
        {"text": "Ce afișează: `s = 0` … `for i in range(4): s += i` … `print(s)`?", "corecta": "6",
         "gresite": ["10", "4", "0"],
         "explicatie": "range(4) = 0,1,2,3, iar 0+1+2+3 = 6.",
         "concepte": ["acumulatori", "bucla_for"], "dificultate": 2},
        {"text": "Când preferi `while` în locul lui `for`?",
         "corecta": "când nu știi dinainte de câte ori se repetă",
         "gresite": ["când parcurgi o listă", "când numărul de pași e fix", "niciodată — for e mereu mai bun"],
         "explicatie": "while = repetiție condiționată; for = repetiție numărată/peste colecții.",
         "concepte": ["bucla_while"], "dificultate": 1},
    ],
}
