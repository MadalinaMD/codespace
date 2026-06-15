"""Quiz de capitol — evaluat integral pe server.

Fluxul anti-trișare:
1. POST /quiz/incepe/{capitol} → serverul alege întrebările și creează o
   tentativă; clientul primește variantele AMESTECATE, fără marcajul corect;
2. POST /quiz/{tentativa}/raspunde → serverul notează și abia apoi dezvăluie
   răspunsul corect + explicația (feedback imediat, dar nefalsificabil);
3. POST /quiz/{tentativa}/finalizeaza → scorul se calculează din răspunsurile
   stocate; XP-ul se acordă la prima tentativă a capitolului.
"""
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.deps import get_db, utilizator_curent
from app.engine import bkt, gamification, sm2
from app.models import (Capitol, CardRecapitulare, Intrebare, RaspunsQuiz,
                        TentativaQuiz, Utilizator)
from app.schemas import RaspunsLaIntrebare

router = APIRouter(prefix="/quiz", tags=["quiz"])

INTREBARI_PER_QUIZ = 8


def _tentativa_proprie(db: Session, tentativa_id: int, user_id: int) -> TentativaQuiz:
    tentativa = db.get(TentativaQuiz, tentativa_id)
    if tentativa is None or tentativa.user_id != user_id:
        raise HTTPException(status_code=404, detail="Tentativa nu există.")
    return tentativa


@router.post("/incepe/{capitol_slug}")
def incepe_quiz(capitol_slug: str, user: Utilizator = Depends(utilizator_curent),
                db: Session = Depends(get_db)):
    capitol = db.execute(
        select(Capitol).where(Capitol.slug == capitol_slug)
    ).scalar_one_or_none()
    if capitol is None:
        raise HTTPException(status_code=404, detail="Capitolul nu există.")

    intrebari = db.execute(
        select(Intrebare).where(Intrebare.capitol_id == capitol.id, Intrebare.activa)
    ).scalars().all()
    if not intrebari:
        raise HTTPException(status_code=400, detail="Capitolul nu are încă întrebări.")

    alese = random.sample(intrebari, min(INTREBARI_PER_QUIZ, len(intrebari)))
    tentativa = TentativaQuiz(user_id=user.id, capitol_id=capitol.id,
                              intrebari_json=[i.id for i in alese], total=len(alese))
    db.add(tentativa)
    db.commit()

    payload = []
    for intrebare in alese:
        variante = [intrebare.varianta_corecta, *intrebare.gresite_json]
        random.shuffle(variante)
        payload.append({"id": intrebare.id, "text": intrebare.text, "variante": variante})
    return {"tentativa_id": tentativa.id, "capitol": capitol.titlu, "intrebari": payload}


@router.post("/{tentativa_id}/raspunde")
def raspunde(tentativa_id: int, date: RaspunsLaIntrebare,
             user: Utilizator = Depends(utilizator_curent),
             db: Session = Depends(get_db)):
    tentativa = _tentativa_proprie(db, tentativa_id, user.id)
    if tentativa.finalizat:
        raise HTTPException(status_code=400, detail="Tentativa e deja finalizată.")
    if date.intrebare_id not in tentativa.intrebari_json:
        raise HTTPException(status_code=400, detail="Întrebarea nu aparține tentativei.")
    deja = db.execute(
        select(RaspunsQuiz.id).where(RaspunsQuiz.tentativa_id == tentativa.id,
                                     RaspunsQuiz.intrebare_id == date.intrebare_id)
    ).scalar_one_or_none()
    if deja is not None:
        raise HTTPException(status_code=400, detail="Ai răspuns deja la această întrebare.")

    intrebare = db.execute(
        select(Intrebare).where(Intrebare.id == date.intrebare_id)
        .options(selectinload(Intrebare.concepte))
    ).scalar_one()
    corect = date.raspuns.strip() == intrebare.varianta_corecta.strip()

    db.add(RaspunsQuiz(tentativa_id=tentativa.id, intrebare_id=intrebare.id,
                       raspuns_text=date.raspuns, corect=corect))
    bkt.inregistreaza_observatie(db, user.id, intrebare.concepte,
                                 corect=corect, tip_activitate="quiz")
    if not corect:
        _adauga_card_recapitulare(db, user.id, intrebare.id)
    db.commit()

    return {"corect": corect, "corecta": intrebare.varianta_corecta,
            "explicatie": intrebare.explicatie}


@router.post("/{tentativa_id}/finalizeaza")
def finalizeaza(tentativa_id: int, user: Utilizator = Depends(utilizator_curent),
                db: Session = Depends(get_db)):
    tentativa = _tentativa_proprie(db, tentativa_id, user.id)
    if tentativa.finalizat:
        raise HTTPException(status_code=400, detail="Tentativa e deja finalizată.")

    raspunsuri = db.execute(
        select(RaspunsQuiz).where(RaspunsQuiz.tentativa_id == tentativa.id)
    ).scalars().all()
    tentativa.scor = sum(1 for r in raspunsuri if r.corect)
    tentativa.total = len(tentativa.intrebari_json)
    tentativa.finalizat = True

    # XP doar la prima tentativă finalizată a capitolului (anti-farming)
    prima = db.execute(
        select(TentativaQuiz.id)
        .where(TentativaQuiz.user_id == user.id,
               TentativaQuiz.capitol_id == tentativa.capitol_id,
               TentativaQuiz.finalizat, TentativaQuiz.id != tentativa.id)
        .limit(1)
    ).scalar_one_or_none() is None
    xp_castigat = 0
    if prima:
        capitol = db.get(Capitol, tentativa.capitol_id)
        xp_castigat = gamification.acorda_xp(
            db, user.id, "quiz", tentativa.scor * config.XP_INTREBARE_QUIZ,
            f"Quiz „{capitol.titlu}”: {tentativa.scor}/{tentativa.total} corecte")

    gamification.inregistreaza_activitate(db, user.id)
    realizari_noi = gamification.verifica_realizari(db, user.id)
    db.commit()

    return {"scor": tentativa.scor, "total": tentativa.total,
            "prima_tentativa": prima, "xp_castigat": xp_castigat,
            "realizari_noi": realizari_noi}


def _adauga_card_recapitulare(db: Session, user_id: int, intrebare_id: int) -> None:
    """Întrebarea greșită intră (sau revine) în coada de repetiție spațiată."""
    card = db.execute(
        select(CardRecapitulare).where(CardRecapitulare.user_id == user_id,
                                       CardRecapitulare.intrebare_id == intrebare_id)
    ).scalar_one_or_none()
    if card is None:
        db.add(CardRecapitulare(user_id=user_id, intrebare_id=intrebare_id,
                                factor_usurinta=config.SM2_FACTOR_INITIAL))
    else:
        # Greșită din nou în quiz: seria SM-2 se reia, cardul e scadent imediat
        programare = sm2.urmatoarea_programare(card.factor_usurinta, card.repetari,
                                               card.interval_zile, sm2.CALITATE_GRESIT)
        card.factor_usurinta = programare.factor_usurinta
        card.repetari = 0
        card.interval_zile = 0
        card.scadent_la = datetime.now()
