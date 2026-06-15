"""Setările globale ale aplicației CodeSpace 3.0.

Toate valorile configurabile (chei, modele AI, parametri pedagogici) stau aici,
ca să poată fi justificate și ajustate dintr-un singur loc.
"""
import os
import sys

from dotenv import load_dotenv

# Consola Windows folosește implicit cp1252; forțăm UTF-8 ca mesajele de log
# cu diacritice să nu oprească aplicația (errors="replace" e plasa de siguranță).
for flux in (sys.stdout, sys.stderr):
    if flux is not None and hasattr(flux, "reconfigure"):
        try:
            flux.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

# Încarcă .env din rădăcina proiectului (un nivel peste /backend)
RADACINA_PROIECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(RADACINA_PROIECT, ".env"))

# ── AI (Google Gemini prin LangChain) ───────────────────────────
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL_LLM = os.environ.get("MODEL_LLM", "gemini-flash-latest")
MODEL_EMBEDDINGS = os.environ.get("MODEL_EMBEDDINGS", "models/text-embedding-004")
# RAG semantic cu embeddings (necesită cotă API); implicit retrieval lexical BM25
RAG_EMBEDDINGS = os.environ.get("RAG_EMBEDDINGS", "0") == "1"
# Aplicația funcționează și fără cheie API (degradare grațioasă: indicii pe reguli,
# teste adaptive din banca de întrebări, tutorele anunță indisponibilitatea).
AI_ACTIV = bool(GOOGLE_API_KEY)

# ── Securitate ──────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = "codespace_cheie_dezvoltare_NU_folosi_in_productie"
    print("[CONFIG] Avertisment: SECRET_KEY lipsește din .env — folosesc cheia de dezvoltare.")
ALGORITHM = "HS256"
TOKEN_EXPIRE_ORE = int(os.environ.get("TOKEN_EXPIRE_ORE", "24"))
# Originile permise pentru CORS (frontend-ul Vite)
ORIGINI_PERMISE = os.environ.get("ORIGINI_PERMISE", "http://localhost:5173,http://127.0.0.1:5173").split(",")

# Limitare de debit pentru endpoint-urile care consumă API-ul AI
LIMITA_AI_PE_MINUT = int(os.environ.get("LIMITA_AI_PE_MINUT", "10"))

# ── Baza de date ────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codespace.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ── Conturi implicite (create la prima pornire) ─────────────────
PROFESOR_EMAIL = "profesor@codespace.ro"
PROFESOR_PAROLA = "Profesor123!"
PROFESOR_NUME = "Profesor CodeSpace"
STUDENT_DEMO_EMAIL = "student@codespace.ro"
STUDENT_DEMO_PAROLA = "Student123!"
STUDENT_DEMO_NUME = "Student Demo"

# ── Reguli de validare text ─────────────────────────────────────
MIN_LUNGIME_NUME = 2
MAX_LUNGIME_NUME = 60
MAX_LUNGIME_INTREBARE = 1200
MAX_LUNGIME_COD = 20_000
PAROLA_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&.\-_])[A-Za-z\d@$!%*?&.\-_]{8,}$"
EMAIL_REGEX = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"

# ── Modelul studentului: Bayesian Knowledge Tracing ─────────────
# Parametri standard din literatură (Corbett & Anderson, 1995).
BKT_P_INIT = 0.20        # p(L0): probabilitatea a priori de a cunoaște conceptul
BKT_P_TRANSFER = 0.15    # p(T): șansa de a învăța conceptul după o interacțiune
BKT_P_ALUNECARE = 0.10   # p(S): "slip" — răspuns greșit deși conceptul e știut
# p(G): "guess" — răspuns corect prin ghicire; depinde de tipul activității
BKT_P_GHICIRE = {
    "quiz": 0.25,        # grilă cu 4 variante → ~25% șansă de ghicire
    "exercitiu": 0.05,   # cod care trece testele e greu de "ghicit"
    "recapitulare": 0.25,
    "test_adaptiv": 0.25,
}
PRAG_STAPANIRE = 0.95    # un concept e considerat stăpânit la p ≥ 0.95
PRAG_FUNDAMENT = 0.55    # prerechizitele unei lecții sunt "gata" la p ≥ 0.55
PRAG_CONCEPT_SLAB = 0.60 # sub acest prag, conceptul intră în recomandările de exersare

# ── Repetiție spațiată (SM-2) ───────────────────────────────────
SM2_FACTOR_INITIAL = 2.5
SM2_FACTOR_MINIM = 1.3
RECAPITULARI_PE_SESIUNE = 12

# ── Gamificare: XP-ul se câștigă DOAR din rezultate ─────────────
XP_EXERCITIU = 50            # exercițiu acceptat (prima dată)
XP_PENALIZARE_INDICIU = 10   # se scade pentru fiecare nivel de indiciu folosit
XP_EXERCITIU_MINIM = 15      # XP-ul minim al unui exercițiu, oricâte indicii
XP_INTREBARE_QUIZ = 10       # per răspuns corect, la prima tentativă a capitolului
XP_RECAPITULARE = 10         # per întrebare recapitulată corect
XP_INTREBARE_TEST = 15       # per răspuns corect la testul adaptiv

# ── Sandbox-ul de execuție a codului pe server ──────────────────
SANDBOX_TIMEOUT_S = 5
SANDBOX_MAX_OUTPUT = 10_000
# Module pe care studenții le pot importa în soluții
MODULE_PERMISE = {
    "math", "random", "string", "functools", "itertools", "collections",
    "json", "re", "datetime", "typing", "statistics", "fractions", "decimal",
}

# ── Tutorele AI ─────────────────────────────────────────────────
ISTORIC_CHAT_CONTEXT = 8     # câte mesaje recente intră în contextul tutorelui
MAX_NIVEL_INDICIU = 3
TEST_ADAPTIV_INTREBARI = 6   # întrebări per test adaptiv
TEST_ADAPTIV_CONCEPTE = 3    # câte concepte slabe vizează un test
