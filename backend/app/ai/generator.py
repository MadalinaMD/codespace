"""Generatorul de conținut pentru profesor — cu validare automată și aprobare umană.

Fluxul (human-in-the-loop):
1. profesorul cere întrebări/un exercițiu pentru un concept;
2. LLM-ul generează; ieșirea se validează STRUCTURAL (câmpuri complete) și,
   pentru exerciții, prin EXECUȚIE: soluția de referință generată trebuie să
   treacă toate testele generate, în sandbox — altfel schița e marcată invalidă;
3. schița ajunge în panoul profesorului, care o aprobă sau o respinge;
4. doar la aprobare conținutul intră în curs (și indexul RAG se reconstruiește).
"""
import json
import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import rag
from app.ai.llm import obtine_llm, text_din_continut
from app.ai.tutor import valideaza_intrebari_generate
from app.engine import sandbox
from app.models import (Capitol, Concept, Exercitiu, Intrebare, Lectie,
                        SchitaGenerata, TestExercitiu)

PROMPT_EXERCITIU = """Ești profesor de Python. Creează UN exercițiu de programare în ROMÂNĂ pentru conceptul „{concept}”, dificultate {dificultate}/3, pornind de la materialul de mai jos.

MATERIAL:
{context}

Răspunde STRICT cu un JSON valid (fără text în plus, fără markdown):
{{
  "titlu": "Titlu scurt",
  "enunt_md": "Cerința în Markdown: ce trebuie să facă funcția, cu un exemplu.",
  "functie_nume": "nume_functie",
  "cod_start": "def nume_functie(...):\\n    # completează\\n    pass\\n",
  "solutie": "def nume_functie(...):\\n    ...\\n",
  "teste": [{{"apel": "nume_functie(argumente)", "asteptat": "rezultat ca literal Python"}}]
}}

Reguli: exact 4-6 teste care acoperă și cazuri-limită; `asteptat` e un literal Python valid (număr, șir cu ghilimele, listă...); soluția folosește doar Python standard; enunțul nu dezvăluie soluția."""


def _extrage_obiect_json(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    inceput, sfarsit = text.find("{"), text.rfind("}")
    if inceput != -1 and sfarsit != -1:
        text = text[inceput:sfarsit + 1]
    return json.loads(text)


def genereaza_intrebari(db: Session, concept: Concept, capitol_id: int | None,
                        numar: int) -> list[SchitaGenerata]:
    llm = obtine_llm()
    if llm is None:
        raise RuntimeError("Generatorul necesită o cheie API Gemini configurată.")
    from app.ai.tutor import PROMPT_TEST
    context, _ = rag.index.context_si_surse(concept.nume, k=3)
    brut = text_din_continut(llm.invoke(PROMPT_TEST.format(
        numar=numar, concept=concept.nume,
        context=context or concept.descriere or concept.nume,
    )).content)
    intrebari = valideaza_intrebari_generate(brut)[:numar]
    if not intrebari:
        raise RuntimeError("AI-ul nu a produs întrebări valide. Încearcă din nou.")

    schite = []
    for intrebare in intrebari:
        schita = SchitaGenerata(
            tip="intrebare", concept_slug=concept.slug, capitol_id=capitol_id,
            payload_json=intrebare, validat=True,
            raport_validare="Validare structurală trecută (text, corectă, 3 greșite).",
        )
        db.add(schita)
        schite.append(schita)
    db.flush()
    return schite


def genereaza_exercitiu(db: Session, concept: Concept, capitol_id: int | None,
                        dificultate: int = 2) -> SchitaGenerata:
    llm = obtine_llm()
    if llm is None:
        raise RuntimeError("Generatorul necesită o cheie API Gemini configurată.")
    context, _ = rag.index.context_si_surse(concept.nume, k=3)
    brut = text_din_continut(llm.invoke(PROMPT_EXERCITIU.format(
        concept=concept.nume, dificultate=dificultate,
        context=context or concept.descriere or concept.nume,
    )).content)

    payload = _extrage_obiect_json(brut)
    necesare = {"titlu", "enunt_md", "functie_nume", "cod_start", "solutie", "teste"}
    lipsa = necesare - set(payload)
    if lipsa:
        raise RuntimeError(f"AI-ul a omis câmpurile: {', '.join(sorted(lipsa))}.")
    teste = [t for t in payload["teste"]
             if isinstance(t, dict) and t.get("apel") and t.get("asteptat") is not None]
    if len(teste) < 3:
        raise RuntimeError("AI-ul a produs prea puține teste valide (minim 3).")
    payload["teste"] = [{"apel": str(t["apel"]), "asteptat": str(t["asteptat"])} for t in teste]

    # Validarea prin execuție: soluția de referință trebuie să treacă testele
    rezultat = sandbox.ruleaza_teste(payload["solutie"], payload["teste"], mod="functie")
    validat = rezultat.status == "acceptat"
    if validat:
        raport = f"Soluția de referință trece toate cele {rezultat.teste_total} teste generate."
    else:
        raport = (f"INVALID: {rezultat.teste_trecute}/{rezultat.teste_total} teste trec "
                  f"({rezultat.eroare_categorie or 'rezultate diferite'}). "
                  "Exercițiul nu poate fi aprobat în forma aceasta.")

    schita = SchitaGenerata(
        tip="exercitiu", concept_slug=concept.slug, capitol_id=capitol_id,
        payload_json={**payload, "dificultate": dificultate},
        validat=validat, raport_validare=raport,
    )
    db.add(schita)
    db.flush()
    return schita


def aproba_schita(db: Session, schita: SchitaGenerata) -> dict:
    """Transformă o schiță aprobată în conținut real de curs."""
    concept = db.execute(
        select(Concept).where(Concept.slug == schita.concept_slug)
    ).scalar_one_or_none()

    if schita.tip == "intrebare":
        capitol_id = schita.capitol_id
        if capitol_id is None:
            lectie = _lectie_pentru_concept(db, concept)
            capitol_id = lectie.capitol_id if lectie else db.execute(
                select(Capitol.id).order_by(Capitol.ordine)).scalars().first()
        intrebare = Intrebare(
            capitol_id=capitol_id,
            text=schita.payload_json["text"],
            varianta_corecta=schita.payload_json["corecta"],
            gresite_json=schita.payload_json["gresite"],
            explicatie=schita.payload_json.get("explicatie", ""),
            sursa="ai",
        )
        if concept:
            intrebare.concepte = [concept]
        db.add(intrebare)
        db.flush()
        schita.stare = "aprobata"
        return {"tip": "intrebare", "id": intrebare.id}

    if not schita.validat:
        raise ValueError("Schița nu a trecut validarea prin execuție și nu poate fi aprobată.")
    lectie = _lectie_pentru_concept(db, concept)
    if lectie is None:
        raise ValueError("Nu există o lecție pentru acest concept — exercițiul nu are unde să fie atașat.")
    payload = schita.payload_json
    ordine = db.execute(
        select(func.coalesce(func.max(Exercitiu.ordine), 0))
        .where(Exercitiu.lectie_id == lectie.id)
    ).scalar_one() + 1
    exercitiu = Exercitiu(
        lectie_id=lectie.id, titlu=payload["titlu"], enunt_md=payload["enunt_md"],
        cod_start=payload["cod_start"], solutie_referinta=payload["solutie"],
        mod="functie", functie_nume=payload["functie_nume"],
        dificultate=int(payload.get("dificultate", 2)), ordine=ordine,
    )
    if concept:
        exercitiu.concepte = [concept]
    db.add(exercitiu)
    db.flush()
    for i, test in enumerate(payload["teste"], start=1):
        db.add(TestExercitiu(exercitiu_id=exercitiu.id, ordine=i,
                             apel=test["apel"], asteptat=test["asteptat"]))
    schita.stare = "aprobata"
    return {"tip": "exercitiu", "id": exercitiu.id, "lectie_slug": lectie.slug}


def _lectie_pentru_concept(db: Session, concept: Concept | None) -> Lectie | None:
    if concept is None:
        return None
    return db.execute(
        select(Lectie).join(Lectie.concepte).where(Concept.id == concept.id)
        .join(Capitol, Lectie.capitol_id == Capitol.id)
        .order_by(Capitol.ordine, Lectie.ordine)
    ).scalars().first()
