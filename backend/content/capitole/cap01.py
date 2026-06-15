# -*- coding: utf-8 -*-
"""Capitolul 1 — Primii pași în Python.
Adaptat după Think Python (Downey), cap. 1–2 și The Python Tutorial, §3."""

SURSA_DOWNEY_1 = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 1 „The way of the program”."
SURSA_DOWNEY_2 = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 2 „Variables, expressions and statements”."
SURSA_TUTORIAL_3 = "Python Software Foundation, The Python Tutorial, §3 „An Informal Introduction to Python”."

CAPITOL = {
    "slug": "primii-pasi",
    "titlu": "Primii pași în Python",
    "descriere": "Ce este un program, cum afișezi rezultate, cum lucrezi cu numere, variabile și date citite de la tastatură.",
    "ordine": 1,
    "lectii": [
        {
            "slug": "ce-este-un-program",
            "titlu": "Ce este un program? print() și calcule",
            "ordine": 1,
            "concepte": ["program_si_print", "operatori_aritmetici"],
            "sursa": SURSA_DOWNEY_1,
            "continut_md": """## Ce este un program?

Un **program** este o secvență de instrucțiuni care descriu, pas cu pas, un calcul.
Python este un limbaj **interpretat**: interpretorul citește codul linie cu linie,
de sus în jos, și execută fiecare instrucțiune imediat.

Prima instrucțiune pe care o înveți este `print()` — afișează o valoare pe ecran:

```python
print("Salut, lume!")
print(42)
```

Textul dintre ghilimele se numește **șir de caractere** (string). Ghilimelele nu se
afișează — ele doar delimitează textul.

## Comentariile

Liniile care încep cu `#` sunt **comentarii**: interpretorul le ignoră complet.
Le folosim ca să explicăm codul pentru oameni.

```python
# Acest rând nu face nimic — e doar o notiță
print("Dar acesta se execută")  # comentariu la finalul liniei
```

## Python ca un calculator

Operatorii aritmetici lucrează ca în matematică, cu câteva simboluri speciale:

| Operator | Semnificație | Exemplu | Rezultat |
|----------|--------------|---------|----------|
| `+` `-` `*` | adunare, scădere, înmulțire | `7 * 6` | `42` |
| `/` | împărțire reală | `17 / 3` | `5.666…` |
| `//` | împărțire întreagă | `17 // 3` | `5` |
| `%` | restul împărțirii (modulo) | `17 % 3` | `2` |
| `**` | ridicare la putere | `2 ** 10` | `1024` |

Prioritatea operatorilor e cea din matematică (parantezele câștigă întotdeauna):
`1 + 2 * 3` este `7`, dar `(1 + 2) * 3` este `9`.

## De reținut

- `/` produce întotdeauna un număr zecimal (`10 / 2` este `5.0`, nu `5`);
- `%` e surprinzător de util: `n % 2` este `0` exact când `n` e par;
- o expresie scrisă singură pe o linie nu afișează nimic într-un program —
  pentru a vedea rezultatul, folosește `print()`.""",
            "cod_exemplu": """# Primul tău program: rulează-l și urmărește fiecare linie
print("Salut, CodeSpace!")

print(7 * 6)        # înmulțire
print(17 / 3)       # împărțire reală: 5.666...
print(17 // 3)      # împărțire întreagă: 5
print(17 % 3)       # restul: 2
print(2 ** 10)      # 2 la puterea 10

# Prioritatea operatorilor
print(1 + 2 * 3)    # 7
print((1 + 2) * 3)  # 9""",
            "exercitii": [
                {
                    "titlu": "Calcule cu print",
                    "enunt_md": """Scrie un program care afișează, **în această ordine, câte una pe linie**:

1. câte minute are o zi (folosește o înmulțire, nu valoarea direct);
2. câtul împărțirii întregi a lui `2026` la `7`;
3. restul împărțirii lui `2026` la `7`.""",
                    "cod_start": "# 1. minutele dintr-o zi (24 de ore × 60 de minute)\n\n# 2. câtul împărțirii întregi 2026 // 7\n\n# 3. restul împărțirii 2026 % 7\n",
                    "solutie": "print(24 * 60)\nprint(2026 // 7)\nprint(2026 % 7)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 1,
                    "concepte": ["program_si_print", "operatori_aritmetici"],
                    "teste": [
                        {"stdin": "", "asteptat": "1440\n289\n3"},
                    ],
                },
            ],
        },
        {
            "slug": "variabile-si-tipuri",
            "titlu": "Variabile și tipuri de date",
            "ordine": 2,
            "concepte": ["variabile", "tipuri_de_date"],
            "sursa": SURSA_DOWNEY_2,
            "continut_md": """## Variabile: nume pentru valori

O **variabilă** este un nume care se referă la o valoare. O creezi printr-o
**instrucțiune de atribuire**:

```python
varsta = 20
nume = "Ana"
pi_aproximativ = 3.14
```

Citește `=` ca „primește valoarea”, nu ca egalitatea din matematică. De aceea
`x = x + 1` are sens: „noul x primește vechiul x plus 1”.

```python
scor = 10
scor = scor + 5   # acum scor este 15
```

## Reguli pentru nume

- pot conține litere, cifre și `_`, dar nu pot **începe** cu o cifră;
- contează literele mari/mici: `Nume` și `nume` sunt variabile diferite;
- alege nume care spun ce conțin: `pret_total`, nu `pt`.

## Tipurile de bază

Fiecare valoare are un **tip**. Cele patru tipuri fundamentale:

| Tip | Ce reprezintă | Exemple |
|-----|---------------|---------|
| `int` | numere întregi | `5`, `-3`, `100` |
| `float` | numere zecimale | `3.14`, `2.0` |
| `str` | text (șiruri) | `"Ana"`, `'Python'` |
| `bool` | adevărat/fals | `True`, `False` |

Funcția `type()` îți spune tipul oricărei valori:

```python
print(type(42))       # <class 'int'>
print(type("42"))     # <class 'str'>  ← atenție: ghilimele = text!
```

## Capcana clasică

`"42"` (text) și `42` (număr) sunt valori complet diferite. `"2" + "3"` lipește
textele (`"23"`), pe când `2 + 3` adună numerele (`5`). Multe erori de început
vin exact de aici.""",
            "cod_exemplu": """# Variabilele păstrează valori între instrucțiuni
nume = "Ana"
varsta = 20
inaltime = 1.68
este_studenta = True

print(nume, "are", varsta, "ani")
print(type(nume), type(varsta), type(inaltime), type(este_studenta))

# Reatribuirea: x = x + 1 are sens în programare
scor = 10
scor = scor + 5
print("Scor final:", scor)

# Text vs. număr — diferența esențială
print(2 + 3)       # 5      (adunare)
print("2" + "3")   # 23     (lipire de texte)""",
            "exercitii": [
                {
                    "titlu": "Schimb de valori",
                    "enunt_md": """Programul primește **două linii** de intrare: două cuvinte.

Citește-le în variabilele `a` și `b` (cu `input()`), **interschimbă** valorile
celor două variabile, apoi afișează-le: `a` pe prima linie, `b` pe a doua.

*Indiciu: ai nevoie de o a treia variabilă, „de schimb” — sau de trucul Python
`a, b = b, a`.*""",
                    "cod_start": "a = input()\nb = input()\n# interschimbă valorile lui a și b, apoi afișează-le\n",
                    "solutie": "a = input()\nb = input()\na, b = b, a\nprint(a)\nprint(b)\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 1,
                    "concepte": ["variabile"],
                    "teste": [
                        {"stdin": "mar\npara\n", "asteptat": "para\nmar"},
                        {"stdin": "unu\ndoi\n", "asteptat": "doi\nunu"},
                    ],
                },
            ],
        },
        {
            "slug": "conversii-si-input",
            "titlu": "Conversii de tip și citirea datelor",
            "ordine": 3,
            "concepte": ["conversii_tip", "citire_input", "fstring"],
            "sursa": SURSA_DOWNEY_2 + " " + SURSA_TUTORIAL_3,
            "continut_md": """## Conversii între tipuri

Funcțiile `int()`, `float()` și `str()` transformă o valoare dintr-un tip în altul:

```python
int("42")      # 42        (text → întreg)
float("3.5")   # 3.5       (text → zecimal)
int(3.99)      # 3         (taie zecimalele, NU rotunjește)
str(42)        # "42"      (număr → text)
```

Dacă textul nu arată ca un număr, conversia eșuează cu `ValueError`:
`int("abc")` oprește programul. (Vom învăța să tratăm asta la capitolul de excepții.)

## Citirea datelor: input()

`input()` oprește programul și așteaptă o linie de la tastatură. Rezultatul este
**întotdeauna un șir de caractere**, chiar dacă utilizatorul tastează cifre:

```python
varsta_text = input()        # utilizatorul scrie: 20
varsta = int(varsta_text)    # conversia e OBLIGATORIE pentru calcule
print(varsta + 1)            # 21
```

Greșeala clasică: `input() + 1` → `TypeError`, pentru că aduni text cu număr.

## f-string: mesaje frumoase

Un **f-string** (format string) inserează valori direct în text — pui `f` înainte
de ghilimele și expresiile între acolade:

```python
nume = "Ana"
varsta = 20
print(f"{nume} va avea {varsta + 1} ani anul viitor.")
# Ana va avea 21 ani anul viitor.
```

Poți controla și zecimalele: `f"{3.14159:.2f}"` → `"3.14"`.

## De reținut

- `input()` returnează mereu `str` — convertește înainte de calcule;
- `int("3.5")` eșuează! Pentru text zecimal folosește `float()`;
- f-string-urile sunt modul modern și lizibil de a construi mesaje.""",
            "cod_exemplu": """# Conversii: ce devine fiecare valoare?
print(int("42") + 1)      # 43
print(int(3.99))          # 3  — taie, nu rotunjește
print(float("2.5") * 2)   # 5.0
print(str(42) + "!")      # 42!

# f-string: valori inserate în text
produs = "caiet"
pret = 12.5
bucati = 3
print(f"{bucati} x {produs} = {bucati * pret:.2f} lei")

# Simulăm input() aici cu o valoare fixă:
varsta = int("20")
print(f"La anul vei avea {varsta + 1} ani.")""",
            "exercitii": [
                {
                    "titlu": "Media a trei note",
                    "enunt_md": """Programul citește **trei numere întregi** (note), fiecare pe o linie.

Afișează media lor aritmetică cu **exact două zecimale**, folosind un f-string
cu formatul `:.2f`.

Exemplu: pentru notele `9`, `10`, `8` se afișează `9.00`.""",
                    "cod_start": "nota1 = int(input())\nnota2 = int(input())\nnota3 = int(input())\n# calculează media și afișeaz-o cu două zecimale\n",
                    "solutie": "nota1 = int(input())\nnota2 = int(input())\nnota3 = int(input())\nmedia = (nota1 + nota2 + nota3) / 3\nprint(f\"{media:.2f}\")\n",
                    "mod": "program",
                    "functie_nume": None,
                    "dificultate": 2,
                    "concepte": ["citire_input", "conversii_tip", "fstring"],
                    "teste": [
                        {"stdin": "9\n10\n8\n", "asteptat": "9.00"},
                        {"stdin": "10\n10\n10\n", "asteptat": "10.00"},
                        {"stdin": "5\n6\n7\n", "asteptat": "6.00"},
                        {"stdin": "7\n8\n8\n", "asteptat": "7.67"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce afișează `print(17 // 3)`?", "corecta": "5",
         "gresite": ["5.666666666666667", "2", "6"],
         "explicatie": "`//` este împărțirea întreagă: păstrează doar câtul, fără zecimale.",
         "concepte": ["operatori_aritmetici"], "dificultate": 1},
        {"text": "Ce afișează `print(17 % 3)`?", "corecta": "2",
         "gresite": ["5", "5.67", "51"],
         "explicatie": "`%` (modulo) dă restul împărțirii: 17 = 3×5 + 2.",
         "concepte": ["operatori_aritmetici"], "dificultate": 1},
        {"text": "Care este rezultatul expresiei `1 + 2 * 3`?", "corecta": "7",
         "gresite": ["9", "6", "123"],
         "explicatie": "Înmulțirea are prioritate față de adunare: 1 + (2×3) = 7.",
         "concepte": ["operatori_aritmetici"], "dificultate": 1},
        {"text": "Ce tip are valoarea `\"42\"`?", "corecta": "str",
         "gresite": ["int", "float", "bool"],
         "explicatie": "Ghilimelele fac din 42 un șir de caractere (text), nu un număr.",
         "concepte": ["tipuri_de_date"], "dificultate": 1},
        {"text": "Ce afișează `print(\"2\" + \"3\")`?", "corecta": "23",
         "gresite": ["5", "eroare", "2 3"],
         "explicatie": "Pentru șiruri, `+` înseamnă concatenare (lipire), nu adunare.",
         "concepte": ["tipuri_de_date"], "dificultate": 1},
        {"text": "Ce valoare are `x` după instrucțiunile `x = 5` și `x = x + 2`?",
         "corecta": "7", "gresite": ["5", "2", "eroare — x nu poate apărea în ambele părți"],
         "explicatie": "Atribuirea se citește „x primește vechiul x plus 2”: 5 + 2 = 7.",
         "concepte": ["variabile"], "dificultate": 1},
        {"text": "Ce returnează ÎNTOTDEAUNA funcția `input()`?", "corecta": "un șir de caractere (str)",
         "gresite": ["un întreg (int)", "tipul potrivit valorii tastate", "un float"],
         "explicatie": "input() returnează mereu text; conversia la număr e responsabilitatea programatorului.",
         "concepte": ["citire_input"], "dificultate": 1},
        {"text": "Ce afișează `print(int(3.99))`?", "corecta": "3",
         "gresite": ["4", "3.99", "eroare"],
         "explicatie": "int() taie partea zecimală (trunchiere), nu rotunjește.",
         "concepte": ["conversii_tip"], "dificultate": 2},
        {"text": "Care expresie produce textul `Am 20 ani` folosind variabila `v = 20`?",
         "corecta": "f\"Am {v} ani\"", "gresite": ["\"Am {v} ani\"", "f\"Am v ani\"", "\"Am \" + v + \" ani\""],
         "explicatie": "f-string-ul cere prefixul f și expresia între acolade; varianta cu + eșuează (text + int).",
         "concepte": ["fstring"], "dificultate": 2},
        {"text": "Ce se întâmplă la `int(\"abc\")`?", "corecta": "se ridică ValueError",
         "gresite": ["rezultă 0", "rezultă None", "se ridică TypeError"],
         "explicatie": "Tipul argumentului (str) e acceptat, dar valoarea nu poate fi interpretată ca număr → ValueError.",
         "concepte": ["conversii_tip"], "dificultate": 2},
    ],
}
