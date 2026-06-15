# -*- coding: utf-8 -*-
"""Capitolul 11 — Clase și obiecte.
Adaptat după Think Python (Downey), cap. 15–17 („Classes and objects",
„Classes and functions", „Classes and methods")."""

SURSA = "Adaptat după A. B. Downey, Think Python (ed. 2), O'Reilly, 2015 — cap. 15–17."

CAPITOL = {
    "slug": "clase-si-obiecte",
    "titlu": "Clase și obiecte",
    "descriere": "Programarea orientată pe obiecte: tipuri definite de tine, cu date și comportament la un loc.",
    "ordine": 11,
    "lectii": [
        {
            "slug": "primele-clase",
            "titlu": "Primele clase: tipuri definite de programator",
            "ordine": 1,
            "concepte": ["clase_si_obiecte"],
            "sursa": SURSA,
            "continut_md": """## De ce clase?

Ai lucrat cu tipurile altora: `int`, `str`, `list`. O **clasă** îți permite să
definești PROPRIUL tip — un șablon care grupează date înrudite sub un nume:

```python
class Punct:
    \"\"\"Un punct în planul 2D.\"\"\"

punct = Punct()      # instanțiere: creăm un OBIECT de tip Punct
punct.x = 3          # atribute: variabile „atașate” obiectului
punct.y = 4
print(punct.x)       # 3
```

Vocabularul esențial:
- **clasa** = șablonul (`Punct`);
- **obiectul / instanța** = un exemplar concret (`punct`);
- **atributele** = variabilele obiectului (`punct.x`).

## Mai multe obiecte, aceeași clasă

Fiecare instanță are atributele EI, independente:

```python
a = Punct(); a.x, a.y = 0, 0
b = Punct(); b.x, b.y = 3, 4
# a și b nu se influențează reciproc
```

## Obiectele ca argumente de funcții

Un obiect circulă prin program ca orice valoare:

```python
def distanta_de_origine(p):
    return (p.x ** 2 + p.y ** 2) ** 0.5

print(distanta_de_origine(b))    # 5.0
```

Observă ce câștigăm: în loc să plimbăm perechi `(x, y)` prin tot programul,
plimbăm UN obiect cu nume clar.

## Obiectele sunt mutabile

Ca listele: două variabile pot referi același obiect, iar modificarea printr-una
se vede prin cealaltă (aliasing). `copy.copy(obiect)` face o copie.

## De reținut

- clasa definește tipul; instanțierea `Clasa()` creează obiecte;
- atributele se accesează cu punct: `obiect.atribut`;
- convenție: numele claselor cu MajusculăLaFiecareCuvânt.""",
            "cod_exemplu": """class Punct:
    \"\"\"Un punct în planul 2D.\"\"\"

# Două obiecte independente
origine = Punct()
origine.x = 0
origine.y = 0

varf = Punct()
varf.x = 3
varf.y = 4

def distanta(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

print("Distanța:", distanta(origine, varf))   # 5.0

# Obiectele sunt mutabile — atenție la aliasing
alias = varf
alias.x = 100
print("varf.x după modificarea prin alias:", varf.x)""",
            "exercitii": [
                {
                    "titlu": "Dreptunghiul",
                    "enunt_md": """Mai jos e definită clasa `Dreptunghi` (goală). Definește funcția
`aria(dreptunghi)` care primește un obiect cu atributele `latime` și
`inaltime` și returnează aria lui.

*Testele creează obiecte, le setează atributele și apelează funcția ta.*""",
                    "cod_start": "class Dreptunghi:\n    \"\"\"Un dreptunghi cu latime si inaltime.\"\"\"\n\ndef aria(dreptunghi):\n    pass\n",
                    "solutie": "class Dreptunghi:\n    \"\"\"Un dreptunghi cu latime si inaltime.\"\"\"\n\ndef aria(dreptunghi):\n    return dreptunghi.latime * dreptunghi.inaltime\n",
                    "mod": "functie",
                    "functie_nume": "aria",
                    "dificultate": 1,
                    "concepte": ["clase_si_obiecte"],
                    "teste": [
                        {"apel": "(lambda d: (setattr(d, 'latime', 3), setattr(d, 'inaltime', 4), aria(d))[-1])(Dreptunghi())", "asteptat": "12"},
                        {"apel": "(lambda d: (setattr(d, 'latime', 5), setattr(d, 'inaltime', 5), aria(d))[-1])(Dreptunghi())", "asteptat": "25"},
                    ],
                },
            ],
        },
        {
            "slug": "init-si-metode",
            "titlu": "__init__ și metodele: obiecte cu comportament",
            "ordine": 2,
            "concepte": ["metode_si_atribute"],
            "sursa": SURSA,
            "continut_md": """## Constructorul __init__

Setarea manuală a atributelor e fragilă. Metoda specială `__init__` rulează
**automat la instanțiere** și inițializează obiectul dintr-o mișcare:

```python
class Punct:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Punct(3, 4)      # __init__ primește 3 și 4
```

## self: obiectul însuși

`self` e primul parametru al oricărei metode și înseamnă „obiectul pe care
s-a apelat metoda”. La apel NU îl scrii tu — Python îl completează:

```python
p.deplaseaza(1, 2)        # Python apelează Punct.deplaseaza(p, 1, 2)
```

`self.x = x` se citește: „atributul x AL ACESTUI obiect primește valoarea
parametrului x”.

## Metode: funcții care „aparțin” obiectului

```python
class Punct:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distanta_de_origine(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def deplaseaza(self, dx, dy):
        self.x += dx
        self.y += dy

p = Punct(3, 4)
print(p.distanta_de_origine())   # 5.0
p.deplaseaza(1, -1)
```

Datele (`x`, `y`) și operațiile pe ele (`deplaseaza`) stau ÎMPREUNĂ — asta e
esența programării orientate pe obiecte: **încapsularea**.

## De reținut

- `__init__` = inițializare automată la `Clasa(argumente)`;
- toate metodele primesc `self` primul; uitarea lui e eroarea clasică
  („takes 0 positional arguments but 1 was given”);
- atribut fără `self.` = variabilă locală care DISPARE la finalul metodei.""",
            "cod_exemplu": """class ContBancar:
    def __init__(self, titular, sold_initial):
        self.titular = titular
        self.sold = sold_initial

    def depune(self, suma):
        self.sold += suma

    def retrage(self, suma):
        if suma > self.sold:
            raise ValueError("Fonduri insuficiente")
        self.sold -= suma

cont = ContBancar("Ana", 100)
cont.depune(50)
cont.retrage(30)
print(f"{cont.titular} are {cont.sold} lei")   # Ana are 120 lei

try:
    cont.retrage(1000)
except ValueError as e:
    print("Refuzat:", e)""",
            "exercitii": [
                {
                    "titlu": "Clasa Student",
                    "enunt_md": """Definește clasa `Student` cu:

- `__init__(self, nume)` — salvează numele și pornește cu lista de note goală;
- metoda `adauga_nota(self, nota)` — adaugă nota în listă;
- metoda `media(self)` — returnează media notelor, sau `0` dacă nu există note.

*Testele creează studenți, adaugă note și verifică media.*""",
                    "cod_start": "class Student:\n    def __init__(self, nume):\n        pass\n\n    def adauga_nota(self, nota):\n        pass\n\n    def media(self):\n        pass\n",
                    "solutie": "class Student:\n    def __init__(self, nume):\n        self.nume = nume\n        self.note = []\n\n    def adauga_nota(self, nota):\n        self.note.append(nota)\n\n    def media(self):\n        if not self.note:\n            return 0\n        return sum(self.note) / len(self.note)\n",
                    "mod": "functie",
                    "functie_nume": "Student",
                    "dificultate": 2,
                    "concepte": ["metode_si_atribute"],
                    "teste": [
                        {"apel": "(lambda s: (s.adauga_nota(9), s.adauga_nota(7), s.media())[-1])(Student('Ana'))", "asteptat": "8.0"},
                        {"apel": "Student('Dan').media()", "asteptat": "0"},
                        {"apel": "(lambda s: (s.adauga_nota(10), s.media())[-1])(Student('Ema'))", "asteptat": "10.0"},
                        {"apel": "Student('Ion').nume", "asteptat": "'Ion'"},
                    ],
                },
            ],
        },
        {
            "slug": "metode-speciale",
            "titlu": "Metode speciale: __str__ și __eq__",
            "ordine": 3,
            "concepte": ["metode_speciale"],
            "sursa": SURSA,
            "continut_md": """## Cum se afișează un obiect?

Implicit, `print(obiect)` afișează ceva inutil: `<__main__.Punct object at
0x...>`. Metoda specială `__str__` definește reprezentarea „omenească”:

```python
class Punct:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

print(Punct(3, 4))     # (3, 4)
```

`print`, `str()` și f-string-urile apelează automat `__str__`.

## Când sunt două obiecte „egale”?

Implicit, `==` compară IDENTITATEA (același obiect în memorie), nu conținutul:

```python
Punct(1, 2) == Punct(1, 2)     # False?! — sunt obiecte diferite
```

Metoda `__eq__` definește egalitatea de conținut:

```python
    def __eq__(self, celalalt):
        return self.x == celalalt.x and self.y == celalalt.y
```

Acum `Punct(1, 2) == Punct(1, 2)` → `True`.

## Imaginea de ansamblu

Metodele cu dublu underscore („dunder”) sunt **protocolul** prin care
obiectele tale se integrează în limbaj: `__init__` (creare), `__str__`
(afișare), `__eq__` (comparare) — și multe altele (`__len__`, `__add__`…)
pe care le vei întâlni mai târziu. Tipurile built-in exact asta fac:
`len(lista)` apelează `lista.__len__()`.

## De reținut

- `__str__` returnează (nu afișează!) un șir;
- fără `__eq__`, `==` înseamnă „același obiect”, nu „aceleași date”;
- metodele speciale se apelează SINGURE, prin sintaxa limbajului.""",
            "cod_exemplu": """class Punct:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __eq__(self, celalalt):
        return self.x == celalalt.x and self.y == celalalt.y

a = Punct(3, 4)
b = Punct(3, 4)

print(a)              # (3, 4) — __str__ în acțiune
print(f"Punctul {b}") # și în f-string-uri

print(a == b)         # True — __eq__ compară conținutul
print(a is b)         # False — sunt obiecte diferite în memorie""",
            "exercitii": [
                {
                    "titlu": "Fracția",
                    "enunt_md": """Definește clasa `Fractie` cu:

- `__init__(self, numarator, numitor)`;
- `__str__` care returnează `"numarator/numitor"` (ex: `"3/4"`);
- `__eq__` care consideră egale fracțiile **echivalente matematic**
  (compară `a/b` cu `c/d` prin produsul în cruce: `a*d == b*c`).""",
                    "cod_start": "class Fractie:\n    def __init__(self, numarator, numitor):\n        pass\n\n    def __str__(self):\n        pass\n\n    def __eq__(self, celalalt):\n        pass\n",
                    "solutie": "class Fractie:\n    def __init__(self, numarator, numitor):\n        self.numarator = numarator\n        self.numitor = numitor\n\n    def __str__(self):\n        return f\"{self.numarator}/{self.numitor}\"\n\n    def __eq__(self, celalalt):\n        return self.numarator * celalalt.numitor == self.numitor * celalalt.numarator\n",
                    "mod": "functie",
                    "functie_nume": "Fractie",
                    "dificultate": 3,
                    "concepte": ["metode_speciale"],
                    "teste": [
                        {"apel": "str(Fractie(3, 4))", "asteptat": "'3/4'"},
                        {"apel": "Fractie(1, 2) == Fractie(2, 4)", "asteptat": "True"},
                        {"apel": "Fractie(1, 2) == Fractie(2, 3)", "asteptat": "False"},
                        {"apel": "str(Fractie(7, 1))", "asteptat": "'7/1'"},
                    ],
                },
            ],
        },
    ],
    "intrebari": [
        {"text": "Care e relația dintre clasă și obiect?",
         "corecta": "clasa e șablonul; obiectul e o instanță concretă a lui",
         "gresite": ["sunt sinonime", "obiectul e șablonul clasei", "clasa există doar la rulare"],
         "explicatie": "Dintr-o clasă se pot crea oricâte obiecte, fiecare cu atributele lui.",
         "concepte": ["clase_si_obiecte"], "dificultate": 1},
        {"text": "Ce face linia `p = Punct()`?",
         "corecta": "creează o instanță nouă a clasei Punct",
         "gresite": ["definește clasa Punct", "apelează metoda p", "copiază clasa în p"],
         "explicatie": "Parantezele după numele clasei instanțiază un obiect nou.",
         "concepte": ["clase_si_obiecte"], "dificultate": 1},
        {"text": "Când se execută metoda `__init__`?",
         "corecta": "automat, la crearea fiecărui obiect",
         "gresite": ["o singură dată, la definirea clasei", "doar dacă o apelezi explicit", "la print(obiect)"],
         "explicatie": "Clasa(argumente) creează obiectul și îi apelează __init__ cu acele argumente.",
         "concepte": ["metode_si_atribute"], "dificultate": 1},
        {"text": "Ce reprezintă `self` într-o metodă?",
         "corecta": "obiectul pe care a fost apelată metoda",
         "gresite": ["clasa însăși", "o variabilă globală", "primul argument dat de utilizator"],
         "explicatie": "La p.metoda(x), Python apelează Clasa.metoda(p, x) — self este p.",
         "concepte": ["metode_si_atribute"], "dificultate": 1},
        {"text": "Ce eroare clasică produce uitarea lui `self` din definiția unei metode?",
         "corecta": "TypeError: takes 0 positional arguments but 1 was given",
         "gresite": ["SyntaxError la definire", "NameError la import", "nicio eroare"],
         "explicatie": "Python pasează automat obiectul ca prim argument — care nu mai are unde să intre.",
         "concepte": ["metode_si_atribute"], "dificultate": 2},
        {"text": "Ce metodă specială folosește `print(obiect)`?", "corecta": "__str__",
         "gresite": ["__print__", "__init__", "__show__"],
         "explicatie": "print(x) afișează str(x), care apelează x.__str__().",
         "concepte": ["metode_speciale"], "dificultate": 1},
        {"text": "Fără `__eq__` definit, ce compară `obiect1 == obiect2`?",
         "corecta": "identitatea — dacă sunt același obiect în memorie",
         "gresite": ["toate atributele, automat", "adresele de email", "rezultatul lui __str__"],
         "explicatie": "Implicit, == pe obiecte e ca operatorul is; __eq__ definește egalitatea de conținut.",
         "concepte": ["metode_speciale"], "dificultate": 2},
        {"text": "Metoda `__str__` trebuie să…", "corecta": "returneze un șir de caractere",
         "gresite": ["afișeze direct cu print", "returneze obiectul", "modifice atributele"],
         "explicatie": "__str__ DESCRIE obiectul; afișarea propriu-zisă o face print.",
         "concepte": ["metode_speciale"], "dificultate": 1},
    ],
}
