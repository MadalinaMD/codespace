# -*- coding: utf-8 -*-
"""Capitolul 4 — Funcții.
Adaptat după Think Python (Downey), cap. 3 „Functions” și cap. 6 „Fruitful functions”."""

SURSA_3 = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 3 „Functions”."
SURSA_6 = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 6 „Fruitful functions”."

CAPITOL = {
    "slug": "functii",
    "titlu": "Funcții",
    "descriere": "Împarte programele în piese reutilizabile: definire, parametri, return și domeniul de vizibilitate.",
    "ordine": 4,
    "lectii": [
        {
            "slug": "definirea-functiilor",
            "titlu": "Definirea și apelarea funcțiilor",
            "ordine": 1,
            "concepte": ["definirea_functiilor"],
            "sursa": SURSA_3,
            "continut_md": """## De ce funcții?

O **funcție** e o secvență de instrucțiuni cu nume. O definești o dată, o apelezi
de câte ori vrei. Avantajele: elimini codul duplicat, dai nume pașilor din
program și poți testa fiecare piesă separat — exact ce face platforma asta
cu exercițiile tale.

## Definire și apel

```python
def saluta():
    print("Bună!")
    print("Bine ai venit la CodeSpace.")

saluta()    # abia apelul execută corpul
saluta()    # ...și de câte ori vrei
```

Anatomia definiției:
- `def` + numele funcției + paranteze + `:`;
- corpul, indentat cu 4 spații;
- definiția **nu execută** nimic — doar „înregistrează” funcția. Execuția se
  întâmplă la **apel**: `saluta()`.

## Ordinea contează

Funcția trebuie definită **înainte** de primul apel (interpretorul citește de
sus în jos):

```python
saluta()        # NameError: name 'saluta' is not defined

def saluta():
    print("Bună!")
```

## Funcții care apelează funcții

Corpul unei funcții poate apela alte funcții — așa se construiesc programele
mari, din piese mici:

```python
def linie():
    print("-" * 20)

def antet():
    linie()
    print("  RAPORT ZILNIC")
    linie()
```

## De reținut

- definirea ≠ apelarea: fără paranteze de apel, nu se execută nimic;
- numele funcțiilor urmează regulile variabilelor (litere mici, `_`);
- docstring-ul (un șir pe primul rând al corpului) documentează funcția.""",
            "cod_exemplu": """# Definire o dată, apel de mai multe ori
def linie():
    print("=" * 24)

def antet(titlu):
    linie()
    print(" ", titlu)
    linie()

antet("RAPORT ZILNIC")
print("Totul funcționează normal.")
antet("FINAL")""",
            "exercitii": [
                {
                    "titlu": "Funcția salut",
                    "enunt_md": """Definește funcția `salut(nume)` care **returnează** (nu afișează!) șirul
`Salut, X!`, unde X este numele primit.

*Exemplu: `salut("Ana")` → `"Salut, Ana!"`.*

*Atenție la diferența return/print — testele verifică valoarea returnată.*""",
                    "cod_start": "def salut(nume):\n    # returnează șirul cerut (folosește un f-string)\n    pass\n",
                    "solutie": "def salut(nume):\n    return f\"Salut, {nume}!\"\n",
                    "mod": "functie",
                    "functie_nume": "salut",
                    "dificultate": 1,
                    "concepte": ["definirea_functiilor", "fstring"],
                    "teste": [
                        {"apel": "salut('Ana')", "asteptat": "'Salut, Ana!'"},
                        {"apel": "salut('CodeSpace')", "asteptat": "'Salut, CodeSpace!'"},
                        {"apel": "salut('')", "asteptat": "'Salut, !'"},
                    ],
                },
            ],
        },
        {
            "slug": "parametri-si-return",
            "titlu": "Parametri și valoarea de retur",
            "ordine": 2,
            "concepte": ["parametri_si_return"],
            "sursa": SURSA_6,
            "continut_md": """## Parametri: intrările funcției

Parametrii sunt variabile care primesc valori la apel:

```python
def putere(baza, exponent):
    return baza ** exponent

print(putere(2, 10))    # 1024 — baza=2, exponent=10
```

Argumentele se potrivesc cu parametrii **în ordine**.

## return: rezultatul funcției

`return` face două lucruri deodată: **oprește** execuția funcției și **trimite
înapoi** o valoare apelantului.

```python
def absolut(n):
    if n < 0:
        return -n
    return n        # se ajunge aici doar dacă n >= 0
```

Valoarea returnată poate fi salvată, folosită în expresii sau pasată altei
funcții: `rezultat = absolut(-5) * 2`.

## return vs. print — diferența crucială

```python
def dublu_print(n):
    print(n * 2)     # DOAR afișează; funcția returnează None

def dublu_return(n):
    return n * 2     # produce o valoare utilizabilă

x = dublu_print(5)   # afișează 10, dar x este None!
y = dublu_return(5)  # y este 10
```

O funcție fără `return` (sau cu `return` gol) returnează automat `None`.
Regulă practică: funcțiile **calculează și returnează**; afișarea o face
apelantul. Toate exercițiile cu mod „funcție” din platformă verifică valoarea
returnată — `print` în loc de `return` e cea mai frecventă greșeală.

## De reținut

- `return` oprește funcția pe loc — codul de după el nu se mai execută;
- poți avea mai multe `return`-uri (pe ramuri diferite);
- lipsa `return` ⇒ `None`.""",
            "cod_exemplu": """def putere(baza, exponent):
    return baza ** exponent

def absolut(n):
    if n < 0:
        return -n
    return n

# Valorile returnate intră în alte calcule
print(putere(2, 10))            # 1024
print(absolut(-7) + absolut(3)) # 10

# return vs print — experimentul-cheie
def dublu_print(n):
    print(n * 2)

x = dublu_print(5)   # afișează 10...
print(x)             # ...dar x este None!""",
            "exercitii": [
                {
                    "titlu": "Minutele din ziua",
                    "enunt_md": """Definește funcția `minute(ora, minut)` care returnează câte minute au trecut
de la miezul nopții până la ora dată.

*Exemplu: `minute(8, 30)` → `510` (8 × 60 + 30).*""",
                    "cod_start": "def minute(ora, minut):\n    pass\n",
                    "solutie": "def minute(ora, minut):\n    return ora * 60 + minut\n",
                    "mod": "functie",
                    "functie_nume": "minute",
                    "dificultate": 1,
                    "concepte": ["parametri_si_return", "operatori_aritmetici"],
                    "teste": [
                        {"apel": "minute(8, 30)", "asteptat": "510"},
                        {"apel": "minute(0, 0)", "asteptat": "0"},
                        {"apel": "minute(23, 59)", "asteptat": "1439"},
                    ],
                },
                {
                    "titlu": "Semnul numărului",
                    "enunt_md": """Definește funcția `semn(n)` care returnează:
- `1` dacă `n` este pozitiv,
- `-1` dacă `n` este negativ,
- `0` dacă `n` este zero.

Folosește mai multe `return`-uri, pe ramuri `if`/`elif`/`else`.""",
                    "cod_start": "def semn(n):\n    pass\n",
                    "solutie": "def semn(n):\n    if n > 0:\n        return 1\n    elif n < 0:\n        return -1\n    else:\n        return 0\n",
                    "mod": "functie",
                    "functie_nume": "semn",
                    "dificultate": 1,
                    "concepte": ["parametri_si_return", "instructiunea_if"],
                    "teste": [
                        {"apel": "semn(42)", "asteptat": "1"},
                        {"apel": "semn(-7)", "asteptat": "-1"},
                        {"apel": "semn(0)", "asteptat": "0"},
                    ],
                },
            ],
        },
        {
            "slug": "domeniul-de-vizibilitate",
            "titlu": "Variabile locale și domeniul de vizibilitate",
            "ordine": 3,
            "concepte": ["domeniu_vizibilitate"],
            "sursa": SURSA_3,
            "continut_md": """## Variabilele funcției sunt locale

Variabilele create **în interiorul** unei funcții (inclusiv parametrii) există
doar acolo — sunt **locale**:

```python
def calculeaza():
    rezultat = 42      # variabilă locală
    return rezultat

calculeaza()
print(rezultat)        # NameError! rezultat nu există aici
```

Când funcția se termină, variabilele ei locale dispar. La fiecare apel se
creează un mediu nou, curat.

## Citire vs. modificare

O funcție **poate citi** o variabilă globală (definită în afara ei), dar dacă îi
**atribuie** o valoare, Python creează o variabilă locală nouă cu același nume —
globala rămâne neschimbată:

```python
scor = 100

def afiseaza():
    print(scor)        # OK: citește globala → 100

def incearca_resetarea():
    scor = 0           # creează un ALT scor, local!

incearca_resetarea()
print(scor)            # tot 100
```

## Practica sănătoasă

Comunicarea cu o funcție se face prin **parametri** (intrare) și **return**
(ieșire), nu prin variabile globale. Funcțiile care depind doar de parametrii
lor sunt ușor de înțeles, testat și refolosit:

```python
def reseteaza(scor):
    return 0           # primește, calculează, returnează

scor = reseteaza(scor)
```

## De reținut

- parametrii și variabilele din corp sunt locale funcției;
- atribuirea într-o funcție NU modifică globala cu același nume;
- date înăuntru prin parametri, date afară prin return.""",
            "cod_exemplu": """scor = 100   # variabilă globală

def afiseaza_scorul():
    print("Scorul văzut din funcție:", scor)   # citirea globalei: permisă

def incearca_resetarea():
    scor = 0   # creează o variabilă LOCALĂ nouă, nu o modifică pe cea globală
    print("Scor local în funcție:", scor)

afiseaza_scorul()
incearca_resetarea()
print("Scor global după apel:", scor)   # tot 100!

# Calea corectă: parametru + return
def reseteaza(valoare):
    return 0

scor = reseteaza(scor)
print("Scor după resetarea corectă:", scor)""",
            "exercitii": [
                {
                    "titlu": "Aplicarea reducerii",
                    "enunt_md": """Definește funcția `aplica_reducere(pret, procent)` care returnează prețul
după aplicarea reducerii, **rotunjit la 2 zecimale** cu `round(valoare, 2)`.

*Exemplu: `aplica_reducere(200, 10)` → `180.0`.*

Funcția nu citește și nu modifică nimic din exterior: doar parametri și return.""",
                    "cod_start": "def aplica_reducere(pret, procent):\n    pass\n",
                    "solutie": "def aplica_reducere(pret, procent):\n    return round(pret * (100 - procent) / 100, 2)\n",
                    "mod": "functie",
                    "functie_nume": "aplica_reducere",
                    "dificultate": 2,
                    "concepte": ["domeniu_vizibilitate", "parametri_si_return"],
                    "teste": [
                        {"apel": "aplica_reducere(200, 10)", "asteptat": "180.0"},
                        {"apel": "aplica_reducere(100, 50)", "asteptat": "50.0"},
                        {"apel": "aplica_reducere(150, 0)", "asteptat": "150.0"},
                        {"apel": "aplica_reducere(80, 25)", "asteptat": "60.0"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Ce se întâmplă când Python întâlnește o definiție `def f(): ...`?",
         "corecta": "înregistrează funcția, fără să-i execute corpul",
         "gresite": ["execută imediat corpul", "verifică dacă funcția e apelată undeva", "rezervă memorie pentru rezultat"],
         "explicatie": "Corpul rulează doar la apel: f().",
         "concepte": ["definirea_functiilor"], "dificultate": 1},
        {"text": "Ce returnează o funcție care nu conține `return`?", "corecta": "None",
         "gresite": ["0", "ultima valoare calculată", "un șir gol"],
         "explicatie": "Lipsa lui return înseamnă implicit `return None`.",
         "concepte": ["parametri_si_return"], "dificultate": 1},
        {"text": "Care e diferența esențială dintre `return x` și `print(x)` într-o funcție?",
         "corecta": "return produce o valoare utilizabilă de apelant; print doar o afișează",
         "gresite": ["niciuna, sunt echivalente", "print e mai rapid", "return afișează și el pe ecran"],
         "explicatie": "Doar valoarea returnată poate fi salvată sau folosită în calcule ulterioare.",
         "concepte": ["parametri_si_return"], "dificultate": 1},
        {"text": "Ce afișează: `def f(n): return n * 2` … `x = f(3); print(x)`?", "corecta": "6",
         "gresite": ["None", "n * 2", "3"],
         "explicatie": "f(3) returnează 6, care se salvează în x.",
         "concepte": ["parametri_si_return"], "dificultate": 1},
        {"text": "Codul de după un `return` executat…", "corecta": "nu se mai execută niciodată",
         "gresite": ["se execută la următorul apel", "se execută doar în if", "produce eroare de sintaxă"],
         "explicatie": "return oprește imediat execuția funcției.",
         "concepte": ["parametri_si_return"], "dificultate": 2},
        {"text": "O variabilă definită în corpul unei funcții…",
         "corecta": "există doar pe durata apelului funcției",
         "gresite": ["e vizibilă în tot programul", "devine globală după primul apel", "se păstrează între apeluri"],
         "explicatie": "Variabilele locale se creează la apel și dispar la final.",
         "concepte": ["domeniu_vizibilitate"], "dificultate": 1},
        {"text": "Ce afișează: `x = 10` … `def f(): x = 5` … `f(); print(x)`?", "corecta": "10",
         "gresite": ["5", "None", "eroare"],
         "explicatie": "Atribuirea din f creează un x LOCAL; globala rămâne 10.",
         "concepte": ["domeniu_vizibilitate"], "dificultate": 2},
        {"text": "Cum ar trebui să comunice o funcție bine scrisă cu restul programului?",
         "corecta": "prin parametri la intrare și return la ieșire",
         "gresite": ["prin variabile globale", "prin print-uri", "prin fișiere temporare"],
         "explicatie": "Parametri + return = funcții previzibile, testabile, reutilizabile.",
         "concepte": ["domeniu_vizibilitate"], "dificultate": 1},
    ],
}
