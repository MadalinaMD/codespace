"""Recomandatorul: decide CE să învețe studentul acum și explică DE CE.

Politica pedagogică (în ordinea priorității):
1. Recapitulările scadente (memoria se consolidează la timp — SM-2);
2. Exersarea conceptelor slabe (p(cunoaștere) sub prag, după minim 2 observații);
3. Următoarea lecție nevizitată ale cărei prerechizite sunt suficient stăpânite;
   dacă prerechizitele nu sunt gata, se recomandă întâi consolidarea lor;
4. Un test adaptiv, când există suficiente concepte studiate de evaluat.

Fiecare recomandare include motivul — sistemul trebuie să fie explicabil,
nu o cutie neagră.
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import config
from app.engine import bkt, sm2
from app.models import (CardRecapitulare, Capitol, Concept, Exercitiu,
                        Lectie, StareConcept, Submisie, VizitaLectie)


def _carduri_scadente(db: Session, user_id: int) -> int:
    carduri = db.execute(
        select(CardRecapitulare).where(
            CardRecapitulare.user_id == user_id,
            CardRecapitulare.scadent_la <= datetime.now(),
        )
    ).scalars().all()
    return sum(
        1 for c in carduri
        if not sm2.card_este_invatat(c.repetari, c.interval_zile)
    )


def _exercitii_rezolvate(db: Session, user_id: int) -> set[int]:
    return {
        e for (e,) in db.execute(
            select(Submisie.exercitiu_id).where(Submisie.user_id == user_id,
                                                Submisie.status == "acceptat")
        ).all()
    }


def _lectii_vizitate(db: Session, user_id: int) -> set[int]:
    return {
        l for (l,) in db.execute(
            select(VizitaLectie.lectie_id).where(VizitaLectie.user_id == user_id)
        ).all()
    }


def prerechizite_nepregatite(lectie: Lectie, stari: dict) -> list[Concept]:
    """Prerechizitele conceptelor lecției aflate sub pragul de fundament.

    Conceptele predate chiar de lecție nu pot fi "prerechizite lipsă" ale ei —
    o lecție care își introduce singură fundamentul e gata de parcurs.
    """
    predate = {c.id for c in lectie.concepte}
    nepregatite, vazute = [], set()
    for concept in lectie.concepte:
        for prerechizit in concept.prerechizite:
            if prerechizit.id in vazute or prerechizit.id in predate:
                continue
            vazute.add(prerechizit.id)
            if bkt.p_concept(stari, prerechizit.id) < config.PRAG_FUNDAMENT:
                nepregatite.append(prerechizit)
    nepregatite.sort(key=lambda c: bkt.p_concept(stari, c.id))
    return nepregatite


def lectia_de_start(db: Session, user_id: int) -> dict:
    """Punctul de plecare recomandat după testul de plasament.

    Prima lecție (în ordinea cursului) care predă cel puțin un concept încă
    nestăpânit suficient — lecțiile dinaintea ei pot fi sărite cu încredere.
    """
    stari = bkt.probabilitati_utilizator(db, user_id)
    lectii = db.execute(
        select(Lectie).join(Capitol)
        .options(selectinload(Lectie.concepte))
        .order_by(Capitol.ordine, Lectie.ordine)
    ).scalars().all()
    for pozitie, lectie in enumerate(lectii):
        if any(bkt.p_concept(stari, c.id) < config.PRAG_CONCEPT_SLAB
               for c in lectie.concepte):
            return {"lectie_slug": lectie.slug, "titlu": lectie.titlu,
                    "lectii_sarite": pozitie}
    if lectii:
        return {"lectie_slug": lectii[0].slug, "titlu": lectii[0].titlu,
                "lectii_sarite": 0}
    return {"lectie_slug": None, "titlu": None, "lectii_sarite": 0}


def recomandari(db: Session, user_id: int, maxim: int = 4) -> list[dict]:
    rezultat: list[dict] = []
    stari = bkt.probabilitati_utilizator(db, user_id)

    # 1. Recapitulări scadente
    nr_scadente = _carduri_scadente(db, user_id)
    if nr_scadente > 0:
        rezultat.append({
            "tip": "recapitulare",
            "titlu": "Sesiune de recapitulare",
            "motiv": f"Ai {nr_scadente} întrebări scadente azi — recapitularea la timp "
                     "fixează cunoștințele în memoria de lungă durată.",
        })

    # 2. Exersarea conceptelor slabe (cu minim 2 observații, ca să nu reacționăm la zgomot)
    rezolvate = _exercitii_rezolvate(db, user_id)
    slabe = sorted(
        (s for s in stari.values()
         if s.nr_observatii >= 2 and s.p_cunoastere < config.PRAG_CONCEPT_SLAB),
        key=lambda s: s.p_cunoastere,
    )
    for stare in slabe:
        if len(rezultat) >= maxim - 1:
            break
        exercitiu = db.execute(
            select(Exercitiu)
            .join(Exercitiu.concepte)
            .where(Concept.id == stare.concept_id, Exercitiu.id.notin_(rezolvate or {0}))
            .order_by(Exercitiu.dificultate, Exercitiu.ordine)
            .limit(1)
        ).scalars().first()
        if exercitiu:
            concept = db.get(Concept, stare.concept_id)
            rezultat.append({
                "tip": "exercitiu",
                "titlu": exercitiu.titlu,
                "exercitiu_id": exercitiu.id,
                "lectie_slug": exercitiu.lectie.slug,
                "motiv": f"Stăpânirea conceptului „{concept.nume}” este la "
                         f"{round(stare.p_cunoastere * 100)}% — un exercițiu țintit o va ridica.",
            })

    # 3. Următoarea lecție al cărei fundament e pregătit
    vizitate = _lectii_vizitate(db, user_id)
    lectii = db.execute(
        select(Lectie)
        .join(Capitol)
        .options(selectinload(Lectie.concepte).selectinload(Concept.prerechizite))
        .order_by(Capitol.ordine, Lectie.ordine)
    ).scalars().all()
    urmatoarea = next((l for l in lectii if l.id not in vizitate), None)
    if urmatoarea is not None:
        nepregatite = prerechizite_nepregatite(urmatoarea, stari)
        slab = nepregatite[0] if nepregatite else None
        lectie_suport = next((l for l in lectii
                              if slab and any(c.id == slab.id for c in l.concepte)), None)
        # Dacă lecția-suport e chiar lecția următoare (își predă singură
        # prerechizitul), recomandarea rămâne lecția, cu motivul standard.
        if not nepregatite or lectie_suport is None or lectie_suport.id == urmatoarea.id:
            motiv = ("Începe parcursul cu prima lecție." if not vizitate else
                     "Următoarea lecție din parcursul tău — fundamentul ei e pregătit.")
            rezultat.append({
                "tip": "lectie",
                "titlu": urmatoarea.titlu,
                "lectie_slug": urmatoarea.slug,
                "motiv": motiv,
            })
        else:
            rezultat.append({
                "tip": "lectie",
                "titlu": lectie_suport.titlu,
                "lectie_slug": lectie_suport.slug,
                "motiv": f"Înainte de „{urmatoarea.titlu}”, consolidează conceptul "
                         f"„{slab.nume}” ({round(bkt.p_concept(stari, slab.id) * 100)}%), "
                         "care îi este prerechizit.",
            })

    # 4. Test adaptiv, când există destule concepte de evaluat
    concepte_studiate = sum(1 for s in stari.values() if s.nr_observatii > 0)
    if len(rezultat) < maxim and concepte_studiate >= 5:
        rezultat.append({
            "tip": "test_adaptiv",
            "titlu": "Test adaptiv",
            "motiv": "Un test scurt, generat pe conceptele tale cele mai slabe, "
                     "îi arată sistemului exact unde să te ajute.",
        })

    return rezultat[:maxim]
