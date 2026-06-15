"""Bayesian Knowledge Tracing — modelul studentului.

Implementare după Corbett & Anderson (1995): pentru fiecare concept se
urmărește p(L) = probabilitatea ca studentul să-l cunoască. După fiecare
răspuns (corect/greșit) se calculează posteriorul Bayes folosind parametrii:

- p(S) "slip":  șansa unui răspuns greșit deși conceptul e cunoscut
- p(G) "guess": șansa unui răspuns corect deși conceptul nu e cunoscut
- p(T) "transfer": șansa de a învăța conceptul în urma interacțiunii

p(G) depinde de tipul activității: la o grilă cu 4 variante ghicirea are
~25% șansă, dar un exercițiu de cod care trece toate testele aproape că
nu poate fi "ghicit" (5%).
"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.models import Concept, StareConcept


def actualizeaza_probabilitate(
    p_cunoastere: float,
    corect: bool,
    p_alunecare: float = config.BKT_P_ALUNECARE,
    p_ghicire: float = 0.25,
    p_transfer: float = config.BKT_P_TRANSFER,
) -> float:
    """Un pas BKT: posterior Bayes condiționat de răspuns + pasul de învățare."""
    p = min(max(p_cunoastere, 0.0), 1.0)

    if corect:
        numarator = p * (1 - p_alunecare)
        numitor = p * (1 - p_alunecare) + (1 - p) * p_ghicire
    else:
        numarator = p * p_alunecare
        numitor = p * p_alunecare + (1 - p) * (1 - p_ghicire)

    posterior = numarator / numitor if numitor > 0 else p
    # Pasul de învățare: orice interacțiune e o ocazie de a învăța conceptul
    p_nou = posterior + (1 - posterior) * p_transfer
    return min(max(p_nou, 0.0), 1.0)


def obtine_stare(db: Session, user_id: int, concept_id: int) -> StareConcept:
    """Returnează starea BKT a utilizatorului pe concept (o creează la nevoie)."""
    stare = db.execute(
        select(StareConcept).where(StareConcept.user_id == user_id,
                                   StareConcept.concept_id == concept_id)
    ).scalar_one_or_none()
    if stare is None:
        stare = StareConcept(user_id=user_id, concept_id=concept_id,
                             p_cunoastere=config.BKT_P_INIT, nr_observatii=0)
        db.add(stare)
        db.flush()
    return stare


def inregistreaza_observatie(
    db: Session,
    user_id: int,
    concepte: list[Concept],
    corect: bool,
    tip_activitate: str,
) -> None:
    """Actualizează starea BKT pe toate conceptele implicate într-o activitate."""
    p_ghicire = config.BKT_P_GHICIRE.get(tip_activitate, 0.25)
    for concept in concepte:
        stare = obtine_stare(db, user_id, concept.id)
        stare.p_cunoastere = actualizeaza_probabilitate(
            stare.p_cunoastere, corect, p_ghicire=p_ghicire)
        stare.nr_observatii += 1
        stare.actualizat_la = datetime.now()


def probabilitati_utilizator(db: Session, user_id: int) -> dict[int, StareConcept]:
    """Toate stările BKT ale unui utilizator, indexate după concept_id."""
    stari = db.execute(
        select(StareConcept).where(StareConcept.user_id == user_id)
    ).scalars().all()
    return {s.concept_id: s for s in stari}


def p_concept(stari: dict[int, StareConcept], concept_id: int) -> float:
    """p(cunoaștere) pentru un concept; priorul BKT dacă nu există observații."""
    stare = stari.get(concept_id)
    return stare.p_cunoastere if stare else config.BKT_P_INIT
