"""Dependențe FastAPI: sesiunea de bază de date și utilizatorul autentificat."""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SesiuneLocala
from app.models import Utilizator
from app.security import decodeaza_token, limitator_ai

security = HTTPBearer()


def get_db():
    db = SesiuneLocala()
    try:
        yield db
    finally:
        db.close()


def utilizator_curent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Utilizator:
    """Decodează tokenul și încarcă utilizatorul din baza de date.

    Încărcarea din DB (nu doar din token) garantează că un cont șters sau
    cu rol schimbat își pierde imediat accesul.
    """
    payload = decodeaza_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token expirat sau invalid.")
    user = db.execute(
        select(Utilizator).where(Utilizator.email == payload["sub"])
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilizator inexistent.")
    return user


def profesor_curent(user: Utilizator = Depends(utilizator_curent)) -> Utilizator:
    if user.rol != "profesor":
        raise HTTPException(status_code=403, detail="Acces permis doar profesorului.")
    return user


def cu_limita_ai(user: Utilizator = Depends(utilizator_curent)) -> Utilizator:
    """Aplică limitarea de debit pe endpoint-urile care consumă API-ul AI."""
    if not limitator_ai.permite(user.id):
        raise HTTPException(status_code=429,
                            detail="Prea multe cereri către AI. Așteaptă un minut și încearcă din nou.")
    return user
