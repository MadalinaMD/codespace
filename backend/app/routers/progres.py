"""Progresul studentului: recomandări explicabile, harta măiestriei, statistici."""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.deps import get_db, utilizator_curent
from app.engine import bkt, gamification, recommender, sm2
from app.models import (CardRecapitulare, Concept, Exercitiu, Intrebare,
                        Lectie, StareConcept, Submisie, TentativaQuiz,
                        Utilizator, VizitaLectie, Capitol)
from app.engine.errors import CATEGORII

router = APIRouter(prefix="/progres", tags=["progres"])


@router.get("/recomandari")
def recomandari(user: Utilizator = Depends(utilizator_curent),
                db: Session = Depends(get_db)):
    ultima_vizita = db.execute(
        select(VizitaLectie).where(VizitaLectie.user_id == user.id)
        .order_by(VizitaLectie.creat_la.desc(), VizitaLectie.id.desc()).limit(1)
    ).scalar_one_or_none()
    continua = None
    if ultima_vizita:
        lectie = db.get(Lectie, ultima_vizita.lectie_id)
        if lectie:
            continua = {"lectie_slug": lectie.slug, "titlu": lectie.titlu}
    return {
        "recomandari": recommender.recomandari(db, user.id),
        "continua": continua,
    }


@router.get("/harta")
def harta_maiestriei(user: Utilizator = Depends(utilizator_curent),
                     db: Session = Depends(get_db)):
    """Graful de concepte cu probabilitatea de cunoaștere a studentului pe fiecare nod."""
    concepte = db.execute(
        select(Concept).options(selectinload(Concept.prerechizite))
        .order_by(Concept.ordine)
    ).scalars().all()
    stari = bkt.probabilitati_utilizator(db, user.id)

    # Prima lecție care predă fiecare concept (pentru click-through din hartă)
    lectii_concept: dict[int, str] = {}
    lectii = db.execute(
        select(Lectie).join(Capitol).options(selectinload(Lectie.concepte))
        .order_by(Capitol.ordine, Lectie.ordine)
    ).scalars().all()
    for lectie in lectii:
        for c in lectie.concepte:
            lectii_concept.setdefault(c.id, lectie.slug)

    noduri = []
    for concept in concepte:
        stare = stari.get(concept.id)
        p = stare.p_cunoastere if stare else config.BKT_P_INIT
        observatii = stare.nr_observatii if stare else 0
        if observatii == 0:
            eticheta = "nestudiat"
        elif p >= config.PRAG_STAPANIRE:
            eticheta = "stapanit"
        elif p < config.PRAG_CONCEPT_SLAB:
            eticheta = "slab"
        else:
            eticheta = "in_lucru"
        noduri.append({
            "slug": concept.slug,
            "nume": concept.nume,
            "descriere": concept.descriere,
            "ordine": concept.ordine,
            "p": round(p, 2),
            "observatii": observatii,
            "stare": eticheta,
            "prerechizite": [pr.slug for pr in concept.prerechizite],
            "lectie_slug": lectii_concept.get(concept.id),
        })
    stapanite = sum(1 for n in noduri if n["stare"] == "stapanit")
    return {"concepte": noduri, "stapanite": stapanite, "total": len(noduri)}


@router.get("/statistici")
def statistici(user: Utilizator = Depends(utilizator_curent),
               db: Session = Depends(get_db)):
    total_lectii = db.execute(select(func.count()).select_from(Lectie)).scalar_one()
    lectii_vizitate = db.execute(
        select(func.count()).select_from(VizitaLectie)
        .where(VizitaLectie.user_id == user.id)).scalar_one()
    total_exercitii = db.execute(select(func.count()).select_from(Exercitiu)).scalar_one()
    exercitii_rezolvate = db.execute(
        select(func.count(func.distinct(Submisie.exercitiu_id)))
        .where(Submisie.user_id == user.id, Submisie.status == "acceptat")).scalar_one()
    total_capitole = db.execute(select(func.count()).select_from(Capitol)).scalar_one()
    capitole_cu_quiz = db.execute(
        select(func.count(func.distinct(TentativaQuiz.capitol_id)))
        .where(TentativaQuiz.user_id == user.id, TentativaQuiz.finalizat)).scalar_one()
    submisii_total = db.execute(
        select(func.count()).select_from(Submisie)
        .where(Submisie.user_id == user.id)).scalar_one()

    # Greșelile frecvente (categorii de erori la submisii)
    erori = db.execute(
        select(Submisie.eroare_categorie, func.count())
        .where(Submisie.user_id == user.id, Submisie.eroare_categorie.isnot(None))
        .group_by(Submisie.eroare_categorie)
        .order_by(func.count().desc()).limit(5)
    ).all()

    # Recapitulări scadente
    carduri = db.execute(
        select(CardRecapitulare).where(CardRecapitulare.user_id == user.id)
    ).scalars().all()
    active = [c for c in carduri if not sm2.card_este_invatat(c.repetari, c.interval_zile)]
    scadente = sum(1 for c in active if c.scadent_la <= datetime.now())

    stari = bkt.probabilitati_utilizator(db, user.id)
    observate = [s for s in stari.values() if s.nr_observatii > 0]
    stapanite = sum(1 for s in observate if s.p_cunoastere >= config.PRAG_STAPANIRE)
    total_concepte = db.execute(select(func.count()).select_from(Concept)).scalar_one()

    profil = gamification.profil_gamificare(db, user.id)
    return {
        "lectii": {"vizitate": lectii_vizitate, "total": total_lectii},
        "exercitii": {"rezolvate": exercitii_rezolvate, "total": total_exercitii,
                      "submisii": submisii_total},
        "quiz": {"capitole_finalizate": capitole_cu_quiz, "total": total_capitole},
        "concepte": {"stapanite": stapanite, "studiate": len(observate),
                     "total": total_concepte},
        "recapitulari_scadente": scadente,
        "erori_frecvente": [{
            "categorie": categorie,
            "titlu": CATEGORII.get(categorie, CATEGORII["alta_eroare"])[0],
            "numar": numar,
        } for categorie, numar in erori],
        "calendar": gamification.calendar_activitate(db, user.id, 30),
        "xp_total": profil["xp_total"],
        "nivel": profil["nivel"],
        "streak": profil["streak"],
    }
