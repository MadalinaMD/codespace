"""Autentificare: înregistrare, login, resetare parolă, profil, schimbarea parolei.

Notă de securitate: aplicația e locală și nu are server de email, așa că „Ai uitat
parola?” generează o parolă temporară puternică (SystemRandom) și o afișează o
singură dată pe ecran. Endpoint-ul e limitat ca debit (anti-abuz) și utilizatorul
e îndemnat să-și schimbe imediat parola din cont. Într-un deploy real, parola s-ar
trimite printr-un link de unică folosință pe email — vezi discuția din lucrare.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.deps import get_db, utilizator_curent
from app.models import Utilizator
from app.schemas import (CerereResetParola, DateInregistrare, DateLogin,
                         SchimbareParola)
from app.security import (creeaza_token, cripteaza_parola,
                         genereaza_parola_temporara, limitator_reset,
                         verifica_parola)

router = APIRouter(prefix="/auth", tags=["autentificare"])


@router.post("/inregistrare")
def inregistrare(date: DateInregistrare, db: Session = Depends(get_db)):
    utilizator = Utilizator(nume=date.nume, email=date.email,
                            parola_hash=cripteaza_parola(date.parola))
    db.add(utilizator)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Există deja un cont cu acest email.")
    return {"mesaj": "Cont creat cu succes! Te poți autentifica."}


@router.post("/login")
def login(date: DateLogin, db: Session = Depends(get_db)):
    utilizator = db.execute(
        select(Utilizator).where(Utilizator.email == date.email)
    ).scalar_one_or_none()
    if utilizator is None or not verifica_parola(date.parola, utilizator.parola_hash):
        raise HTTPException(status_code=401, detail="Email sau parolă incorecte.")
    return {
        "token": creeaza_token(utilizator.email, utilizator.rol),
        "nume": utilizator.nume,
        "email": utilizator.email,
        "rol": utilizator.rol,
    }


@router.post("/reset-parola")
def reset_parola(date: CerereResetParola, request: Request, db: Session = Depends(get_db)):
    """„Ai uitat parola?”: generează o parolă temporară și o întoarce o singură dată.

    Limitat la 5 cereri / 10 minute / IP. Recomandăm schimbarea parolei imediat
    după autentificare, din contul propriu (/auth/schimba-parola).
    """
    ip = request.client.host if request.client else "necunoscut"
    if not limitator_reset.permite(ip):
        raise HTTPException(status_code=429,
                            detail="Prea multe cereri de resetare. Încearcă din nou peste câteva minute.")

    utilizator = db.execute(
        select(Utilizator).where(Utilizator.email == date.email)
    ).scalar_one_or_none()
    if utilizator is None:
        raise HTTPException(status_code=404, detail="Nu există niciun cont cu acest email.")

    parola_noua = genereaza_parola_temporara()
    utilizator.parola_hash = cripteaza_parola(parola_noua)
    db.commit()
    return {
        "mesaj": "Am generat o parolă temporară. Autentifică-te cu ea, apoi schimb-o din contul tău.",
        "email": utilizator.email,
        "parola_temporara": parola_noua,
    }


@router.get("/eu")
def profil_propriu(user: Utilizator = Depends(utilizator_curent)):
    return {"id": user.id, "nume": user.nume, "email": user.email, "rol": user.rol}


@router.post("/schimba-parola")
def schimba_parola(date: SchimbareParola, user: Utilizator = Depends(utilizator_curent),
                   db: Session = Depends(get_db)):
    if not verifica_parola(date.parola_actuala, user.parola_hash):
        raise HTTPException(status_code=400, detail="Parola actuală nu este corectă.")
    user.parola_hash = cripteaza_parola(date.parola_noua)
    db.add(user)
    db.commit()
    return {"mesaj": "Parola a fost schimbată."}
