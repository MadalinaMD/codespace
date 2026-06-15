"""Repetiție spațiată — algoritmul SM-2 (SuperMemo, Wozniak 1990).

Fiecare întrebare greșită devine un "card" care revine la intervale
crescătoare: 1 zi → 6 zile → interval × factor de ușurință. Un răspuns
greșit resetează seria, iar factorul de ușurință scade (cardul revine
mai des). Calitatea răspunsului se notează pe scara SM-2 (0–5); pentru
grile folosim: corect = 4, greșit = 2.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta

from app import config

CALITATE_CORECT = 4
CALITATE_GRESIT = 2


@dataclass
class ProgramareSM2:
    factor_usurinta: float
    repetari: int
    interval_zile: float
    scadent_la: datetime


def urmatoarea_programare(
    factor_usurinta: float,
    repetari: int,
    interval_zile: float,
    calitate: int,
    acum: datetime | None = None,
) -> ProgramareSM2:
    """Aplică un pas SM-2 și returnează noua programare a cardului."""
    acum = acum or datetime.now()
    calitate = min(max(calitate, 0), 5)

    if calitate < 3:
        # Răspuns greșit: seria se reia, cardul revine mâine
        repetari_noi = 0
        interval_nou = 1.0
    else:
        repetari_noi = repetari + 1
        if repetari_noi == 1:
            interval_nou = 1.0
        elif repetari_noi == 2:
            interval_nou = 6.0
        else:
            interval_nou = round(interval_zile * factor_usurinta, 1)

    # Actualizarea factorului de ușurință (formula SM-2 originală)
    factor_nou = factor_usurinta + (0.1 - (5 - calitate) * (0.08 + (5 - calitate) * 0.02))
    factor_nou = max(config.SM2_FACTOR_MINIM, factor_nou)

    return ProgramareSM2(
        factor_usurinta=round(factor_nou, 3),
        repetari=repetari_noi,
        interval_zile=interval_nou,
        scadent_la=acum + timedelta(days=interval_nou),
    )


def card_este_invatat(repetari: int, interval_zile: float) -> bool:
    """Un card cu 3+ repetări corecte la rând și interval mare e considerat
    stăpânit — iese din coada activă (rămâne în istoric)."""
    return repetari >= 3 and interval_zile >= 14
