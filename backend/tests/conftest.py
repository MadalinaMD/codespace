"""Configurarea pytest: bază de date în memorie + fabrici de obiecte de test."""
import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# backend/ pe sys.path, ca testele să importe pachetul `app`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import Baza  # noqa: E402
from app.models import (Capitol, Concept, Exercitiu, Intrebare, Lectie,  # noqa: E402
                        TestExercitiu, Utilizator)
from app.security import cripteaza_parola  # noqa: E402


@pytest.fixture()
def db():
    """Sesiune SQLAlchemy pe o bază SQLite în memorie, izolată per test.

    StaticPool + check_same_thread=False: TestClient rulează endpoint-urile
    în alt thread decât fixture-ul, iar baza din memorie trebuie să rămână
    aceeași conexiune pentru toți.
    """
    engine = create_engine("sqlite://",
                           connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Baza.metadata.create_all(engine)
    Sesiune = sessionmaker(bind=engine, expire_on_commit=False)
    sesiune = Sesiune()
    yield sesiune
    sesiune.close()
    engine.dispose()


@pytest.fixture()
def student(db):
    user = Utilizator(nume="Student Test", email="test@codespace.ro",
                      parola_hash=cripteaza_parola("Parola123!"), rol="student")
    db.add(user)
    db.commit()
    return user


def creeaza_concept(db, slug, nume=None, prerechizite=()):
    concept = Concept(slug=slug, nume=nume or slug.replace("_", " ").title())
    concept.prerechizite = list(prerechizite)
    db.add(concept)
    db.flush()
    return concept


def creeaza_capitol(db, slug="capitol-test", ordine=1):
    capitol = Capitol(slug=slug, titlu=f"Capitol {ordine}", ordine=ordine)
    db.add(capitol)
    db.flush()
    return capitol


def creeaza_lectie(db, capitol, slug, concepte=(), ordine=1):
    lectie = Lectie(capitol_id=capitol.id, slug=slug, titlu=slug.replace("-", " ").title(),
                    ordine=ordine, continut_md=f"## {slug}\n\nConținut de test.")
    lectie.concepte = list(concepte)
    db.add(lectie)
    db.flush()
    return lectie


def creeaza_exercitiu(db, lectie, concepte=(), titlu="Exercițiu test"):
    exercitiu = Exercitiu(
        lectie_id=lectie.id, titlu=titlu,
        enunt_md="Scrie funcția `dublu(n)` care returnează dublul lui n.",
        cod_start="def dublu(n):\n    pass\n",
        solutie_referinta="def dublu(n):\n    return n * 2\n",
        mod="functie", functie_nume="dublu",
    )
    exercitiu.concepte = list(concepte)
    db.add(exercitiu)
    db.flush()
    db.add(TestExercitiu(exercitiu_id=exercitiu.id, ordine=1, apel="dublu(2)", asteptat="4"))
    db.add(TestExercitiu(exercitiu_id=exercitiu.id, ordine=2, apel="dublu(-3)", asteptat="-6"))
    db.flush()
    return exercitiu


def creeaza_intrebare(db, capitol, concepte=(), text="2 + 2 = ?"):
    intrebare = Intrebare(capitol_id=capitol.id, text=text, varianta_corecta="4",
                          gresite_json=["3", "5", "22"], explicatie="Adunare simplă.")
    intrebare.concepte = list(concepte)
    db.add(intrebare)
    db.flush()
    return intrebare
