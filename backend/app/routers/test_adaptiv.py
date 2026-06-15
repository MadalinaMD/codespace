"""Testul adaptiv: generat pe conceptele slabe ale studentului, notat pe server.

Răspunsurile corecte ale întrebărilor generate NU părăsesc serverul — clientul
primește doar textul și variantele amestecate (repară vulnerabilitatea din v2,
unde răspunsurile veneau în payload).
"""
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.attributes import flag_modified

from app import config
from app.ai import tutor
from app.deps import cu_limita_ai, get_db, utilizator_curent
from app.engine import bkt, gamification, recommender
from app.models import Concept, TestAdaptiv, Utilizator
from app.schemas import RaspunsLaIndex

router = APIRouter(prefix="/test-adaptiv", tags=["test adaptiv"])


def _test_propriu(db: Session, test_id: int, user_id: int) -> TestAdaptiv:
    test = db.get(TestAdaptiv, test_id)
    if test is None or test.user_id != user_id:
        raise HTTPException(status_code=404, detail="Testul nu există.")
    return test


@router.post("/genereaza")
def genereaza_test(user: Utilizator = Depends(cu_limita_ai),
                   db: Session = Depends(get_db)):
    intrebari, concepte_slugs = tutor.genereaza_intrebari_adaptive(db, user.id)
    if not intrebari:
        raise HTTPException(status_code=400,
                            detail="Nu există încă material pentru un test — parcurge câteva lecții întâi.")

    test = TestAdaptiv(user_id=user.id, intrebari_json=intrebari,
                       concepte_vizate=concepte_slugs, total=len(intrebari))
    db.add(test)
    db.commit()

    concepte = db.execute(
        select(Concept).where(Concept.slug.in_(concepte_slugs))
    ).scalars().all()
    payload = []
    for index, intrebare in enumerate(intrebari):
        variante = [intrebare["corecta"], *intrebare["gresite"]]
        random.shuffle(variante)
        payload.append({"index": index, "text": intrebare["text"], "variante": variante})
    return {
        "test_id": test.id,
        "intrebari": payload,
        "concepte_vizate": [c.nume for c in concepte],
    }


@router.post("/plasament/incepe")
def incepe_plasament(user: Utilizator = Depends(utilizator_curent),
                     db: Session = Depends(get_db)):
    """Testul de plasament: calibrarea inițială a modelului studentului.

    Întrebări din banca de întrebări (fără AI — plasamentul merge mereu),
    câte una pe concept, răspândite pe toată întinderea cursului.
    """
    intrebari, concepte_slugs = tutor.intrebari_plasament(db)
    if len(intrebari) < 3:
        raise HTTPException(status_code=400,
                            detail="Banca de întrebări e prea mică pentru un plasament.")

    test = TestAdaptiv(user_id=user.id, tip="plasament", intrebari_json=intrebari,
                       concepte_vizate=concepte_slugs, total=len(intrebari))
    db.add(test)
    db.commit()

    import random as _random
    payload = []
    for index, intrebare in enumerate(intrebari):
        variante = [intrebare["corecta"], *intrebare["gresite"]]
        _random.shuffle(variante)
        payload.append({"index": index, "text": intrebare["text"], "variante": variante})
    return {"test_id": test.id, "intrebari": payload, "total": len(payload)}


@router.post("/{test_id}/raspunde")
def raspunde_test(test_id: int, date: RaspunsLaIndex,
                  user: Utilizator = Depends(utilizator_curent),
                  db: Session = Depends(get_db)):
    test = _test_propriu(db, test_id, user.id)
    if test.finalizat:
        raise HTTPException(status_code=400, detail="Testul e deja finalizat.")
    if not 0 <= date.index < len(test.intrebari_json):
        raise HTTPException(status_code=400, detail="Index de întrebare invalid.")
    cheie = str(date.index)
    if cheie in (test.raspunsuri_json or {}):
        raise HTTPException(status_code=400, detail="Ai răspuns deja la această întrebare.")

    intrebare = test.intrebari_json[date.index]
    corect = date.raspuns.strip() == intrebare["corecta"].strip()

    raspunsuri = dict(test.raspunsuri_json or {})
    raspunsuri[cheie] = {"raspuns": date.raspuns, "corect": corect}
    test.raspunsuri_json = raspunsuri
    flag_modified(test, "raspunsuri_json")

    concept = db.execute(
        select(Concept).where(Concept.slug == intrebare.get("concept_slug", ""))
        .options(selectinload(Concept.prerechizite))
    ).scalar_one_or_none()
    if concept is not None:
        bkt.inregistreaza_observatie(db, user.id, [concept],
                                     corect=corect, tip_activitate="test_adaptiv")
        if test.tip == "plasament":
            # Pondere dublă la plasament: întrebările sunt sonde deliberate de
            # calibrare — o singură observație pe grilă (ghicire 25%) nu poate
            # urni priorul de 0.20 peste pragul de fundament, oricât de bun
            # ar fi studentul. Două observații îl duc la ~0.84.
            bkt.inregistreaza_observatie(db, user.id, [concept],
                                         corect=corect, tip_activitate="test_adaptiv")
            # Răspunsul corect e dovadă implicită și pentru prerechizitele
            # directe: cine stăpânește buclele știe variabilele. (Greșeala NU
            # se propagă — nu putem conchide că fundamentul lipsește.)
            if corect and concept.prerechizite:
                bkt.inregistreaza_observatie(db, user.id, concept.prerechizite,
                                             corect=True, tip_activitate="test_adaptiv")
    db.commit()

    return {"corect": corect, "corecta": intrebare["corecta"],
            "explicatie": intrebare.get("explicatie", "")}


@router.post("/{test_id}/finalizeaza")
def finalizeaza_test(test_id: int, user: Utilizator = Depends(utilizator_curent),
                     db: Session = Depends(get_db)):
    test = _test_propriu(db, test_id, user.id)
    if test.finalizat:
        raise HTTPException(status_code=400, detail="Testul e deja finalizat.")

    raspunsuri = test.raspunsuri_json or {}
    test.scor = sum(1 for r in raspunsuri.values() if r.get("corect"))
    test.finalizat = True
    # Plasamentul e calibrare, nu învățare: nu acordă XP (corectitudine în clasament)
    xp_castigat = 0
    if test.tip != "plasament":
        xp_castigat = gamification.acorda_xp(
            db, user.id, "test_adaptiv", test.scor * config.XP_INTREBARE_TEST,
            f"Test adaptiv: {test.scor}/{test.total} corecte")
    gamification.inregistreaza_activitate(db, user.id)
    realizari_noi = gamification.verifica_realizari(db, user.id)

    # Defalcare pe concepte: unde a progresat, unde mai e de lucru
    pe_concepte: dict[str, dict] = {}
    for index_str, raspuns in raspunsuri.items():
        intrebare = test.intrebari_json[int(index_str)]
        slug = intrebare.get("concept_slug", "general")
        statistici = pe_concepte.setdefault(slug, {"corecte": 0, "total": 0})
        statistici["total"] += 1
        statistici["corecte"] += 1 if raspuns.get("corect") else 0
    concepte = db.execute(
        select(Concept).where(Concept.slug.in_(list(pe_concepte)))
    ).scalars().all()
    nume = {c.slug: c.nume for c in concepte}
    db.commit()

    rezultat = {
        "scor": test.scor,
        "total": test.total,
        "tip": test.tip,
        "xp_castigat": xp_castigat,
        "realizari_noi": realizari_noi,
        "pe_concepte": [
            {"concept": nume.get(slug, slug), **statistici}
            for slug, statistici in pe_concepte.items()
        ],
    }
    if test.tip == "plasament":
        # Punctul de plecare personalizat, dedus din modelul abia calibrat
        rezultat["start"] = recommender.lectia_de_start(db, user.id)
    return rezultat
