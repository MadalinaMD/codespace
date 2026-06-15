"""Cursul: harta capitolelor/lecțiilor (cu starea per student) și conținutul lecțiilor."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.deps import get_db, utilizator_curent
from app.engine import bkt, gamification, recommender
from app.models import (Capitol, Concept, Lectie, Submisie, TentativaQuiz,
                        Utilizator, VizitaLectie)

router = APIRouter(tags=["curs"])


def _vizitate(db: Session, user_id: int) -> set[int]:
    return {l for (l,) in db.execute(
        select(VizitaLectie.lectie_id).where(VizitaLectie.user_id == user_id)).all()}


def _exercitii_rezolvate(db: Session, user_id: int) -> set[int]:
    return {e for (e,) in db.execute(
        select(Submisie.exercitiu_id).where(Submisie.user_id == user_id,
                                            Submisie.status == "acceptat")).all()}


@router.get("/curs")
def harta_cursului(user: Utilizator = Depends(utilizator_curent),
                   db: Session = Depends(get_db)):
    """Capitolele și lecțiile, cu starea fiecărei lecții pentru studentul curent."""
    capitole = db.execute(
        select(Capitol)
        .options(selectinload(Capitol.lectii).selectinload(Lectie.concepte)
                 .selectinload(Concept.prerechizite),
                 selectinload(Capitol.lectii).selectinload(Lectie.exercitii))
        .order_by(Capitol.ordine)
    ).scalars().all()

    vizitate = _vizitate(db, user.id)
    rezolvate = _exercitii_rezolvate(db, user.id)
    stari = bkt.probabilitati_utilizator(db, user.id)

    # Cea mai bună tentativă de quiz per capitol
    tentative = db.execute(
        select(TentativaQuiz).where(TentativaQuiz.user_id == user.id,
                                    TentativaQuiz.finalizat)
    ).scalars().all()
    quiz_best: dict[int, dict] = {}
    for t in tentative:
        existent = quiz_best.get(t.capitol_id)
        procent = t.scor / t.total if t.total else 0
        if existent is None or procent > existent["procent"]:
            quiz_best[t.capitol_id] = {"scor": t.scor, "total": t.total, "procent": procent}

    rezultat = []
    for capitol in capitole:
        lectii = []
        for lectie in capitol.lectii:
            nepregatite = recommender.prerechizite_nepregatite(lectie, stari)
            exercitii_ids = [e.id for e in lectie.exercitii]
            lectii.append({
                "slug": lectie.slug,
                "titlu": lectie.titlu,
                "vizitata": lectie.id in vizitate,
                "fundament_gata": not nepregatite,
                "prerechizite_lipsa": [c.nume for c in nepregatite],
                "exercitii_total": len(exercitii_ids),
                "exercitii_rezolvate": sum(1 for e in exercitii_ids if e in rezolvate),
                "concepte": [c.nume for c in lectie.concepte],
            })
        quiz = quiz_best.get(capitol.id)
        rezultat.append({
            "id": capitol.id,
            "slug": capitol.slug,
            "titlu": capitol.titlu,
            "descriere": capitol.descriere,
            "lectii": lectii,
            "quiz": {"scor": quiz["scor"], "total": quiz["total"],
                     "procent": round(quiz["procent"] * 100)} if quiz else None,
        })
    return rezultat


@router.get("/lectii/{slug}")
def detalii_lectie(slug: str, user: Utilizator = Depends(utilizator_curent),
                   db: Session = Depends(get_db)):
    lectie = db.execute(
        select(Lectie).where(Lectie.slug == slug)
        .options(selectinload(Lectie.concepte), selectinload(Lectie.exercitii),
                 selectinload(Lectie.capitol))
    ).scalar_one_or_none()
    if lectie is None:
        raise HTTPException(status_code=404, detail="Lecția nu există.")

    stari = bkt.probabilitati_utilizator(db, user.id)
    rezolvate = _exercitii_rezolvate(db, user.id)

    # Navigare: lecția anterioară/următoare în ordinea cursului
    toate = db.execute(
        select(Lectie.slug, Lectie.titlu).join(Capitol)
        .order_by(Capitol.ordine, Lectie.ordine)
    ).all()
    sluguri = [s for s, _ in toate]
    pozitie = sluguri.index(slug)
    anterioara = ({"slug": toate[pozitie - 1][0], "titlu": toate[pozitie - 1][1]}
                  if pozitie > 0 else None)
    urmatoarea = ({"slug": toate[pozitie + 1][0], "titlu": toate[pozitie + 1][1]}
                  if pozitie < len(toate) - 1 else None)

    return {
        "slug": lectie.slug,
        "titlu": lectie.titlu,
        "continut_md": lectie.continut_md,
        "cod_exemplu": lectie.cod_exemplu,
        "sursa": lectie.sursa,
        "capitol": {"slug": lectie.capitol.slug, "titlu": lectie.capitol.titlu},
        "concepte": [{
            "slug": c.slug, "nume": c.nume,
            "p": round(bkt.p_concept(stari, c.id), 2),
        } for c in lectie.concepte],
        "exercitii": [{
            "id": e.id, "titlu": e.titlu, "dificultate": e.dificultate,
            "rezolvat": e.id in rezolvate,
        } for e in lectie.exercitii],
        "anterioara": anterioara,
        "urmatoarea": urmatoarea,
    }


@router.post("/lectii/{slug}/vizita")
def marcheaza_vizita(slug: str, user: Utilizator = Depends(utilizator_curent),
                     db: Session = Depends(get_db)):
    lectie = db.execute(select(Lectie).where(Lectie.slug == slug)).scalar_one_or_none()
    if lectie is None:
        raise HTTPException(status_code=404, detail="Lecția nu există.")
    exista = db.execute(
        select(VizitaLectie.id).where(VizitaLectie.user_id == user.id,
                                      VizitaLectie.lectie_id == lectie.id)
    ).scalar_one_or_none()
    prima_data = exista is None
    if prima_data:
        db.add(VizitaLectie(user_id=user.id, lectie_id=lectie.id))
    gamification.inregistreaza_activitate(db, user.id)
    realizari_noi = gamification.verifica_realizari(db, user.id)
    db.commit()
    return {"prima_data": prima_data, "realizari_noi": realizari_noi}
