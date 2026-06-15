"""Securitate: parole (bcrypt), token-uri JWT și limitare de debit."""
import string
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from random import SystemRandom

import bcrypt
from jose import JWTError, jwt

from app import config

# SystemRandom folosește os.urandom — sursă criptografică, potrivită pentru parole
# (spre deosebire de `random` obișnuit, previzibil).
_rng = SystemRandom()


# ── Parole ──────────────────────────────────────────────────────
def cripteaza_parola(parola: str) -> str:
    return bcrypt.hashpw(parola.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verifica_parola(parola: str, parola_hash: str) -> bool:
    try:
        return bcrypt.checkpw(parola.encode("utf-8"), parola_hash.encode("utf-8"))
    except ValueError:
        return False


def genereaza_parola_temporara() -> str:
    """Parolă temporară puternică (10 caractere) care respectă regula de validare
    a aplicației: garantat literă mare, literă mică, cifră și caracter special."""
    caractere = [
        _rng.choice(string.ascii_uppercase),
        _rng.choice(string.ascii_lowercase),
        _rng.choice(string.digits),
        _rng.choice("@$!%*?&"),
    ]
    caractere += [_rng.choice(string.ascii_letters + string.digits) for _ in range(6)]
    _rng.shuffle(caractere)
    return "".join(caractere)


# ── JWT ─────────────────────────────────────────────────────────
def creeaza_token(email: str, rol: str) -> str:
    payload = {
        "sub": email,
        "rol": rol,
        "exp": datetime.now(timezone.utc) + timedelta(hours=config.TOKEN_EXPIRE_ORE),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm=config.ALGORITHM)


def decodeaza_token(token: str) -> dict | None:
    """Returnează payload-ul tokenului sau None dacă e invalid/expirat."""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if not payload.get("sub"):
            return None
        return payload
    except JWTError:
        return None


# ── Limitare de debit (în memorie, per utilizator) ──────────────
class LimitatorDebit:
    """Fereastră glisantă simplă: maxim `limita` apeluri în `fereastra_s` secunde.

    Protejează endpoint-urile care consumă cota API-ului AI de apeluri în rafală.
    """

    def __init__(self, limita: int, fereastra_s: int = 60):
        self.limita = limita
        self.fereastra_s = fereastra_s
        self._apeluri: dict[int, deque] = defaultdict(deque)

    def permite(self, user_id: int) -> bool:
        acum = time.monotonic()
        coada = self._apeluri[user_id]
        while coada and acum - coada[0] > self.fereastra_s:
            coada.popleft()
        if len(coada) >= self.limita:
            return False
        coada.append(acum)
        return True


limitator_ai = LimitatorDebit(config.LIMITA_AI_PE_MINUT)
# Resetarea parolei: maxim 5 cereri în 10 minute de la aceeași adresă IP,
# ca să nu poată cineva reseta parole în rafală (protecție anti-abuz).
limitator_reset = LimitatorDebit(limita=5, fereastra_s=600)
