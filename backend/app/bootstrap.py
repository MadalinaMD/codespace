"""Datele minime de funcționare: schema, realizările și conturile implicite.

Apelat și la pornirea serverului (main.py), și de scriptul de seed — idempotent.
"""
from sqlalchemy import select, text

from app import config
from app.db import Baza, SesiuneLocala, engine
from app.engine import gamification
from app.models import Utilizator
from app.security import cripteaza_parola


def _adauga_coloana(tabel: str, coloana: str, definitie: str) -> None:
    """Migrație idempotentă: adaugă o coloană doar dacă lipsește (SQLite)."""
    with engine.connect() as conexiune:
        existente = conexiune.execute(text(f"PRAGMA table_info({tabel})")).fetchall()
        if not any(rand[1] == coloana for rand in existente):
            conexiune.execute(text(f"ALTER TABLE {tabel} ADD COLUMN {coloana} {definitie}"))
            conexiune.commit()


def asigura_date_minime() -> None:
    Baza.metadata.create_all(engine)
    # Migrații pentru baze create înainte de adăugarea coloanelor noi
    _adauga_coloana("teste_adaptive", "tip", "VARCHAR(20) DEFAULT 'adaptiv'")
    db = SesiuneLocala()
    try:
        gamification.seed_realizari(db)
        conturi = [
            (config.PROFESOR_EMAIL, config.PROFESOR_NUME, config.PROFESOR_PAROLA, "profesor"),
            (config.STUDENT_DEMO_EMAIL, config.STUDENT_DEMO_NUME, config.STUDENT_DEMO_PAROLA, "student"),
        ]
        for email, nume, parola, rol in conturi:
            exista = db.execute(
                select(Utilizator).where(Utilizator.email == email)
            ).scalar_one_or_none()
            if exista is None:
                db.add(Utilizator(nume=nume, email=email,
                                  parola_hash=cripteaza_parola(parola), rol=rol))
        db.commit()
    finally:
        db.close()
