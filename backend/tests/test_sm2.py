"""Teste pentru planificatorul de repetiție spațiată (SM-2)."""
from datetime import datetime, timedelta

from app import config
from app.engine import sm2


def test_prima_repetare_corecta():
    p = sm2.urmatoarea_programare(2.5, repetari=0, interval_zile=0,
                                  calitate=sm2.CALITATE_CORECT)
    assert p.repetari == 1
    assert p.interval_zile == 1.0


def test_a_doua_repetare_corecta():
    p = sm2.urmatoarea_programare(2.5, repetari=1, interval_zile=1,
                                  calitate=sm2.CALITATE_CORECT)
    assert p.repetari == 2
    assert p.interval_zile == 6.0


def test_intervalele_cresc_geometric():
    p = sm2.urmatoarea_programare(2.5, repetari=2, interval_zile=6,
                                  calitate=sm2.CALITATE_CORECT)
    assert p.repetari == 3
    assert p.interval_zile == 15.0  # 6 × 2.5


def test_raspunsul_gresit_reseteaza_seria():
    p = sm2.urmatoarea_programare(2.5, repetari=3, interval_zile=15,
                                  calitate=sm2.CALITATE_GRESIT)
    assert p.repetari == 0
    assert p.interval_zile == 1.0
    assert p.factor_usurinta < 2.5  # cardul devine "mai greu"


def test_factorul_nu_scade_sub_minim():
    factor = 1.3
    for _ in range(10):
        p = sm2.urmatoarea_programare(factor, 0, 1, calitate=0)
        factor = p.factor_usurinta
    assert factor == config.SM2_FACTOR_MINIM


def test_scadenta_respecta_intervalul():
    start = datetime(2026, 6, 11, 12, 0)
    p = sm2.urmatoarea_programare(2.5, 1, 1, calitate=sm2.CALITATE_CORECT, acum=start)
    assert p.scadent_la == start + timedelta(days=6)


def test_card_invatat():
    assert not sm2.card_este_invatat(repetari=2, interval_zile=6)
    assert not sm2.card_este_invatat(repetari=3, interval_zile=10)
    assert sm2.card_este_invatat(repetari=3, interval_zile=15)
