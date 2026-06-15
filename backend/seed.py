"""Popularea bazei de date cu cursul — cu AUTOVALIDAREA conținutului.

Poarta de calitate: înainte de a intra în baza de date, fiecare exercițiu
este verificat prin EXECUȚIE — soluția de referință trebuie să treacă toate
testele în sandbox. Un exercițiu cu teste greșite oprește seed-ul cu un
raport precis, deci cursul publicat nu poate conține exerciții nerezolvabile.

Rulare:
    python seed.py            # populează o bază goală
    python seed.py --reset    # șterge baza existentă și o reconstruiește
"""
import os
import sys

from sqlalchemy import select

from app import config
from app.bootstrap import asigura_date_minime
from app.db import SesiuneLocala
from app.engine import sandbox
from app.models import (Capitol, Concept, Exercitiu, Intrebare, Lectie,
                        TestExercitiu)
from content import CAPITOLE, CONCEPTE


def _valideaza_exercitiu(exercitiu: dict, eticheta: str) -> None:
    """Rulează soluția de referință contra testelor; eșecul oprește seed-ul."""
    rezultat = sandbox.ruleaza_teste(
        exercitiu["solutie"], exercitiu["teste"], mod=exercitiu["mod"])
    if rezultat.status != "acceptat":
        print(f"\n[SEED][EROARE] Exercițiul „{eticheta}” NU trece propriile teste!")
        print(f"  status: {rezultat.status}  "
              f"({rezultat.teste_trecute}/{rezultat.teste_total} teste)")
        if rezultat.eroare_mesaj:
            print(f"  eroare: {rezultat.eroare_mesaj}")
        for r in rezultat.rezultate:
            if not r.get("trecut"):
                print(f"  test picat: {r.get('descriere')} -> obținut {r.get('obtinut')}, "
                      f"așteptat {r.get('asteptat')}")
        sys.exit(1)


def _verifica_slugurile_conceptelor(slugs_valide: set) -> None:
    """Orice referință la un concept inexistent (typo) oprește seed-ul."""
    probleme = []
    for capitol in CAPITOLE:
        for lectie in capitol["lectii"]:
            for slug in lectie["concepte"]:
                if slug not in slugs_valide:
                    probleme.append(f"lecția „{lectie['slug']}”: concept necunoscut „{slug}”")
            for exercitiu in lectie.get("exercitii", []):
                for slug in exercitiu["concepte"]:
                    if slug not in slugs_valide:
                        probleme.append(f"exercițiul „{exercitiu['titlu']}”: concept necunoscut „{slug}”")
        for intrebare in capitol["intrebari"]:
            for slug in intrebare["concepte"]:
                if slug not in slugs_valide:
                    probleme.append(f"întrebarea „{intrebare['text'][:40]}…”: concept necunoscut „{slug}”")
    if probleme:
        print("[SEED][EROARE] Referințe către concepte inexistente:")
        for p in probleme:
            print("  -", p)
        sys.exit(1)


def populeaza() -> None:
    asigura_date_minime()
    db = SesiuneLocala()
    try:
        existente = db.execute(select(Capitol).limit(1)).scalar_one_or_none()
        if existente is not None:
            print("[SEED] Baza conține deja cursul. Folosește `python seed.py --reset` "
                  "pentru a o reconstrui de la zero (ATENȚIE: șterge și progresul).")
            return

        # 1. Graful de concepte (noduri, apoi muchiile de prerechizit)
        slugs = {slug for slug, *_ in CONCEPTE}
        _verifica_slugurile_conceptelor(slugs)

        concepte: dict[str, Concept] = {}
        for ordine, (slug, nume, descriere, _) in enumerate(CONCEPTE):
            concept = Concept(slug=slug, nume=nume, descriere=descriere, ordine=ordine)
            db.add(concept)
            concepte[slug] = concept
        db.flush()
        for slug, _, _, prerechizite in CONCEPTE:
            concepte[slug].prerechizite = [concepte[p] for p in prerechizite]
        db.flush()

        # 2. Capitole → lecții → exerciții (validate) → întrebări
        nr_lectii = nr_exercitii = nr_teste = nr_intrebari = 0
        for date_capitol in CAPITOLE:
            capitol = Capitol(slug=date_capitol["slug"], titlu=date_capitol["titlu"],
                              descriere=date_capitol["descriere"],
                              ordine=date_capitol["ordine"])
            db.add(capitol)
            db.flush()

            for date_lectie in date_capitol["lectii"]:
                lectie = Lectie(
                    capitol_id=capitol.id, slug=date_lectie["slug"],
                    titlu=date_lectie["titlu"], ordine=date_lectie["ordine"],
                    continut_md=date_lectie["continut_md"],
                    cod_exemplu=date_lectie["cod_exemplu"],
                    sursa=date_lectie["sursa"],
                )
                lectie.concepte = [concepte[s] for s in date_lectie["concepte"]]
                db.add(lectie)
                db.flush()
                nr_lectii += 1

                for ordine_ex, date_ex in enumerate(date_lectie.get("exercitii", []), start=1):
                    eticheta = f"{date_lectie['slug']} / {date_ex['titlu']}"
                    _valideaza_exercitiu(date_ex, eticheta)

                    exercitiu = Exercitiu(
                        lectie_id=lectie.id, titlu=date_ex["titlu"],
                        enunt_md=date_ex["enunt_md"], cod_start=date_ex["cod_start"],
                        solutie_referinta=date_ex["solutie"], mod=date_ex["mod"],
                        functie_nume=date_ex["functie_nume"],
                        dificultate=date_ex["dificultate"], ordine=ordine_ex,
                    )
                    exercitiu.concepte = [concepte[s] for s in date_ex["concepte"]]
                    db.add(exercitiu)
                    db.flush()
                    nr_exercitii += 1

                    for ordine_t, test in enumerate(date_ex["teste"], start=1):
                        db.add(TestExercitiu(
                            exercitiu_id=exercitiu.id, ordine=ordine_t,
                            apel=test.get("apel"), stdin=test.get("stdin"),
                            asteptat=test.get("asteptat", ""),
                            asteptat_eroare=test.get("eroare"),
                        ))
                        nr_teste += 1
                    print(f"[SEED] OK  {eticheta}")

            for date_i in date_capitol["intrebari"]:
                intrebare = Intrebare(
                    capitol_id=capitol.id, text=date_i["text"],
                    varianta_corecta=date_i["corecta"], gresite_json=date_i["gresite"],
                    explicatie=date_i["explicatie"],
                    dificultate=date_i.get("dificultate", 1), sursa="manual",
                )
                intrebare.concepte = [concepte[s] for s in date_i["concepte"]]
                db.add(intrebare)
                nr_intrebari += 1

        db.commit()
        print("\n[SEED] Curs publicat cu succes:")
        print(f"  {len(CONCEPTE)} concepte  ·  {len(CAPITOLE)} capitole  ·  "
              f"{nr_lectii} lecții  ·  {nr_exercitii} exerciții "
              f"({nr_teste} teste, toate validate prin execuție)  ·  "
              f"{nr_intrebari} întrebări")
        print(f"  Profesor: {config.PROFESOR_EMAIL} / {config.PROFESOR_PAROLA}")
        print(f"  Student demo: {config.STUDENT_DEMO_EMAIL} / {config.STUDENT_DEMO_PAROLA}")
    finally:
        db.close()


if __name__ == "__main__":
    if "--reset" in sys.argv and os.path.exists(config.DB_PATH):
        os.remove(config.DB_PATH)
        print(f"[SEED] Baza veche ștearsă: {config.DB_PATH}")
    populeaza()
