"""Graful de concepte Python — modelul de domeniu al sistemului de tutoriat.

Fiecare concept: (slug, nume, descriere, [prerechizite]).
Prerechizitele formează un graf aciclic: un concept e "pregătit" de învățat
când prerechizitele lui au p(cunoaștere) peste pragul de fundament.
Ordinea din listă dă și ordinea pedagogică globală (câmpul `ordine`).
"""

CONCEPTE = [
    # ── Fundamente ──────────────────────────────────────────────
    ("program_si_print", "Programe și afișare",
     "Ce este un program, cum îl execută interpretorul, afișarea cu print().", []),
    ("operatori_aritmetici", "Operatori aritmetici",
     "Operațiile numerice: + - * / // % **, prioritatea operatorilor.", ["program_si_print"]),
    ("variabile", "Variabile și atribuire",
     "Nume care se referă la valori; instrucțiunea de atribuire.", ["program_si_print"]),
    ("tipuri_de_date", "Tipuri de date de bază",
     "int, float, str, bool; funcția type().", ["variabile"]),
    ("conversii_tip", "Conversii între tipuri",
     "int(), float(), str() și când sunt necesare.", ["tipuri_de_date"]),
    ("citire_input", "Citirea datelor (input)",
     "Citirea de la tastatură cu input() și conversia rezultatului.", ["conversii_tip"]),
    ("fstring", "Formatarea șirurilor (f-string)",
     "Construirea mesajelor cu f\"...{expresie}...\".", ["tipuri_de_date"]),

    # ── Decizii ─────────────────────────────────────────────────
    ("expresii_logice", "Expresii logice",
     "bool, operatori de comparație și operatorii and / or / not.", ["variabile"]),
    ("instructiunea_if", "Instrucțiunea if / elif / else",
     "Execuția condiționată și ramificarea programelor.", ["expresii_logice"]),

    # ── Repetiție ───────────────────────────────────────────────
    ("bucla_while", "Bucla while",
     "Repetiția condiționată; actualizarea variabilei de control.", ["instructiunea_if"]),
    ("bucla_for", "Bucla for și range",
     "Iterarea peste secvențe și peste intervale de numere.", ["variabile"]),
    ("break_continue", "break și continue",
     "Controlul fin al buclelor: ieșire anticipată și salt peste pași.", ["bucla_while", "bucla_for"]),
    ("acumulatori", "Tipare cu acumulatori",
     "Sume, numărări, minim/maxim construite pas cu pas într-o buclă.", ["bucla_for"]),

    # ── Funcții ─────────────────────────────────────────────────
    ("definirea_functiilor", "Definirea funcțiilor",
     "def, corpul funcției, apelul; de ce împărțim codul în funcții.", ["variabile"]),
    ("parametri_si_return", "Parametri și return",
     "Funcții cu intrări și rezultat; diferența dintre return și print.", ["definirea_functiilor"]),
    ("domeniu_vizibilitate", "Domeniul de vizibilitate",
     "Variabile locale vs. globale; durata de viață a numelor.", ["parametri_si_return"]),
    ("recursivitate", "Recursivitate",
     "Funcții care se apelează pe sine: caz de bază + pas recursiv.", ["parametri_si_return", "instructiunea_if"]),

    # ── Șiruri ──────────────────────────────────────────────────
    ("siruri_indexare", "Șiruri: indexare și feliere",
     "Accesul la caractere, slicing, len(); imutabilitatea șirurilor.", ["variabile"]),
    ("siruri_metode", "Metodele șirurilor",
     "upper, lower, strip, replace, split, join, count, find.", ["siruri_indexare"]),
    ("parcurgerea_sirurilor", "Parcurgerea șirurilor",
     "Iterarea caracter cu caracter; operatorul in.", ["siruri_indexare", "bucla_for"]),

    # ── Colecții ────────────────────────────────────────────────
    ("liste_baza", "Liste: bazele",
     "Crearea, indexarea și modificarea listelor; len și append.", ["variabile"]),
    ("liste_metode", "Metodele listelor",
     "append, insert, remove, pop, sort, sorted, sum, min, max.", ["liste_baza"]),
    ("liste_si_bucle", "Liste și bucle",
     "Parcurgerea listelor; construirea unei liste noi pas cu pas.", ["liste_baza", "bucla_for"]),
    ("tupluri", "Tupluri",
     "Secvențe imuabile; împachetare/despachetare; tuple vs. listă.", ["liste_baza"]),
    ("comprehensii", "Comprehensii de liste",
     "Construirea concisă a listelor: [expresie for x in secventa if conditie].", ["liste_si_bucle"]),
    ("dictionare", "Dicționare",
     "Perechi cheie–valoare: creare, acces, modificare, get, in.", ["liste_baza"]),
    ("dictionare_parcurgere", "Parcurgerea dicționarelor",
     "items(), keys(), values(); tiparul numărării frecvențelor.", ["dictionare", "bucla_for"]),
    ("multimi", "Mulțimi (set)",
     "Colecții de elemente unice; operații de mulțimi.", ["liste_baza"]),

    # ── Robustețe ───────────────────────────────────────────────
    ("exceptii", "Excepții: try / except",
     "Tratarea erorilor la rulare fără oprirea programului.", ["instructiunea_if"]),
    ("ridicarea_exceptiilor", "Ridicarea excepțiilor (raise)",
     "Semnalarea datelor invalide; validarea argumentelor unei funcții.", ["exceptii", "definirea_functiilor"]),

    # ── Obiecte ─────────────────────────────────────────────────
    ("clase_si_obiecte", "Clase și obiecte",
     "class, instanțierea, atribute; obiectul ca pachet de date.", ["definirea_functiilor"]),
    ("metode_si_atribute", "Metode și __init__",
     "Metode de instanță, parametrul self, constructorul __init__.", ["clase_si_obiecte"]),
    ("metode_speciale", "Metode speciale",
     "__str__ și __eq__: cum se afișează și se compară obiectele.", ["metode_si_atribute"]),

    # ── Ecosistem ───────────────────────────────────────────────
    ("module_import", "Module și import",
     "Folosirea bibliotecii standard: math, random; sintaxa import.", ["definirea_functiilor"]),
    ("json_serializare", "Serializarea JSON",
     "dumps/loads: salvarea structurilor de date ca text.", ["dictionare", "module_import"]),
]
