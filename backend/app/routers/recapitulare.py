"""Recapitulare prin repetiție spațiată (SM-2): coada scadentă + notarea răspunsurilor."""
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.deps import get_db, utilizator_curent
from app.engine import bkt, gamification, sm2
from app.models import CardRecapitulare, Intrebare, Utilizator
from app.schemas import RaspunsLaIntrebare

router = APIRouter(prefix="/recapitulare", tags=["recapitulare"])


def _carduri_active(db: Session, user_id: int) -> list[CardRecapitulare]:
    carduri = db.execute(
        select(CardRecapitulare).where(CardRecapitulare.user_id == user_id)
        .options(selectinload(CardRecapitulare.intrebare)
                 .selectinload(Intrebare.capitol))
        .order_by(CardRecapitulare.scadent_la)
    ).scalars().all()
    return [c for c in carduri
            if not sm2.card_este_invatat(c.repetari, c.interval_zile)]


@router.get("")
def coada_recapitulare(user: Utilizator = Depends(utilizator_curent),
                       db: Session = Depends(get_db)):
    """Cardurile scadente acum (limitate la o sesiune), plus statistici de coadă."""
    active = _carduri_active(db, user.id)
    acum = datetime.now()
    scadente = [c for c in active if c.scadent_la <= acum]
    viitoare = [c for c in active if c.scadent_la > acum]

    sesiune = []
    for card in scadente[:config.RECAPITULARI_PE_SESIUNE]:
        variante = [card.intrebare.varianta_corecta, *card.intrebare.gresite_json]
        random.shuffle(variante)
        sesiune.append({
            "card_id": card.id,
            "intrebare_id": card.intrebare.id,
            "text": card.intrebare.text,
            "variante": variante,
            "capitol": card.intrebare.capitol.titlu,
            "repetari": card.repetari,
        })
    return {
        "carduri": sesiune,
        "total_scadente": len(scadente),
        "total_in_invatare": len(active),
        "urmatoarea_scadenta": min((c.scadent_la for c in viitoare), default=None),
    }


@router.post("/{card_id}/raspunde")
def raspunde_recapitulare(card_id: int, date: RaspunsLaIntrebare,
                          user: Utilizator = Depends(utilizator_curent),
                          db: Session = Depends(get_db)):
    card = db.execute(
        select(CardRecapitulare).where(CardRecapitulare.id == card_id)
        .options(selectinload(CardRecapitulare.intrebare).selectinload(Intrebare.concepte))
    ).scalar_one_or_none()
    if card is None or card.user_id != user.id:
        raise HTTPException(status_code=404, detail="Cardul nu există.")

    intrebare = card.intrebare
    corect = date.raspuns.strip() == intrebare.varianta_corecta.strip()

    programare = sm2.urmatoarea_programare(
        card.factor_usurinta, card.repetari, card.interval_zile,
        sm2.CALITATE_CORECT if corect else sm2.CALITATE_GRESIT)
    card.factor_usurinta = programare.factor_usurinta
    card.repetari = programare.repetari
    card.interval_zile = programare.interval_zile
    card.scadent_la = programare.scadent_la
    card.ultima_calitate = sm2.CALITATE_CORECT if corect else sm2.CALITATE_GRESIT

    bkt.inregistreaza_observatie(db, user.id, intrebare.concepte,
                                 corect=corect, tip_activitate="recapitulare")
    xp_castigat = 0
    if corect:
        xp_castigat = gamification.acorda_xp(db, user.id, "recapitulare",
                                             config.XP_RECAPITULARE,
                                             "Întrebare recapitulată corect")
    gamification.inregistreaza_activitate(db, user.id)
    realizari_noi = gamification.verifica_realizari(db, user.id)
    db.commit()

    return {
        "corect": corect,
        "corecta": intrebare.varianta_corecta,
        "explicatie": intrebare.explicatie,
        "interval_zile": card.interval_zile,
        "scadent_la": card.scadent_la,
        "invatat": sm2.card_este_invatat(card.repetari, card.interval_zile),
        "xp_castigat": xp_castigat,
        "realizari_noi": realizari_noi,
    }
