"""Detectarea similarității între soluții (sprijin anti-plagiat pentru profesor).

Metodă: normalizare AST + comparare de secvențe.
1. Codul se parsează în AST; numele de variabile/funcții devin simboluri
   poziționale (v0, v1, ...), iar constantele devin tipul lor (INT, STR ...).
   Astfel redenumirea variabilelor sau schimbarea valorilor nu ascunde copierea.
2. Arborii normalizați (serializați) se compară cu difflib.SequenceMatcher.

Scorul 1.0 = structural identice. Pragul implicit de raportare: 0.90.
"""
import ast
import difflib


class _Normalizator(ast.NodeTransformer):
    """Înlocuiește numele și constantele cu simboluri canonice."""

    def __init__(self):
        self.mapare: dict[str, str] = {}

    def _simbol(self, nume: str) -> str:
        if nume not in self.mapare:
            self.mapare[nume] = f"v{len(self.mapare)}"
        return self.mapare[nume]

    def visit_Name(self, nod: ast.Name):
        return ast.copy_location(ast.Name(id=self._simbol(nod.id), ctx=nod.ctx), nod)

    def visit_arg(self, nod: ast.arg):
        return ast.copy_location(ast.arg(arg=self._simbol(nod.arg)), nod)

    def visit_FunctionDef(self, nod: ast.FunctionDef):
        self.generic_visit(nod)
        nod.name = self._simbol(nod.name)
        return nod

    def visit_ClassDef(self, nod: ast.ClassDef):
        self.generic_visit(nod)
        nod.name = self._simbol(nod.name)
        return nod

    def visit_Constant(self, nod: ast.Constant):
        eticheta = type(nod.value).__name__.upper()
        return ast.copy_location(ast.Constant(value=eticheta), nod)


def amprenta(cod: str) -> str | None:
    """Forma canonică a codului (sau None dacă nu se poate parsa)."""
    try:
        arbore = ast.parse(cod)
    except SyntaxError:
        return None
    normalizat = _Normalizator().visit(arbore)
    return ast.dump(normalizat, annotate_fields=False)


def similaritate(cod_a: str, cod_b: str) -> float:
    """Scor de similaritate structurală în [0, 1]."""
    a, b = amprenta(cod_a), amprenta(cod_b)
    if a is None or b is None:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def perechi_suspecte(submisii: list[dict], prag: float = 0.90) -> list[dict]:
    """Compară fiecare pereche de submisii și raportează perechile peste prag.

    `submisii`: [{"user_id", "nume", "cod"}] — ultima submisie acceptată per student.
    """
    amprente = [(s, amprenta(s["cod"])) for s in submisii]
    raport = []
    for i in range(len(amprente)):
        s1, a1 = amprente[i]
        if a1 is None:
            continue
        for j in range(i + 1, len(amprente)):
            s2, a2 = amprente[j]
            if a2 is None:
                continue
            scor = difflib.SequenceMatcher(None, a1, a2).ratio()
            if scor >= prag:
                raport.append({
                    "student_1": {"id": s1["user_id"], "nume": s1["nume"]},
                    "student_2": {"id": s2["user_id"], "nume": s2["nume"]},
                    "scor": round(scor, 3),
                })
    raport.sort(key=lambda r: r["scor"], reverse=True)
    return raport
