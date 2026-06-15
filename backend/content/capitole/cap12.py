# -*- coding: utf-8 -*-
"""Capitolul 12 — Module și JSON.
Adaptat după The Python Tutorial §6 „Modules”, §10 „Brief Tour of the Standard Library”
și documentația modulului json."""

SURSA_MODULE = "Python Software Foundation, The Python Tutorial — §6 „Modules”, §10 „Brief Tour of the Standard Library”."
SURSA_JSON = "Python Software Foundation — documentația modulului json (docs.python.org/3/library/json.html)."

CAPITOL = {
    "slug": "module-si-json",
    "titlu": "Module și JSON",
    "descriere": "Folosește biblioteca standard și schimbă date cu lumea: import, math, random și formatul JSON.",
    "ordine": 12,
    "lectii": [
        {
            "slug": "module-si-biblioteca",
            "titlu": "Module și biblioteca standard",
            "ordine": 1,
            "concepte": ["module_import"],
            "sursa": SURSA_MODULE,
            "continut_md": """## Codul altora, la un import distanță

Un **modul** e un fișier cu funcții și constante gata scrise. Python vine „cu
bateriile incluse” — o bibliotecă standard uriașă:

```python
import math

print(math.sqrt(144))     # 12.0
print(math.pi)            # 3.14159...
print(math.floor(3.9))    # 3
print(math.ceil(3.1))     # 4
```

Sintaxa `modul.functie()` spune clar de unde vine fiecare nume.

## Variante de import

```python
import math                  # tot modulul; apel: math.sqrt(x)
from math import sqrt, pi    # doar anumite nume; apel: sqrt(x)
```

A doua formă scurtează codul, dar pierde „adresa” numelui — pentru început,
`import modul` e mai clar.

## random: numere aleatoare

```python
import random

random.randint(1, 6)            # întreg din [1, 6] — zarul
random.choice(["a", "b", "c"])  # un element la întâmplare
random.shuffle(lista)           # amestecă lista pe loc
```

(Pe platformă, exercițiile cu random se testează greu — îl folosești în
playground; testele automate preferă funcții deterministe.)

## Alte module de știut

- `datetime` — date și ore; `statistics` — medie, mediană;
- `collections.Counter` — frecvențele dintr-o secvență, gata făcute:

```python
from collections import Counter
Counter("abracadabra").most_common(2)   # [('a', 5), ('b', 2)]
```

Da — idiomul frecvențelor pe care l-ai scris manual există în bibliotecă.
L-ai învățat manual ca să înțelegi CE face; de acum poți folosi unealta.

## De reținut

- `import modul`, apoi `modul.functie()`;
- explorează biblioteca standard înainte să reinventezi roata;
- numele modulului ≠ numele fișierului tău (nu-ți numi fișierul `math.py`!).""",
            "cod_exemplu": """import math
import random
from collections import Counter

# math: instrumentele matematice
print(math.sqrt(2) * math.sqrt(2))   # ~2.0
print(math.gcd(12, 18))              # 6 — cel mai mare divizor comun

# random: simulăm 10 aruncări de zar
aruncari = [random.randint(1, 6) for _ in range(10)]
print("Aruncări:", aruncari)

# Counter: frecvențele, instant
print(Counter(aruncari))
print(Counter("abracadabra").most_common(2))""",
            "exercitii": [
                {
                    "titlu": "Ipotenuza",
                    "enunt_md": """Definește funcția `ipotenuza(a, b)` care returnează lungimea ipotenuzei
unui triunghi dreptunghic cu catetele `a` și `b`, **rotunjită la 2 zecimale**.

Folosește `math.sqrt` (sau `math.hypot`) — modulul `math` e permis la import.

*Exemplu: `ipotenuza(3, 4)` → `5.0`.*""",
                    "cod_start": "import math\n\ndef ipotenuza(a, b):\n    pass\n",
                    "solutie": "import math\n\ndef ipotenuza(a, b):\n    return round(math.sqrt(a * a + b * b), 2)\n",
                    "mod": "functie",
                    "functie_nume": "ipotenuza",
                    "dificultate": 1,
                    "concepte": ["module_import"],
                    "teste": [
                        {"apel": "ipotenuza(3, 4)", "asteptat": "5.0"},
                        {"apel": "ipotenuza(1, 1)", "asteptat": "1.41"},
                        {"apel": "ipotenuza(6, 8)", "asteptat": "10.0"},
                    ],
                },
            ],
        },
        {
            "slug": "json-salvarea-datelor",
            "titlu": "JSON: schimbul și salvarea datelor",
            "ordine": 2,
            "concepte": ["json_serializare"],
            "sursa": SURSA_JSON,
            "continut_md": """## Ce este JSON?

**JSON** (JavaScript Object Notation) e formatul-text standard în care
aplicațiile schimbă date — orice API web vorbește JSON. Arată aproape ca
dicționarele și listele Python:

```json
{"nume": "Ana", "note": [9, 10], "activ": true}
```

Diferențe mici: `true/false/null` (nu `True/False/None`), doar ghilimele
duble, cheile obligatoriu șiruri.

## Serializare: Python → text

```python
import json

student = {"nume": "Ana", "note": [9, 10], "activ": True}
text = json.dumps(student)
# '{"nume": "Ana", "note": [9, 10], "activ": true}'
```

`dumps` („dump string”) transformă dicționare, liste, numere, șiruri și
booleeni într-un șir JSON. Obiectele claselor tale NU se serializează direct —
le transformi întâi în dicționare.

## Deserializare: text → Python

```python
date = json.loads('{"oras": "Cluj", "populatie": 286000}')
print(date["oras"])           # Cluj — un dicționar normal
```

`loads` ridică `json.JSONDecodeError` pentru text invalid — încă un loc unde
`try/except` își câștigă pâinea.

## Dus-întors

`loads(dumps(x))` reconstruiește structura: echipa din spatele unui joc își
salvează astfel progresul, iar platforma asta exact așa îți stochează
răspunsurile testelor adaptive.

Un detaliu: tuplurile devin liste la drumul prin JSON — formatul nu are
noțiunea de tuplu.

## De reținut

- `dumps` = către text, `loads` = dinspre text;
- JSON acoperă: dict, listă, str, numere, bool, None;
- datele de la utilizatori/API se validează cu try/except la `loads`.""",
            "cod_exemplu": """import json

# Serializare: structura Python devine text
student = {"nume": "Ana", "note": [9, 10, 8], "activ": True}
text = json.dumps(student)
print(text)
print(type(text))            # <class 'str'>

# Deserializare: textul redevine structură
inapoi = json.loads(text)
print(inapoi["note"])        # [9, 10, 8]
print(sum(inapoi["note"]) / len(inapoi["note"]))

# Textul invalid se tratează cu except
try:
    json.loads("{nu e json}")
except json.JSONDecodeError as e:
    print("JSON invalid:", e)""",
            "exercitii": [
                {
                    "titlu": "Media din JSON",
                    "enunt_md": """Definește funcția `media_din_json(text)` care primește un șir JSON de forma
`'{"nume": "...", "note": [...]}'` și returnează media notelor, rotunjită la
2 zecimale.

Dacă textul nu e JSON valid sau lista de note e goală, returnează `None`.

*Exemplu: `media_din_json('{"nume": "Ana", "note": [9, 10]}')` → `9.5`.*""",
                    "cod_start": "import json\n\ndef media_din_json(text):\n    pass\n",
                    "solutie": "import json\n\ndef media_din_json(text):\n    try:\n        date = json.loads(text)\n        note = date[\"note\"]\n        if not note:\n            return None\n        return round(sum(note) / len(note), 2)\n    except (json.JSONDecodeError, KeyError, TypeError):\n        return None\n",
                    "mod": "functie",
                    "functie_nume": "media_din_json",
                    "dificultate": 3,
                    "concepte": ["json_serializare", "exceptii"],
                    "teste": [
                        {"apel": "media_din_json('{\"nume\": \"Ana\", \"note\": [9, 10]}')", "asteptat": "9.5"},
                        {"apel": "media_din_json('{\"nume\": \"Dan\", \"note\": []}')", "asteptat": "None"},
                        {"apel": "media_din_json('nu e json')", "asteptat": "None"},
                        {"apel": "media_din_json('{\"nume\": \"Ema\", \"note\": [7, 8, 10]}')", "asteptat": "8.33"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Cum apelezi funcția sqrt după `import math`?", "corecta": "math.sqrt(x)",
         "gresite": ["sqrt(x)", "import.sqrt(x)", "math->sqrt(x)"],
         "explicatie": "Cu `import math`, numele rămân în spațiul modulului: math.functie().",
         "concepte": ["module_import"], "dificultate": 1},
        {"text": "Ce permite `from math import sqrt`?", "corecta": "apelul direct sqrt(x), fără prefix",
         "gresite": ["importul întregului modul de două ori", "redenumirea modulului", "doar citirea documentației"],
         "explicatie": "from...import aduce numele alese direct în spațiul tău de nume.",
         "concepte": ["module_import"], "dificultate": 1},
        {"text": "Ce returnează `random.randint(1, 6)`?",
         "corecta": "un întreg aleator din intervalul [1, 6], inclusiv capetele",
         "gresite": ["un întreg din [1, 6)", "un float din [1, 6]", "mereu 6"],
         "explicatie": "Spre deosebire de range, randint include ambele capete.",
         "concepte": ["module_import"], "dificultate": 2},
        {"text": "Ce face `Counter(\"banana\")` din modulul collections?",
         "corecta": "numără frecvența fiecărui caracter",
         "gresite": ["numără doar vocalele", "sortează literele", "elimină duplicatele"],
         "explicatie": "Counter automatizează exact tiparul frecvențelor: {'a': 3, 'n': 2, 'b': 1}.",
         "concepte": ["module_import"], "dificultate": 2},
        {"text": "Ce face `json.dumps(date)`?", "corecta": "transformă structura Python într-un șir JSON",
         "gresite": ["citește un fișier JSON", "transformă text JSON în dicționar", "validează un JSON"],
         "explicatie": "dumps = serializare (către text); loads = deserializare (dinspre text).",
         "concepte": ["json_serializare"], "dificultate": 1},
        {"text": "Ce produce `json.loads('{\"x\": 1}')`?", "corecta": "dicționarul {'x': 1}",
         "gresite": ["șirul '{\"x\": 1}'", "lista ['x', 1]", "eroare — cheile JSON nu pot fi șiruri"],
         "explicatie": "loads parsează textul JSON și reconstruiește structura Python.",
         "concepte": ["json_serializare"], "dificultate": 1},
        {"text": "Cum apare valoarea Python `True` într-un text JSON?", "corecta": "true",
         "gresite": ["True", "\"True\"", "1, întotdeauna"],
         "explicatie": "JSON folosește true/false/null cu literă mică.",
         "concepte": ["json_serializare"], "dificultate": 2},
        {"text": "Ce excepție ridică `json.loads` pentru text invalid?",
         "corecta": "json.JSONDecodeError", "gresite": ["ValueError... mereu altul", "KeyError", "ImportError"],
         "explicatie": "JSONDecodeError (subclasă de ValueError) semnalează parsarea eșuată.",
         "concepte": ["json_serializare", "exceptii"], "dificultate": 2},
    ],
}
