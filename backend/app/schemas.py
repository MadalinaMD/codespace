"""Modele Pydantic pentru validarea datelor de intrare."""
import re
from typing import Optional

from pydantic import BaseModel, field_validator

from app import config

_email_re = re.compile(config.EMAIL_REGEX)
_parola_re = re.compile(config.PAROLA_REGEX)
# Caractere de control invizibile (cu excepția tab/newline)
_control_re = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _curata(text: str) -> str:
    if text is None:
        return ""
    return _control_re.sub("", text).strip()


def _valideaza_email(v: str) -> str:
    v = _curata(v).lower()
    if not _email_re.match(v):
        raise ValueError("Adresa de email nu este validă.")
    return v


# ── Autentificare ───────────────────────────────────────────────
class DateInregistrare(BaseModel):
    nume: str
    email: str
    parola: str

    @field_validator("nume")
    @classmethod
    def _nume(cls, v: str) -> str:
        v = _curata(v)
        if not (config.MIN_LUNGIME_NUME <= len(v) <= config.MAX_LUNGIME_NUME):
            raise ValueError(
                f"Numele trebuie să aibă între {config.MIN_LUNGIME_NUME} și {config.MAX_LUNGIME_NUME} caractere.")
        if not re.match(r"^[A-Za-zĂÂÎȘȚăâîșț\s.\-']+$", v):
            raise ValueError("Numele conține caractere nepermise.")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _valideaza_email(v)

    @field_validator("parola")
    @classmethod
    def _parola(cls, v: str) -> str:
        if not _parola_re.match(v or ""):
            raise ValueError("Parola: minim 8 caractere, literă mare, literă mică, cifră și caracter special.")
        return v


class DateLogin(BaseModel):
    email: str
    parola: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _valideaza_email(v)

    @field_validator("parola")
    @classmethod
    def _parola(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("Parola este obligatorie.")
        return v


class CerereResetParola(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return _valideaza_email(v)


class SchimbareParola(BaseModel):
    parola_actuala: str
    parola_noua: str

    @field_validator("parola_noua")
    @classmethod
    def _parola(cls, v: str) -> str:
        if not _parola_re.match(v or ""):
            raise ValueError("Parola nouă: minim 8 caractere, literă mare, literă mică, cifră și caracter special.")
        return v


# ── Exerciții ───────────────────────────────────────────────────
class TrimitereCod(BaseModel):
    cod: str

    @field_validator("cod")
    @classmethod
    def _cod(cls, v: str) -> str:
        v = (v or "").replace("\r\n", "\n")
        if not v.strip():
            raise ValueError("Codul nu poate fi gol.")
        if len(v) > config.MAX_LUNGIME_COD:
            raise ValueError(f"Codul depășește limita de {config.MAX_LUNGIME_COD} caractere.")
        return v


class CerereIndiciu(BaseModel):
    cod: str = ""
    nivel: int = 1

    @field_validator("nivel")
    @classmethod
    def _nivel(cls, v: int) -> int:
        if not 1 <= v <= config.MAX_NIVEL_INDICIU:
            raise ValueError(f"Nivelul indiciului trebuie să fie între 1 și {config.MAX_NIVEL_INDICIU}.")
        return v


# ── Quiz / recapitulare / test adaptiv ──────────────────────────
class RaspunsLaIntrebare(BaseModel):
    intrebare_id: int
    raspuns: str

    @field_validator("raspuns")
    @classmethod
    def _raspuns(cls, v: str) -> str:
        v = _curata(v)
        if not v:
            raise ValueError("Răspunsul nu poate fi gol.")
        return v


class RaspunsLaIndex(BaseModel):
    index: int
    raspuns: str

    @field_validator("raspuns")
    @classmethod
    def _raspuns(cls, v: str) -> str:
        v = _curata(v)
        if not v:
            raise ValueError("Răspunsul nu poate fi gol.")
        return v


# ── Tutore AI ───────────────────────────────────────────────────
class IntrebareChat(BaseModel):
    intrebare: str
    lectie_slug: Optional[str] = None

    @field_validator("intrebare")
    @classmethod
    def _intrebare(cls, v: str) -> str:
        v = _curata(v)
        if len(v) < 3:
            raise ValueError("Întrebarea e prea scurtă (minim 3 caractere).")
        if len(v) > config.MAX_LUNGIME_INTREBARE:
            raise ValueError(f"Întrebarea e prea lungă (maxim {config.MAX_LUNGIME_INTREBARE} caractere).")
        return v


# ── Profesor ────────────────────────────────────────────────────
class CerereGenerare(BaseModel):
    concept_slug: str
    capitol_id: Optional[int] = None
    numar: int = 3

    @field_validator("numar")
    @classmethod
    def _numar(cls, v: int) -> int:
        if not 1 <= v <= 8:
            raise ValueError("Se pot genera între 1 și 8 elemente odată.")
        return v


class EditareLectie(BaseModel):
    continut_md: Optional[str] = None
    cod_exemplu: Optional[str] = None
    titlu: Optional[str] = None


class IntrebareNoua(BaseModel):
    capitol_id: int
    text: str
    varianta_corecta: str
    gresite: list[str]
    explicatie: str = ""
    dificultate: int = 1
    concepte: list[str] = []

    @field_validator("text", "varianta_corecta")
    @classmethod
    def _nevid(cls, v: str) -> str:
        v = _curata(v)
        if not v:
            raise ValueError("Câmp obligatoriu.")
        return v

    @field_validator("gresite")
    @classmethod
    def _gresite(cls, v: list[str]) -> list[str]:
        v = [_curata(x) for x in v if _curata(x)]
        if len(v) != 3:
            raise ValueError("Sunt necesare exact 3 variante greșite.")
        return v
