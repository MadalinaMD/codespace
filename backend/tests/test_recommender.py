"""Teste pentru recomandator și pentru gamificare (streak, nivele)."""
from datetime import date, datetime, timedelta

from app.engine import gamification, recommender
from app.models import ActivitateZi, CardRecapitulare, StareConcept, VizitaLectie
from tests.conftest import (creeaza_capitol, creeaza_concept, creeaza_exercitiu,
                            creeaza_intrebare, creeaza_lectie)


def _curs_minimal(db):
    """Două lecții: a doua are un concept cu prerechizit predat de prima."""
    capitol = creeaza_capitol(db)
    variabile = creeaza_concept(db, "variabile")
    bucle = creeaza_concept(db, "bucle_for", prerechizite=[variabile])
    lectie1 = creeaza_lectie(db, capitol, "variabile-lectie", concepte=[variabile], ordine=1)
    lectie2 = creeaza_lectie(db, capitol, "bucle-lectie", concepte=[bucle], ordine=2)
    db.commit()
    return capitol, variabile, bucle, lectie1, lectie2


def test_utilizator_nou_primeste_prima_lectie(db, student):
    _, _, _, lectie1, _ = _curs_minimal(db)
    rec = recommender.recomandari(db, student.id)
    lectii = [r for r in rec if r["tip"] == "lectie"]
    assert lectii and lectii[0]["lectie_slug"] == lectie1.slug
    assert "motiv" in lectii[0]


def test_recapitularile_scadente_au_prioritate(db, student):
    capitol, variabile, *_ = _curs_minimal(db)
    intrebare = creeaza_intrebare(db, capitol, concepte=[variabile])
    db.add(CardRecapitulare(user_id=student.id, intrebare_id=intrebare.id,
                            scadent_la=datetime.now() - timedelta(hours=1)))
    db.commit()
    rec = recommender.recomandari(db, student.id)
    assert rec[0]["tip"] == "recapitulare"
    assert "1" in rec[0]["motiv"]


def test_conceptul_slab_primeste_exercitiu_cu_motiv_procentual(db, student):
    _, variabile, _, lectie1, _ = _curs_minimal(db)
    creeaza_exercitiu(db, lectie1, concepte=[variabile])
    db.add(StareConcept(user_id=student.id, concept_id=variabile.id,
                        p_cunoastere=0.35, nr_observatii=3))
    db.commit()
    rec = recommender.recomandari(db, student.id)
    exercitii = [r for r in rec if r["tip"] == "exercitiu"]
    assert exercitii
    assert "35%" in exercitii[0]["motiv"]


def test_prerechizitul_slab_blocheaza_lectia_urmatoare(db, student):
    _, variabile, _, lectie1, lectie2 = _curs_minimal(db)
    db.add(VizitaLectie(user_id=student.id, lectie_id=lectie1.id))
    db.add(StareConcept(user_id=student.id, concept_id=variabile.id,
                        p_cunoastere=0.3, nr_observatii=1))
    db.commit()
    rec = recommender.recomandari(db, student.id)
    lectii = [r for r in rec if r["tip"] == "lectie"]
    # Sistemul recomandă consolidarea lecției-suport, nu lecția nouă
    assert lectii and lectii[0]["lectie_slug"] == lectie1.slug
    assert "prerechizit" in lectii[0]["motiv"]


def test_lectia_urmatoare_se_deschide_cand_fundamentul_e_gata(db, student):
    _, variabile, _, lectie1, lectie2 = _curs_minimal(db)
    db.add(VizitaLectie(user_id=student.id, lectie_id=lectie1.id))
    db.add(StareConcept(user_id=student.id, concept_id=variabile.id,
                        p_cunoastere=0.8, nr_observatii=4))
    db.commit()
    rec = recommender.recomandari(db, student.id)
    lectii = [r for r in rec if r["tip"] == "lectie"]
    assert lectii and lectii[0]["lectie_slug"] == lectie2.slug


# ── Gamificare ──────────────────────────────────────────────────
def test_streak_se_calculeaza_pe_zile_consecutive(db, student):
    azi = date.today()
    for delta in (0, 1, 2):
        db.add(ActivitateZi(user_id=student.id, zi=(azi - timedelta(days=delta)).isoformat()))
    db.add(ActivitateZi(user_id=student.id, zi=(azi - timedelta(days=5)).isoformat()))
    db.commit()
    assert gamification.calculeaza_streak(db, student.id) == 3


def test_streak_nu_se_rupe_daca_azi_nu_ai_intrat_inca(db, student):
    azi = date.today()
    for delta in (1, 2):
        db.add(ActivitateZi(user_id=student.id, zi=(azi - timedelta(days=delta)).isoformat()))
    db.commit()
    assert gamification.calculeaza_streak(db, student.id) == 2


def test_streak_zero_fara_activitate_recenta(db, student):
    azi = date.today()
    db.add(ActivitateZi(user_id=student.id, zi=(azi - timedelta(days=3)).isoformat()))
    db.commit()
    assert gamification.calculeaza_streak(db, student.id) == 0


def test_curba_nivelelor():
    assert gamification.detalii_nivel(0)["nivel"] == 1
    assert gamification.detalii_nivel(99)["nivel"] == 1
    assert gamification.detalii_nivel(100)["nivel"] == 2
    assert gamification.detalii_nivel(300)["nivel"] == 3
    detalii = gamification.detalii_nivel(150)
    assert detalii["xp_in_nivel"] == 50
    assert detalii["xp_necesar_nivel"] == 200


def test_realizarile_se_deblocheaza_o_singura_data(db, student):
    capitol = creeaza_capitol(db)
    concept = creeaza_concept(db, "test_concept")
    lectie = creeaza_lectie(db, capitol, "lectie-realizare", concepte=[concept])
    gamification.seed_realizari(db)
    db.add(VizitaLectie(user_id=student.id, lectie_id=lectie.id))
    db.commit()

    noi = gamification.verifica_realizari(db, student.id)
    db.commit()
    assert any(r["cod"] == "primul_pas" for r in noi)

    din_nou = gamification.verifica_realizari(db, student.id)
    db.commit()
    assert not any(r["cod"] == "primul_pas" for r in din_nou)
