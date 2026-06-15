"""Taxonomia erorilor Python — clasificare pentru feedback și analiza misconcepțiilor.

Fiecare submisie eșuată primește o categorie de eroare. Categoriile alimentează:
1. feedback-ul imediat pentru student (explicație prietenoasă + sfat)
2. statistica "greșelile tale frecvente" din profil
3. analiza misconcepțiilor la nivel de clasă (panoul profesorului)
"""

# categorie -> (titlu RO, explicație prietenoasă, sfat de remediere)
CATEGORII = {
    "sintaxa": (
        "Eroare de sintaxă",
        "Python nu a putut interpreta codul — o paranteză, un două puncte sau ghilimele lipsesc ori sunt în plus.",
        "Citește linia indicată în eroare și pe cea de dinaintea ei. Verifică parantezele pereche și `:` la finalul lui if/for/def.",
    ),
    "indentare": (
        "Eroare de indentare",
        "Blocurile de cod din Python se delimitează prin indentare (spații la început de linie), iar aici nivelurile nu se aliniază.",
        "Folosește consecvent 4 spații pentru fiecare nivel. Tot ce e în interiorul unui if/for/def stă mai la dreapta cu un nivel.",
    ),
    "nume_nedefinit": (
        "Nume nedefinit (NameError)",
        "Codul folosește o variabilă sau o funcție care nu a fost definită până în acel punct.",
        "Verifică ortografia numelui și ordinea: definirea trebuie să apară înainte de utilizare.",
    ),
    "tip_incompatibil": (
        "Tipuri incompatibile (TypeError)",
        "O operație a primit un tip de date nepotrivit — de exemplu adunarea unui număr cu un șir de caractere.",
        "Afișează tipurile cu type() și convertește explicit cu int(), str() sau float() unde e nevoie.",
    ),
    "valoare": (
        "Valoare invalidă (ValueError)",
        "Tipul e corect, dar valoarea nu poate fi procesată — de exemplu int(\"abc\").",
        "Validează datele înainte de conversie sau tratează cazul cu try/except.",
    ),
    "index": (
        "Index în afara listei (IndexError)",
        "Codul accesează o poziție care nu există în listă sau în șir.",
        "Amintește-ți că indexarea începe de la 0: ultimul element e la poziția len(x) - 1.",
    ),
    "cheie": (
        "Cheie inexistentă (KeyError)",
        "Dicționarul nu conține cheia accesată.",
        "Verifică existența cheii cu `cheie in dictionar` sau folosește .get(cheie, valoare_implicita).",
    ),
    "atribut": (
        "Atribut inexistent (AttributeError)",
        "Obiectul nu are metoda sau atributul apelat — adesea un indiciu că variabila are alt tip decât crezi.",
        "Verifică tipul variabilei cu type() și caută metoda potrivită tipului respectiv.",
    ),
    "impartire_la_zero": (
        "Împărțire la zero (ZeroDivisionError)",
        "O împărțire sau un modulo a primit 0 ca al doilea operand.",
        "Tratează separat cazul în care numitorul poate fi 0, cu un if înainte de împărțire.",
    ),
    "recursivitate_infinita": (
        "Recursivitate fără oprire (RecursionError)",
        "Funcția se apelează pe sine la nesfârșit — lipsește cazul de bază sau nu se ajunge niciodată la el.",
        "Asigură-te că există un caz de bază care returnează direct și că fiecare apel se apropie de el.",
    ),
    "bucla_infinita": (
        "Programul nu se termină (timeout)",
        "Execuția a depășit limita de timp — cel mai probabil o buclă while a cărei condiție nu devine niciodată falsă.",
        "Verifică dacă variabila din condiția buclei chiar se modifică în interiorul buclei.",
    ),
    "import_blocat": (
        "Modul nepermis",
        "Soluția importă un modul care nu este permis în acest exercițiu.",
        "Rezolvă exercițiul cu instrumentele de bază ale limbajului și modulele permise (math, random, json...).",
    ),
    "cod_periculos": (
        "Construcție nepermisă",
        "Codul folosește funcții rezervate mediului (ex. open, exec, eval) care nu sunt necesare exercițiilor.",
        "Rezolvă exercițiul folosind doar construcțiile predate în lecții.",
    ),
    "raspuns_gresit": (
        "Testele nu trec",
        "Codul rulează fără erori, dar rezultatele diferă de cele așteptate.",
        "Compară atent rezultatul obținut cu cel așteptat la primul test picat și urmărește calculul pas cu pas.",
    ),
    "alta_eroare": (
        "Eroare la execuție",
        "Programul s-a oprit cu o excepție.",
        "Citește mesajul erorii de jos în sus: ultima linie spune tipul, iar cele de deasupra arată unde a apărut.",
    ),
}

# Maparea excepțiilor Python pe categorii
_EXCEPTII = {
    "SyntaxError": "sintaxa",
    "IndentationError": "indentare",
    "TabError": "indentare",
    "NameError": "nume_nedefinit",
    "UnboundLocalError": "nume_nedefinit",
    "TypeError": "tip_incompatibil",
    "ValueError": "valoare",
    "IndexError": "index",
    "KeyError": "cheie",
    "AttributeError": "atribut",
    "ZeroDivisionError": "impartire_la_zero",
    "RecursionError": "recursivitate_infinita",
}


def clasifica_exceptie(tip_exceptie: str) -> str:
    """Mapează numele unei excepții Python pe o categorie din taxonomie."""
    return _EXCEPTII.get(tip_exceptie, "alta_eroare")


def descrie(categorie: str) -> dict:
    """Titlul, explicația și sfatul asociate unei categorii de eroare."""
    titlu, explicatie, sfat = CATEGORII.get(categorie, CATEGORII["alta_eroare"])
    return {"categorie": categorie, "titlu": titlu, "explicatie": explicatie, "sfat": sfat}
