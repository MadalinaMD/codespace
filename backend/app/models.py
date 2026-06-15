"""Modelele ORM (SQLAlchemy 2.0) — schema completă a sistemului de tutoriat.

Organizare:
- conținut:       Concept, Capitol, Lectie, Exercitiu, TestExercitiu, Intrebare
- modelul studentului: StareConcept (BKT), CardRecapitulare (SM-2)
- activitate:     VizitaLectie, Submisie, IndiciuAcordat, TentativaQuiz,
                  RaspunsQuiz, TestAdaptiv, MesajChat
- gamificare:     EvenimentXP, ActivitateZi, Realizare, RealizareUtilizator
- profesor:       SchitaGenerata (conținut generat de AI, în așteptarea aprobării)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (JSON, Boolean, Column, DateTime, Float, ForeignKey,
                        Integer, String, Table, Text, UniqueConstraint)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Baza


def acum() -> datetime:
    return datetime.now()


# ── Utilizatori ─────────────────────────────────────────────────
class Utilizator(Baza):
    __tablename__ = "utilizatori"

    id: Mapped[int] = mapped_column(primary_key=True)
    nume: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    parola_hash: Mapped[str] = mapped_column(String(120))
    rol: Mapped[str] = mapped_column(String(20), default="student")  # student | profesor
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


# ── Modelul de domeniu: graful de concepte ──────────────────────
concept_prerechizite = Table(
    "concept_prerechizite",
    Baza.metadata,
    Column("concept_id", ForeignKey("concepte.id", ondelete="CASCADE"), primary_key=True),
    Column("prerechizit_id", ForeignKey("concepte.id", ondelete="CASCADE"), primary_key=True),
)

lectie_concepte = Table(
    "lectie_concepte",
    Baza.metadata,
    Column("lectie_id", ForeignKey("lectii.id", ondelete="CASCADE"), primary_key=True),
    Column("concept_id", ForeignKey("concepte.id", ondelete="CASCADE"), primary_key=True),
)

exercitiu_concepte = Table(
    "exercitiu_concepte",
    Baza.metadata,
    Column("exercitiu_id", ForeignKey("exercitii.id", ondelete="CASCADE"), primary_key=True),
    Column("concept_id", ForeignKey("concepte.id", ondelete="CASCADE"), primary_key=True),
)

intrebare_concepte = Table(
    "intrebare_concepte",
    Baza.metadata,
    Column("intrebare_id", ForeignKey("intrebari.id", ondelete="CASCADE"), primary_key=True),
    Column("concept_id", ForeignKey("concepte.id", ondelete="CASCADE"), primary_key=True),
)


class Concept(Baza):
    """Un nod din graful de concepte Python (ex: bucle for, dicționare)."""
    __tablename__ = "concepte"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    nume: Mapped[str] = mapped_column(String(120))
    descriere: Mapped[str] = mapped_column(Text, default="")
    ordine: Mapped[int] = mapped_column(Integer, default=0)

    prerechizite: Mapped[list["Concept"]] = relationship(
        secondary=concept_prerechizite,
        primaryjoin=id == concept_prerechizite.c.concept_id,
        secondaryjoin=id == concept_prerechizite.c.prerechizit_id,
    )


# ── Conținutul cursului ─────────────────────────────────────────
class Capitol(Baza):
    __tablename__ = "capitole"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    titlu: Mapped[str] = mapped_column(String(160))
    descriere: Mapped[str] = mapped_column(Text, default="")
    ordine: Mapped[int] = mapped_column(Integer, default=0)

    lectii: Mapped[list["Lectie"]] = relationship(back_populates="capitol",
                                                  order_by="Lectie.ordine",
                                                  cascade="all, delete-orphan")
    intrebari: Mapped[list["Intrebare"]] = relationship(back_populates="capitol",
                                                        cascade="all, delete-orphan")


class Lectie(Baza):
    __tablename__ = "lectii"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitol_id: Mapped[int] = mapped_column(ForeignKey("capitole.id", ondelete="CASCADE"))
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    titlu: Mapped[str] = mapped_column(String(160))
    ordine: Mapped[int] = mapped_column(Integer, default=0)
    continut_md: Mapped[str] = mapped_column(Text, default="")     # teoria, în Markdown
    cod_exemplu: Mapped[str] = mapped_column(Text, default="")     # exemplu rulabil în playground
    sursa: Mapped[str] = mapped_column(Text, default="")           # citarea bibliografică

    capitol: Mapped["Capitol"] = relationship(back_populates="lectii")
    concepte: Mapped[list["Concept"]] = relationship(secondary=lectie_concepte)
    exercitii: Mapped[list["Exercitiu"]] = relationship(back_populates="lectie",
                                                        order_by="Exercitiu.ordine",
                                                        cascade="all, delete-orphan")


class Exercitiu(Baza):
    """Exercițiu de programare evaluat automat prin teste."""
    __tablename__ = "exercitii"

    id: Mapped[int] = mapped_column(primary_key=True)
    lectie_id: Mapped[int] = mapped_column(ForeignKey("lectii.id", ondelete="CASCADE"))
    titlu: Mapped[str] = mapped_column(String(160))
    enunt_md: Mapped[str] = mapped_column(Text)
    cod_start: Mapped[str] = mapped_column(Text, default="")
    solutie_referinta: Mapped[str] = mapped_column(Text)           # validată la seed, nu pleacă spre client
    mod: Mapped[str] = mapped_column(String(20), default="functie")  # functie | program
    functie_nume: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    dificultate: Mapped[int] = mapped_column(Integer, default=1)   # 1 ușor … 3 greu
    ordine: Mapped[int] = mapped_column(Integer, default=0)

    lectie: Mapped["Lectie"] = relationship(back_populates="exercitii")
    concepte: Mapped[list["Concept"]] = relationship(secondary=exercitiu_concepte)
    teste: Mapped[list["TestExercitiu"]] = relationship(back_populates="exercitiu",
                                                        order_by="TestExercitiu.ordine",
                                                        cascade="all, delete-orphan")


class TestExercitiu(Baza):
    """Un caz de test al unui exercițiu (vizibil studentului).

    - mod "functie": `apel` (ex: "suma_pare([1, 2, 3])") + `asteptat` (literal Python)
    - mod "program": `stdin` (intrarea programului) + `asteptat` (stdout-ul așteptat)
    - teste de excepție: `apel` + `asteptat_eroare` (numele excepției așteptate)
    """
    __tablename__ = "teste_exercitii"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercitiu_id: Mapped[int] = mapped_column(ForeignKey("exercitii.id", ondelete="CASCADE"))
    ordine: Mapped[int] = mapped_column(Integer, default=0)
    apel: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stdin: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    asteptat: Mapped[str] = mapped_column(Text, default="")
    asteptat_eroare: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    exercitiu: Mapped["Exercitiu"] = relationship(back_populates="teste")


class Intrebare(Baza):
    """Întrebare grilă din banca unui capitol (folosită la quiz și recapitulare)."""
    __tablename__ = "intrebari"

    id: Mapped[int] = mapped_column(primary_key=True)
    capitol_id: Mapped[int] = mapped_column(ForeignKey("capitole.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(Text)
    varianta_corecta: Mapped[str] = mapped_column(Text)
    gresite_json: Mapped[list] = mapped_column(JSON, default=list)   # 3 variante greșite
    explicatie: Mapped[str] = mapped_column(Text, default="")
    dificultate: Mapped[int] = mapped_column(Integer, default=1)
    sursa: Mapped[str] = mapped_column(String(20), default="manual")  # manual | ai
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    capitol: Mapped["Capitol"] = relationship(back_populates="intrebari")
    concepte: Mapped[list["Concept"]] = relationship(secondary=intrebare_concepte)


# ── Modelul studentului ─────────────────────────────────────────
class StareConcept(Baza):
    """Starea BKT a unui utilizator pe un concept: p(cunoaștere)."""
    __tablename__ = "stari_concepte"
    __table_args__ = (UniqueConstraint("user_id", "concept_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    concept_id: Mapped[int] = mapped_column(ForeignKey("concepte.id", ondelete="CASCADE"))
    p_cunoastere: Mapped[float] = mapped_column(Float, default=0.2)
    nr_observatii: Mapped[int] = mapped_column(Integer, default=0)
    actualizat_la: Mapped[datetime] = mapped_column(DateTime, default=acum, onupdate=acum)

    concept: Mapped["Concept"] = relationship()


class CardRecapitulare(Baza):
    """Card de repetiție spațiată (SM-2) pentru o întrebare greșită."""
    __tablename__ = "carduri_recapitulare"
    __table_args__ = (UniqueConstraint("user_id", "intrebare_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    intrebare_id: Mapped[int] = mapped_column(ForeignKey("intrebari.id", ondelete="CASCADE"))
    factor_usurinta: Mapped[float] = mapped_column(Float, default=2.5)
    repetari: Mapped[int] = mapped_column(Integer, default=0)
    interval_zile: Mapped[float] = mapped_column(Float, default=0)
    scadent_la: Mapped[datetime] = mapped_column(DateTime, default=acum, index=True)
    ultima_calitate: Mapped[int] = mapped_column(Integer, default=0)

    intrebare: Mapped["Intrebare"] = relationship()


# ── Activitatea de învățare ─────────────────────────────────────
class VizitaLectie(Baza):
    __tablename__ = "vizite_lectii"
    __table_args__ = (UniqueConstraint("user_id", "lectie_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    lectie_id: Mapped[int] = mapped_column(ForeignKey("lectii.id", ondelete="CASCADE"))
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


class Submisie(Baza):
    """O trimitere de cod la un exercițiu, evaluată oficial pe server."""
    __tablename__ = "submisii"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    exercitiu_id: Mapped[int] = mapped_column(ForeignKey("exercitii.id", ondelete="CASCADE"), index=True)
    cod: Mapped[str] = mapped_column(Text)
    # acceptat | teste_esuate | eroare | timeout | blocat
    status: Mapped[str] = mapped_column(String(20))
    teste_total: Mapped[int] = mapped_column(Integer, default=0)
    teste_trecute: Mapped[int] = mapped_column(Integer, default=0)
    eroare_categorie: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    eroare_mesaj: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detalii_json: Mapped[list] = mapped_column(JSON, default=list)  # rezultate per test
    indicii_folosite: Mapped[int] = mapped_column(Integer, default=0)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


class IndiciuAcordat(Baza):
    """Jurnalul indiciilor progresive cerute de student la un exercițiu."""
    __tablename__ = "indicii_acordate"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    exercitiu_id: Mapped[int] = mapped_column(ForeignKey("exercitii.id", ondelete="CASCADE"))
    nivel: Mapped[int] = mapped_column(Integer)
    continut: Mapped[str] = mapped_column(Text)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


class TentativaQuiz(Baza):
    """O tentativă de quiz pe capitol; răspunsurile se evaluează pe server."""
    __tablename__ = "tentative_quiz"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    capitol_id: Mapped[int] = mapped_column(ForeignKey("capitole.id", ondelete="CASCADE"))
    intrebari_json: Mapped[list] = mapped_column(JSON, default=list)  # id-urile întrebărilor servite
    scor: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    finalizat: Mapped[bool] = mapped_column(Boolean, default=False)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)

    raspunsuri: Mapped[list["RaspunsQuiz"]] = relationship(back_populates="tentativa",
                                                           cascade="all, delete-orphan")


class RaspunsQuiz(Baza):
    __tablename__ = "raspunsuri_quiz"
    __table_args__ = (UniqueConstraint("tentativa_id", "intrebare_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    tentativa_id: Mapped[int] = mapped_column(ForeignKey("tentative_quiz.id", ondelete="CASCADE"))
    intrebare_id: Mapped[int] = mapped_column(ForeignKey("intrebari.id", ondelete="CASCADE"))
    raspuns_text: Mapped[str] = mapped_column(Text)
    corect: Mapped[bool] = mapped_column(Boolean)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)

    tentativa: Mapped["TentativaQuiz"] = relationship(back_populates="raspunsuri")


class TestAdaptiv(Baza):
    """Test generat pe conceptele slabe; răspunsurile corecte rămân pe server.

    `tip` distinge testul adaptiv obișnuit de testul de PLASAMENT (calibrarea
    inițială a modelului BKT, la primul contact cu platforma).
    """
    __tablename__ = "teste_adaptive"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    tip: Mapped[str] = mapped_column(String(20), default="adaptiv")  # adaptiv | plasament
    # listă de {text, corecta, gresite, explicatie, concept_slug, sursa}
    intrebari_json: Mapped[list] = mapped_column(JSON, default=list)
    # dict {index: {raspuns, corect}}
    raspunsuri_json: Mapped[dict] = mapped_column(JSON, default=dict)
    concepte_vizate: Mapped[list] = mapped_column(JSON, default=list)
    scor: Mapped[int] = mapped_column(Integer, default=0)
    total: Mapped[int] = mapped_column(Integer, default=0)
    finalizat: Mapped[bool] = mapped_column(Boolean, default=False)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


class MesajChat(Baza):
    """Istoricul conversației cu tutorele AI."""
    __tablename__ = "mesaje_chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    rol: Mapped[str] = mapped_column(String(10))  # user | asistent
    continut: Mapped[str] = mapped_column(Text)
    surse_json: Mapped[list] = mapped_column(JSON, default=list)
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


# ── Gamificare ──────────────────────────────────────────────────
class EvenimentXP(Baza):
    __tablename__ = "evenimente_xp"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    tip: Mapped[str] = mapped_column(String(30))
    puncte: Mapped[int] = mapped_column(Integer)
    descriere: Mapped[str] = mapped_column(Text, default="")
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)


class ActivitateZi(Baza):
    __tablename__ = "activitate_zile"
    __table_args__ = (UniqueConstraint("user_id", "zi"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    zi: Mapped[str] = mapped_column(String(10))  # data ISO: "2026-06-11"


class Realizare(Baza):
    __tablename__ = "realizari"

    id: Mapped[int] = mapped_column(primary_key=True)
    cod: Mapped[str] = mapped_column(String(40), unique=True)
    titlu: Mapped[str] = mapped_column(String(80))
    descriere: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(10), default="🏅")
    ordine: Mapped[int] = mapped_column(Integer, default=0)


class RealizareUtilizator(Baza):
    __tablename__ = "realizari_utilizatori"
    __table_args__ = (UniqueConstraint("user_id", "realizare_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("utilizatori.id", ondelete="CASCADE"), index=True)
    realizare_id: Mapped[int] = mapped_column(ForeignKey("realizari.id", ondelete="CASCADE"))
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)

    realizare: Mapped["Realizare"] = relationship()


# ── Conținut generat de AI, în așteptarea aprobării ─────────────
class SchitaGenerata(Baza):
    """Întrebare/exercițiu generat de AI; intră în curs doar după aprobarea profesorului."""
    __tablename__ = "schite_generate"

    id: Mapped[int] = mapped_column(primary_key=True)
    tip: Mapped[str] = mapped_column(String(20))  # intrebare | exercitiu
    concept_slug: Mapped[str] = mapped_column(String(60))
    capitol_id: Mapped[Optional[int]] = mapped_column(ForeignKey("capitole.id", ondelete="SET NULL"), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    validat: Mapped[bool] = mapped_column(Boolean, default=False)
    raport_validare: Mapped[str] = mapped_column(Text, default="")
    stare: Mapped[str] = mapped_column(String(20), default="propusa")  # propusa | aprobata | respinsa
    creat_la: Mapped[datetime] = mapped_column(DateTime, default=acum)
