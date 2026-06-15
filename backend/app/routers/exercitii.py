"""Exerciții: enunț + teste vizibile, trimiterea oficială (evaluată pe server)
și indiciile progresive.

Anti-trișare: soluția de referință nu pleacă NICIODATĂ spre client, iar
statusul/XP-ul se decid exclusiv din rularea pe server.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.ai import tutor
from app.deps import cu_limita_ai, get_db, utilizator_curent
from app.engine import bkt, errors, gamification, sandbox
from app.models import Exercitiu, IndiciuAcordat, Submisie, Utilizator
from app.schemas import CerereIndiciu, TrimitereCod

router = APIRouter(prefix="/exercitii", tags=["exercitii"])


def _exercitiu_sau_404(db: Session, exercitiu_id: int) -> Exercitiu:
    exercitiu = db.execute(
        select(Exercitiu).where(Exercitiu.id == exercitiu_id)
        .options(selectinload(Exercitiu.teste), selectinload(Exercitiu.concepte),
                 selectinload(Exercitiu.lectie))
    ).scalar_one_or_none()
    if exercitiu is None:
        raise HTTPException(status_code=404, detail="Exercițiul nu există.")
    return exercitiu


def _nivel_maxim_indiciu(db: Session, user_id: int, exercitiu_id: int) -> int:
    return db.execute(
        select(func.coalesce(func.max(IndiciuAcordat.nivel), 0))
        .where(IndiciuAcordat.user_id == user_id,
               IndiciuAcordat.exercitiu_id == exercitiu_id)
    ).scalar_one()


@router.get("/{exercitiu_id}")
def detalii_exercitiu(exercitiu_id: int, user: Utilizator = Depends(utilizator_curent),
                      db: Session = Depends(get_db)):
    exercitiu = _exercitiu_sau_404(db, exercitiu_id)
    rezolvat = db.execute(
        select(Submisie.id).where(Submisie.user_id == user.id,
                                  Submisie.exercitiu_id == exercitiu_id,
                                  Submisie.status == "acceptat").limit(1)
    ).scalar_one_or_none() is not None
    ultima = db.execute(
        select(Submisie).where(Submisie.user_id == user.id,
                               Submisie.exercitiu_id == exercitiu_id)
        .order_by(Submisie.id.desc()).limit(1)
    ).scalar_one_or_none()
    indicii = db.execute(
        select(IndiciuAcordat).where(IndiciuAcordat.user_id == user.id,
                                     IndiciuAcordat.exercitiu_id == exercitiu_id)
        .order_by(IndiciuAcordat.nivel)
    ).scalars().all()

    raspuns = {
        "id": exercitiu.id,
        "titlu": exercitiu.titlu,
        "enunt_md": exercitiu.enunt_md,
        "cod_start": exercitiu.cod_start,
        "mod": exercitiu.mod,
        "functie_nume": exercitiu.functie_nume,
        "dificultate": exercitiu.dificultate,
        "lectie": {"slug": exercitiu.lectie.slug, "titlu": exercitiu.lectie.titlu},
        "concepte": [c.nume for c in exercitiu.concepte],
        "teste": sandbox.teste_din_model(exercitiu.teste),
        "rezolvat": rezolvat,
        "ultimul_cod": ultima.cod if ultima else None,
        "indicii_primite": [{"nivel": i.nivel, "continut": i.continut} for i in indicii],
        "nivel_indiciu_urmator": min(_nivel_maxim_indiciu(db, user.id, exercitiu_id) + 1,
                                     config.MAX_NIVEL_INDICIU),
    }
    # Soluția de referință se dezvăluie DOAR după ce exercițiul a fost rezolvat —
    # ca să poți compara abordarea ta cu a profesorului, nu ca să copiezi.
    if rezolvat:
        raspuns["solutie_referinta"] = exercitiu.solutie_referinta
    return raspuns


@router.post("/{exercitiu_id}/trimite")
def trimite_solutie(exercitiu_id: int, date: TrimitereCod,
                    user: Utilizator = Depends(utilizator_curent),
                    db: Session = Depends(get_db)):
    """Evaluarea oficială: rulează codul în sandbox-ul serverului și notează."""
    exercitiu = _exercitiu_sau_404(db, exercitiu_id)
    teste = sandbox.teste_din_model(exercitiu.teste)
    rezultat = sandbox.ruleaza_teste(date.cod, teste, mod=exercitiu.mod)

    era_rezolvat = db.execute(
        select(Submisie.id).where(Submisie.user_id == user.id,
                                  Submisie.exercitiu_id == exercitiu_id,
                                  Submisie.status == "acceptat").limit(1)
    ).scalar_one_or_none() is not None
    nivel_indicii = _nivel_maxim_indiciu(db, user.id, exercitiu_id)

    submisie = Submisie(
        user_id=user.id, exercitiu_id=exercitiu_id, cod=date.cod,
        status=rezultat.status, teste_total=rezultat.teste_total,
        teste_trecute=rezultat.teste_trecute,
        eroare_categorie=rezultat.eroare_categorie,
        eroare_mesaj=rezultat.eroare_mesaj,
        detalii_json=rezultat.rezultate,
        indicii_folosite=nivel_indicii,
    )
    db.add(submisie)

    acceptat = rezultat.status == "acceptat"
    # Modelul studentului învață din ORICE submisie, nu doar din reușite
    bkt.inregistreaza_observatie(db, user.id, exercitiu.concepte,
                                 corect=acceptat, tip_activitate="exercitiu")

    xp_castigat = 0
    if acceptat and not era_rezolvat:
        xp = max(config.XP_EXERCITIU - nivel_indicii * config.XP_PENALIZARE_INDICIU,
                 config.XP_EXERCITIU_MINIM)
        xp_castigat = gamification.acorda_xp(
            db, user.id, "exercitiu", xp,
            f"Exercițiul „{exercitiu.titlu}” rezolvat"
            + (f" (cu {nivel_indicii} indicii)" if nivel_indicii else ""))

    gamification.inregistreaza_activitate(db, user.id)
    realizari_noi = gamification.verifica_realizari(db, user.id)
    db.commit()

    return {
        "status": rezultat.status,
        "teste_total": rezultat.teste_total,
        "teste_trecute": rezultat.teste_trecute,
        "rezultate": rezultat.rezultate,
        "eroare": errors.descrie(rezultat.eroare_categorie) if rezultat.eroare_categorie else None,
        "eroare_mesaj": rezultat.eroare_mesaj,
        "prima_rezolvare": acceptat and not era_rezolvat,
        "xp_castigat": xp_castigat,
        "realizari_noi": realizari_noi,
    }


@router.post("/{exercitiu_id}/indiciu")
def cere_indiciu(exercitiu_id: int, date: CerereIndiciu,
                 user: Utilizator = Depends(cu_limita_ai),
                 db: Session = Depends(get_db)):
    """Indiciu progresiv (1→3). Nivelurile se deblochează pe rând, iar folosirea
    lor reduce XP-ul exercițiului — împinge studentul să încerce singur întâi."""
    exercitiu = _exercitiu_sau_404(db, exercitiu_id)
    nivel_curent = _nivel_maxim_indiciu(db, user.id, exercitiu_id)
    if date.nivel > nivel_curent + 1:
        raise HTTPException(status_code=400,
                            detail=f"Indiciile se deblochează pe rând: cere întâi nivelul {nivel_curent + 1}.")

    # Rulăm codul curent ca indiciul să se refere la problema reală a studentului
    rezultat = None
    if date.cod.strip():
        rezultat = sandbox.ruleaza_teste(date.cod, sandbox.teste_din_model(exercitiu.teste),
                                         mod=exercitiu.mod)

    continut = tutor.genereaza_indiciu(db, exercitiu, date.cod, rezultat, date.nivel)
    db.add(IndiciuAcordat(user_id=user.id, exercitiu_id=exercitiu_id,
                          nivel=date.nivel, continut=continut))
    gamification.inregistreaza_activitate(db, user.id)
    db.commit()
    return {"nivel": date.nivel, "continut": continut,
            "nivel_urmator": min(date.nivel + 1, config.MAX_NIVEL_INDICIU)}
