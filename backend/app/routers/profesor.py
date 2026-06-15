"""Panoul profesorului: analitica clasei, integritate academică și gestiunea conținutului.

Toate rutele cer rolul `profesor`.
"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.ai import generator, rag
from app.deps import cu_limita_ai, get_db, profesor_curent
from app.engine import similarity
from app.engine.errors import CATEGORII
from app.models import (ActivitateZi, Capitol, Concept, EvenimentXP,
                        Exercitiu, Intrebare, Lectie, SchitaGenerata,
                        StareConcept, Submisie, Utilizator)
from app.schemas import CerereGenerare, EditareLectie, IntrebareNoua
from app.security import cripteaza_parola, genereaza_parola_temporara

router = APIRouter(prefix="/profesor", tags=["profesor"],
                   dependencies=[Depends(profesor_curent)])


# ── Privire de ansamblu ─────────────────────────────────────────
@router.get("/ansamblu")
def ansamblu(db: Session = Depends(get_db)):
    numar = lambda model: db.execute(select(func.count()).select_from(model)).scalar_one()
    submisii_total = numar(Submisie)
    submisii_ok = db.execute(
        select(func.count()).select_from(Submisie).where(Submisie.status == "acceptat")
    ).scalar_one()
    return {
        "studenti": db.execute(select(func.count()).select_from(Utilizator)
                               .where(Utilizator.rol == "student")).scalar_one(),
        "lectii": numar(Lectie),
        "exercitii": numar(Exercitiu),
        "intrebari": db.execute(select(func.count()).select_from(Intrebare)
                                .where(Intrebare.activa)).scalar_one(),
        "intrebari_ai": db.execute(select(func.count()).select_from(Intrebare)
                                   .where(Intrebare.activa, Intrebare.sursa == "ai")).scalar_one(),
        "submisii_total": submisii_total,
        "procent_acceptare": round(submisii_ok / submisii_total * 100) if submisii_total else 0,
        "schite_in_asteptare": db.execute(
            select(func.count()).select_from(SchitaGenerata)
            .where(SchitaGenerata.stare == "propusa")).scalar_one(),
    }


# ── Studenți + detecția riscului ────────────────────────────────
@router.get("/studenti")
def studenti(db: Session = Depends(get_db)):
    lista = db.execute(
        select(Utilizator).where(Utilizator.rol == "student").order_by(Utilizator.id)
    ).scalars().all()

    xp_map = dict(db.execute(
        select(EvenimentXP.user_id, func.sum(EvenimentXP.puncte))
        .group_by(EvenimentXP.user_id)).all())
    exercitii_map = dict(db.execute(
        select(Submisie.user_id, func.count(func.distinct(Submisie.exercitiu_id)))
        .where(Submisie.status == "acceptat").group_by(Submisie.user_id)).all())
    ultima_zi_map = dict(db.execute(
        select(ActivitateZi.user_id, func.max(ActivitateZi.zi))
        .group_by(ActivitateZi.user_id)).all())

    stari = db.execute(select(StareConcept).where(StareConcept.nr_observatii > 0)).scalars().all()
    medie_map: dict[int, list[float]] = {}
    for stare in stari:
        medie_map.setdefault(stare.user_id, []).append(stare.p_cunoastere)

    rezultat = []
    azi = date.today()
    for student in lista:
        valori = medie_map.get(student.id, [])
        medie = round(sum(valori) / len(valori), 2) if valori else None
        ultima_zi = ultima_zi_map.get(student.id)
        zile_inactiv = (azi - date.fromisoformat(ultima_zi)).days if ultima_zi else None

        motive = []
        if ultima_zi is None:
            if (datetime.now() - student.creat_la).days >= 7:
                motive.append("nicio activitate de la înscriere")
        elif zile_inactiv is not None and zile_inactiv >= 7:
            motive.append(f"inactiv de {zile_inactiv} zile")
        if medie is not None and len(valori) >= 5 and medie < 0.4:
            motive.append(f"măiestrie medie scăzută ({round(medie * 100)}%)")

        xp = xp_map.get(student.id, 0) or 0
        rezultat.append({
            "id": student.id,
            "nume": student.nume,
            "email": student.email,
            "creat_la": student.creat_la,
            "ultima_activitate": ultima_zi,
            "xp": xp,
            "medie_maiestrie": medie,
            "concepte_observate": len(valori),
            "exercitii_rezolvate": exercitii_map.get(student.id, 0),
            "la_risc": bool(motive),
            "motive_risc": motive,
        })
    rezultat.sort(key=lambda s: (not s["la_risc"], -(s["xp"])))
    return rezultat


@router.post("/studenti/{user_id}/reseteaza-parola")
def reseteaza_parola(user_id: int, db: Session = Depends(get_db)):
    """Generează o parolă temporară pentru un student (vizibilă doar profesorului)."""
    student = db.get(Utilizator, user_id)
    if student is None or student.rol != "student":
        raise HTTPException(status_code=404, detail="Studentul nu există.")
    parola_noua = genereaza_parola_temporara()
    student.parola_hash = cripteaza_parola(parola_noua)
    db.commit()
    return {"mesaj": f"Parola pentru {student.nume} a fost resetată.",
            "parola_temporara": parola_noua}


@router.delete("/studenti/{user_id}")
def sterge_student(user_id: int, db: Session = Depends(get_db)):
    student = db.get(Utilizator, user_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Studentul nu există.")
    if student.rol == "profesor":
        raise HTTPException(status_code=403, detail="Contul de profesor nu poate fi șters.")
    db.delete(student)  # tabelele dependente au ondelete=CASCADE
    db.commit()
    return {"mesaj": "Contul studentului a fost șters."}


# ── Analitica de clasă ──────────────────────────────────────────
@router.get("/heatmap")
def heatmap_concepte(db: Session = Depends(get_db)):
    """Măiestria medie a clasei pe fiecare concept — unde se împotmolește grupul."""
    concepte = db.execute(select(Concept).order_by(Concept.ordine)).scalars().all()
    stari = db.execute(select(StareConcept).where(StareConcept.nr_observatii > 0)).scalars().all()
    pe_concept: dict[int, list[float]] = {}
    for stare in stari:
        pe_concept.setdefault(stare.concept_id, []).append(stare.p_cunoastere)
    return [{
        "slug": c.slug,
        "nume": c.nume,
        "ordine": c.ordine,
        "studenti": len(pe_concept.get(c.id, [])),
        "medie_p": round(sum(v) / len(v), 2) if (v := pe_concept.get(c.id)) else None,
        "procent_stapanire": round(
            sum(1 for p in v if p >= config.PRAG_STAPANIRE) / len(v) * 100
        ) if (v := pe_concept.get(c.id)) else None,
    } for c in concepte]


@router.get("/erori")
def erori_clasa(db: Session = Depends(get_db)):
    """Categoriile de erori cele mai frecvente la nivel de clasă (misconcepții)."""
    erori = db.execute(
        select(Submisie.eroare_categorie, func.count())
        .where(Submisie.eroare_categorie.isnot(None))
        .group_by(Submisie.eroare_categorie)
        .order_by(func.count().desc())
    ).all()
    total = sum(n for _, n in erori) or 1
    return [{
        "categorie": categorie,
        "titlu": CATEGORII.get(categorie, CATEGORII["alta_eroare"])[0],
        "numar": numar,
        "procent": round(numar / total * 100),
    } for categorie, numar in erori]


@router.get("/exercitii")
def lista_exercitii(db: Session = Depends(get_db)):
    exercitii = db.execute(
        select(Exercitiu).options(selectinload(Exercitiu.lectie))
        .order_by(Exercitiu.lectie_id, Exercitiu.ordine)
    ).scalars().all()
    return [{"id": e.id, "titlu": e.titlu, "lectie": e.lectie.titlu} for e in exercitii]


@router.get("/similaritate/{exercitiu_id}")
def similaritate_exercitiu(exercitiu_id: int, db: Session = Depends(get_db)):
    """Perechile de soluții suspect de asemănătoare la un exercițiu (AST normalizat)."""
    exercitiu = db.get(Exercitiu, exercitiu_id)
    if exercitiu is None:
        raise HTTPException(status_code=404, detail="Exercițiul nu există.")

    submisii = db.execute(
        select(Submisie).where(Submisie.exercitiu_id == exercitiu_id,
                               Submisie.status == "acceptat")
        .order_by(Submisie.user_id, Submisie.id.desc())
    ).scalars().all()
    ultima_per_student: dict[int, Submisie] = {}
    for submisie in submisii:
        ultima_per_student.setdefault(submisie.user_id, submisie)

    utilizatori = {u.id: u.nume for u in db.execute(select(Utilizator)).scalars().all()}
    intrari = [{"user_id": uid, "nume": utilizatori.get(uid, f"#{uid}"), "cod": s.cod}
               for uid, s in ultima_per_student.items()]
    return {
        "exercitiu": exercitiu.titlu,
        "solutii_comparate": len(intrari),
        "perechi_suspecte": similarity.perechi_suspecte(intrari),
    }


# ── Generatorul de conținut (cu aprobare umană) ─────────────────
@router.get("/schite")
def lista_schite(db: Session = Depends(get_db)):
    schite = db.execute(
        select(SchitaGenerata).where(SchitaGenerata.stare == "propusa")
        .order_by(SchitaGenerata.id.desc())
    ).scalars().all()
    return [{
        "id": s.id, "tip": s.tip, "concept_slug": s.concept_slug,
        "payload": s.payload_json, "validat": s.validat,
        "raport_validare": s.raport_validare, "creat_la": s.creat_la,
    } for s in schite]


def _concept_dupa_slug(db: Session, slug: str) -> Concept:
    concept = db.execute(select(Concept).where(Concept.slug == slug)).scalar_one_or_none()
    if concept is None:
        raise HTTPException(status_code=404, detail="Conceptul nu există.")
    return concept


@router.post("/genereaza/intrebari")
def genereaza_intrebari(date: CerereGenerare, db: Session = Depends(get_db),
                        _=Depends(cu_limita_ai)):
    concept = _concept_dupa_slug(db, date.concept_slug)
    try:
        schite = generator.genereaza_intrebari(db, concept, date.capitol_id, date.numar)
        db.commit()
    except RuntimeError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(e))
    return {"generate": len(schite), "mesaj": "Schițele așteaptă aprobarea ta."}


@router.post("/genereaza/exercitiu")
def genereaza_exercitiu(date: CerereGenerare, db: Session = Depends(get_db),
                        _=Depends(cu_limita_ai)):
    concept = _concept_dupa_slug(db, date.concept_slug)
    try:
        schita = generator.genereaza_exercitiu(db, concept, date.capitol_id)
        db.commit()
    except RuntimeError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(e))
    return {"id": schita.id, "validat": schita.validat,
            "raport_validare": schita.raport_validare,
            "mesaj": "Exercițiul generat așteaptă aprobarea ta."}


@router.post("/schite/{schita_id}/aproba")
def aproba(schita_id: int, db: Session = Depends(get_db)):
    schita = db.get(SchitaGenerata, schita_id)
    if schita is None or schita.stare != "propusa":
        raise HTTPException(status_code=404, detail="Schița nu există sau a fost deja procesată.")
    try:
        rezultat = generator.aproba_schita(db, schita)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    return {"mesaj": "Conținutul a fost adăugat în curs.", **rezultat}


@router.post("/schite/{schita_id}/respinge")
def respinge(schita_id: int, db: Session = Depends(get_db)):
    schita = db.get(SchitaGenerata, schita_id)
    if schita is None or schita.stare != "propusa":
        raise HTTPException(status_code=404, detail="Schița nu există sau a fost deja procesată.")
    schita.stare = "respinsa"
    db.commit()
    return {"mesaj": "Schița a fost respinsă."}


# ── Gestiunea conținutului ──────────────────────────────────────
@router.get("/concepte")
def lista_concepte(db: Session = Depends(get_db)):
    concepte = db.execute(select(Concept).order_by(Concept.ordine)).scalars().all()
    return [{"slug": c.slug, "nume": c.nume} for c in concepte]


@router.get("/intrebari")
def lista_intrebari(capitol_id: int | None = None, db: Session = Depends(get_db)):
    interogare = select(Intrebare).where(Intrebare.activa).options(
        selectinload(Intrebare.concepte), selectinload(Intrebare.capitol))
    if capitol_id is not None:
        interogare = interogare.where(Intrebare.capitol_id == capitol_id)
    intrebari = db.execute(interogare.order_by(Intrebare.capitol_id, Intrebare.id)).scalars().all()
    return [{
        "id": i.id, "capitol": i.capitol.titlu, "capitol_id": i.capitol_id,
        "text": i.text, "corecta": i.varianta_corecta, "gresite": i.gresite_json,
        "explicatie": i.explicatie, "sursa": i.sursa,
        "concepte": [c.nume for c in i.concepte],
    } for i in intrebari]


@router.post("/intrebari")
def adauga_intrebare(date: IntrebareNoua, db: Session = Depends(get_db)):
    capitol = db.get(Capitol, date.capitol_id)
    if capitol is None:
        raise HTTPException(status_code=404, detail="Capitolul nu există.")
    intrebare = Intrebare(
        capitol_id=date.capitol_id, text=date.text,
        varianta_corecta=date.varianta_corecta, gresite_json=date.gresite,
        explicatie=date.explicatie, dificultate=date.dificultate, sursa="manual")
    if date.concepte:
        intrebare.concepte = db.execute(
            select(Concept).where(Concept.slug.in_(date.concepte))).scalars().all()
    db.add(intrebare)
    db.commit()
    return {"id": intrebare.id, "mesaj": "Întrebarea a fost adăugată."}


@router.delete("/intrebari/{intrebare_id}")
def dezactiveaza_intrebare(intrebare_id: int, db: Session = Depends(get_db)):
    """Dezactivare (nu ștergere): întrebarea poate apărea în istoricul studenților."""
    intrebare = db.get(Intrebare, intrebare_id)
    if intrebare is None:
        raise HTTPException(status_code=404, detail="Întrebarea nu există.")
    intrebare.activa = False
    db.commit()
    return {"mesaj": "Întrebarea a fost retrasă din quiz-uri."}


@router.put("/lectii/{slug}")
def editeaza_lectie(slug: str, date: EditareLectie, db: Session = Depends(get_db)):
    lectie = db.execute(select(Lectie).where(Lectie.slug == slug)).scalar_one_or_none()
    if lectie is None:
        raise HTTPException(status_code=404, detail="Lecția nu există.")
    if date.titlu is not None:
        lectie.titlu = date.titlu
    if date.continut_md is not None:
        lectie.continut_md = date.continut_md
    if date.cod_exemplu is not None:
        lectie.cod_exemplu = date.cod_exemplu
    db.commit()
    rag.index.construieste(db)  # conținutul s-a schimbat → reindexare RAG
    return {"mesaj": "Lecția a fost actualizată și indexul RAG reconstruit."}
