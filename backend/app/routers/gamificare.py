"""Gamificare: profilul (XP, nivel, streak, realizări), istoricul XP și clasamentul.

Clasamentul nu mai expune adresele de email ale studenților (vulnerabilitate v2).
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import config
from app.deps import get_db, utilizator_curent
from app.engine import gamification
from app.models import (EvenimentXP, StareConcept, Submisie, Utilizator)

router = APIRouter(tags=["gamificare"])


@router.get("/gamificare/profil")
def profil(user: Utilizator = Depends(utilizator_curent), db: Session = Depends(get_db)):
    return gamification.profil_gamificare(db, user.id)


@router.get("/gamificare/istoric-xp")
def istoric_xp(user: Utilizator = Depends(utilizator_curent),
               db: Session = Depends(get_db)):
    evenimente = db.execute(
        select(EvenimentXP).where(EvenimentXP.user_id == user.id)
        .order_by(EvenimentXP.id.desc()).limit(30)
    ).scalars().all()
    return [{"tip": e.tip, "puncte": e.puncte, "descriere": e.descriere,
             "creat_la": e.creat_la} for e in evenimente]


@router.get("/clasament")
def clasament(user: Utilizator = Depends(utilizator_curent),
              db: Session = Depends(get_db)):
    studenti = db.execute(
        select(Utilizator).where(Utilizator.rol == "student")
    ).scalars().all()

    xp_map = dict(db.execute(
        select(EvenimentXP.user_id, func.sum(EvenimentXP.puncte))
        .group_by(EvenimentXP.user_id)).all())
    exercitii_map = dict(db.execute(
        select(Submisie.user_id, func.count(func.distinct(Submisie.exercitiu_id)))
        .where(Submisie.status == "acceptat")
        .group_by(Submisie.user_id)).all())
    stapanite_map = dict(db.execute(
        select(StareConcept.user_id, func.count())
        .where(StareConcept.p_cunoastere >= config.PRAG_STAPANIRE)
        .group_by(StareConcept.user_id)).all())

    intrari = []
    for student in studenti:
        xp = xp_map.get(student.id, 0) or 0
        if xp == 0 and student.id not in exercitii_map:
            continue  # studenții fără activitate nu apar în clasament
        intrari.append({
            "user_id": student.id,
            "nume": student.nume,
            "xp": xp,
            "nivel": gamification.detalii_nivel(xp)["nivel"],
            "exercitii_rezolvate": exercitii_map.get(student.id, 0),
            "concepte_stapanite": stapanite_map.get(student.id, 0),
            "esti_tu": student.id == user.id,
        })
    intrari.sort(key=lambda i: (-i["xp"], -i["exercitii_rezolvate"], i["nume"]))
    for pozitie, intrare in enumerate(intrari, start=1):
        intrare["rank"] = pozitie
        del intrare["user_id"]
    return intrari
