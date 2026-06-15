"""Gamificare: XP din rezultate, nivele, streak zilnic real și realizări."""
from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import config
from app.models import (ActivitateZi, Capitol, EvenimentXP, Realizare,
                        RealizareUtilizator, StareConcept, Submisie,
                        TentativaQuiz, VizitaLectie)

# (cod, titlu, descriere, icon)
REALIZARI = [
    ("primul_pas", "Primul pas", "Ai deschis prima lecție", "🚀"),
    ("prima_solutie", "Prima soluție", "Primul exercițiu rezolvat corect", "✅"),
    ("explorator", "Explorator", "Ai parcurs 10 lecții", "🧭"),
    ("fara_plase", "Fără plase de siguranță", "5 exerciții rezolvate fără niciun indiciu", "🎯"),
    ("perfectionist", "Perfecționist", "Un quiz încheiat fără nicio greșeală", "💯"),
    ("serie_3", "Serie de 3", "Activitate 3 zile la rând", "🔥"),
    ("serie_7", "Serie de 7", "Activitate 7 zile la rând", "⚡"),
    ("maestru_concept", "Primul concept stăpânit", "Un concept adus la nivel de măiestrie", "🌟"),
    ("polimat", "Polimat", "5 concepte stăpânite", "🏅"),
    ("recapitulant", "Memorie de fier", "20 de recapitulări corecte", "🔁"),
    ("capitol_complet", "Capitol încheiat", "Primul quiz de capitol finalizat", "📗"),
    ("absolvent", "Absolvent CodeSpace", "Quiz-ul fiecărui capitol finalizat", "👑"),
]


# ── XP și nivele ────────────────────────────────────────────────
def acorda_xp(db: Session, user_id: int, tip: str, puncte: int, descriere: str = "") -> int:
    if puncte <= 0:
        return 0
    db.add(EvenimentXP(user_id=user_id, tip=tip, puncte=puncte, descriere=descriere))
    return puncte


def total_xp(db: Session, user_id: int) -> int:
    return db.execute(
        select(func.coalesce(func.sum(EvenimentXP.puncte), 0))
        .where(EvenimentXP.user_id == user_id)
    ).scalar_one()


def _prag_nivel(nivel: int) -> int:
    """XP cumulat necesar pentru a atinge un nivel (creștere pătratică)."""
    return 50 * (nivel - 1) * nivel  # 0, 100, 300, 600, 1000, ...


def detalii_nivel(xp: int) -> dict:
    nivel = 1
    while _prag_nivel(nivel + 1) <= xp:
        nivel += 1
    prag_curent, prag_urmator = _prag_nivel(nivel), _prag_nivel(nivel + 1)
    castigat = xp - prag_curent
    necesar = prag_urmator - prag_curent
    return {
        "nivel": nivel,
        "xp_total": xp,
        "xp_in_nivel": castigat,
        "xp_necesar_nivel": necesar,
        "progres_nivel": round(castigat / necesar * 100) if necesar else 100,
    }


# ── Activitate zilnică și streak ────────────────────────────────
def inregistreaza_activitate(db: Session, user_id: int) -> None:
    azi = date.today().isoformat()
    exista = db.execute(
        select(ActivitateZi.id).where(ActivitateZi.user_id == user_id,
                                      ActivitateZi.zi == azi)
    ).scalar_one_or_none()
    if exista is None:
        db.add(ActivitateZi(user_id=user_id, zi=azi))


def calculeaza_streak(db: Session, user_id: int) -> int:
    """Numărul de zile consecutive cu activitate, terminând azi sau ieri.

    (Dacă azi nu ai intrat încă, seria de până ieri nu e considerată ruptă.)
    """
    zile = {
        r for (r,) in db.execute(
            select(ActivitateZi.zi).where(ActivitateZi.user_id == user_id)
        ).all()
    }
    if not zile:
        return 0
    azi = date.today()
    start = azi if azi.isoformat() in zile else azi - timedelta(days=1)
    if start.isoformat() not in zile:
        return 0
    streak = 0
    zi = start
    while zi.isoformat() in zile:
        streak += 1
        zi -= timedelta(days=1)
    return streak


def calendar_activitate(db: Session, user_id: int, nr_zile: int = 30) -> list[dict]:
    """Ultimele `nr_zile` zile, cu marcaj de activitate (pentru mini-calendarul din profil)."""
    zile_active = {
        r for (r,) in db.execute(
            select(ActivitateZi.zi).where(ActivitateZi.user_id == user_id)
        ).all()
    }
    azi = date.today()
    rezultat = []
    for delta in range(nr_zile - 1, -1, -1):
        zi = azi - timedelta(days=delta)
        rezultat.append({"zi": zi.isoformat(), "activ": zi.isoformat() in zile_active})
    return rezultat


# ── Realizări ───────────────────────────────────────────────────
def seed_realizari(db: Session) -> None:
    existente = {r.cod for r in db.execute(select(Realizare)).scalars().all()}
    for ordine, (cod, titlu, descriere, icon) in enumerate(REALIZARI):
        if cod not in existente:
            db.add(Realizare(cod=cod, titlu=titlu, descriere=descriere,
                             icon=icon, ordine=ordine))


def _statistici_realizari(db: Session, user_id: int) -> dict:
    lectii = db.execute(
        select(func.count()).select_from(VizitaLectie).where(VizitaLectie.user_id == user_id)
    ).scalar_one()
    exercitii_ok = db.execute(
        select(func.count(func.distinct(Submisie.exercitiu_id)))
        .where(Submisie.user_id == user_id, Submisie.status == "acceptat")
    ).scalar_one()
    fara_indicii = db.execute(
        select(func.count(func.distinct(Submisie.exercitiu_id)))
        .where(Submisie.user_id == user_id, Submisie.status == "acceptat",
               Submisie.indicii_folosite == 0)
    ).scalar_one()
    quiz_perfect = db.execute(
        select(func.count()).select_from(TentativaQuiz)
        .where(TentativaQuiz.user_id == user_id, TentativaQuiz.finalizat,
               TentativaQuiz.total > 0, TentativaQuiz.scor == TentativaQuiz.total)
    ).scalar_one()
    capitole_cu_quiz = db.execute(
        select(func.count(func.distinct(TentativaQuiz.capitol_id)))
        .where(TentativaQuiz.user_id == user_id, TentativaQuiz.finalizat)
    ).scalar_one()
    total_capitole = db.execute(select(func.count()).select_from(Capitol)).scalar_one()
    concepte_stapanite = db.execute(
        select(func.count()).select_from(StareConcept)
        .where(StareConcept.user_id == user_id,
               StareConcept.p_cunoastere >= config.PRAG_STAPANIRE)
    ).scalar_one()
    recapitulari_corecte = db.execute(
        select(func.count()).select_from(EvenimentXP)
        .where(EvenimentXP.user_id == user_id, EvenimentXP.tip == "recapitulare")
    ).scalar_one()
    return {
        "lectii": lectii, "exercitii_ok": exercitii_ok, "fara_indicii": fara_indicii,
        "quiz_perfect": quiz_perfect, "capitole_cu_quiz": capitole_cu_quiz,
        "total_capitole": total_capitole, "concepte_stapanite": concepte_stapanite,
        "recapitulari_corecte": recapitulari_corecte,
        "streak": calculeaza_streak(db, user_id),
    }


def _conditii(s: dict) -> dict:
    return {
        "primul_pas": s["lectii"] >= 1,
        "prima_solutie": s["exercitii_ok"] >= 1,
        "explorator": s["lectii"] >= 10,
        "fara_plase": s["fara_indicii"] >= 5,
        "perfectionist": s["quiz_perfect"] >= 1,
        "serie_3": s["streak"] >= 3,
        "serie_7": s["streak"] >= 7,
        "maestru_concept": s["concepte_stapanite"] >= 1,
        "polimat": s["concepte_stapanite"] >= 5,
        "recapitulant": s["recapitulari_corecte"] >= 20,
        "capitol_complet": s["capitole_cu_quiz"] >= 1,
        "absolvent": s["total_capitole"] > 0 and s["capitole_cu_quiz"] >= s["total_capitole"],
    }


def verifica_realizari(db: Session, user_id: int) -> list[dict]:
    """Deblochează realizările îndeplinite; returnează lista celor noi (pentru toast-uri)."""
    statistici = _statistici_realizari(db, user_id)
    conditii = _conditii(statistici)
    definitii = {r.cod: r for r in db.execute(select(Realizare)).scalars().all()}
    deblocate = {
        ru.realizare_id for ru in db.execute(
            select(RealizareUtilizator).where(RealizareUtilizator.user_id == user_id)
        ).scalars().all()
    }
    noi = []
    for cod, indeplinit in conditii.items():
        definitie = definitii.get(cod)
        if definitie and indeplinit and definitie.id not in deblocate:
            db.add(RealizareUtilizator(user_id=user_id, realizare_id=definitie.id))
            noi.append({"cod": cod, "titlu": definitie.titlu, "icon": definitie.icon})
    return noi


def profil_gamificare(db: Session, user_id: int) -> dict:
    xp = total_xp(db, user_id)
    nivel = detalii_nivel(xp)
    toate = db.execute(select(Realizare).order_by(Realizare.ordine)).scalars().all()
    deblocate = {
        ru.realizare_id for ru in db.execute(
            select(RealizareUtilizator).where(RealizareUtilizator.user_id == user_id)
        ).scalars().all()
    }
    return {
        **nivel,
        "streak": calculeaza_streak(db, user_id),
        "realizari": [{
            "cod": r.cod, "titlu": r.titlu, "descriere": r.descriere,
            "icon": r.icon, "deblocata": r.id in deblocate,
        } for r in toate],
        "realizari_deblocate": len(deblocate),
        "realizari_total": len(toate),
    }
