"""Teste pentru modelul studentului (Bayesian Knowledge Tracing)."""
from app import config
from app.engine import bkt
from tests.conftest import creeaza_concept


def test_raspuns_corect_creste_probabilitatea():
    p_nou = bkt.actualizeaza_probabilitate(0.3, corect=True, p_ghicire=0.25)
    assert p_nou > 0.3


def test_raspuns_gresit_scade_probabilitatea():
    p_nou = bkt.actualizeaza_probabilitate(0.5, corect=False, p_ghicire=0.25)
    assert p_nou < 0.5


def test_probabilitatea_ramane_in_interval():
    p = 0.5
    for _ in range(50):
        p = bkt.actualizeaza_probabilitate(p, corect=True, p_ghicire=0.25)
    assert p <= 1.0
    p = 0.5
    for _ in range(50):
        p = bkt.actualizeaza_probabilitate(p, corect=False, p_ghicire=0.25)
    assert p >= 0.0


def test_exercitiul_e_dovada_mai_puternica_decat_grila():
    """p(ghicire) mic (exercițiu de cod) → un succes spune mai mult despre student."""
    p_quiz = bkt.actualizeaza_probabilitate(0.2, corect=True,
                                            p_ghicire=config.BKT_P_GHICIRE["quiz"])
    p_exercitiu = bkt.actualizeaza_probabilitate(0.2, corect=True,
                                                 p_ghicire=config.BKT_P_GHICIRE["exercitiu"])
    assert p_exercitiu > p_quiz


def test_succese_repetate_duc_la_stapanire():
    p = config.BKT_P_INIT
    for _ in range(6):
        p = bkt.actualizeaza_probabilitate(p, corect=True,
                                           p_ghicire=config.BKT_P_GHICIRE["exercitiu"])
    assert p >= config.PRAG_STAPANIRE


def test_inregistreaza_observatie_creeaza_si_actualizeaza_stari(db, student):
    c1 = creeaza_concept(db, "bucle_for")
    c2 = creeaza_concept(db, "liste")
    db.commit()

    bkt.inregistreaza_observatie(db, student.id, [c1, c2], corect=True, tip_activitate="exercitiu")
    db.commit()

    stari = bkt.probabilitati_utilizator(db, student.id)
    assert set(stari) == {c1.id, c2.id}
    assert all(s.nr_observatii == 1 for s in stari.values())
    assert all(s.p_cunoastere > config.BKT_P_INIT for s in stari.values())

    p_inainte = stari[c1.id].p_cunoastere
    bkt.inregistreaza_observatie(db, student.id, [c1], corect=False, tip_activitate="quiz")
    db.commit()
    stari = bkt.probabilitati_utilizator(db, student.id)
    assert stari[c1.id].nr_observatii == 2
    assert stari[c1.id].p_cunoastere < p_inainte


def test_p_concept_foloseste_priorul_fara_observatii():
    assert bkt.p_concept({}, 99) == config.BKT_P_INIT
