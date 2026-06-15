"""Inițializarea modelului Gemini (LangChain), cu degradare grațioasă.

Aplicația NU depinde critic de API-ul AI: fără cheie, tutorele anunță
indisponibilitatea, indiciile cad pe varianta bazată pe reguli, iar testul
adaptiv se construiește din banca de întrebări. Orice apel trece prin
`obtine_llm()`, care întoarce None când AI-ul nu e disponibil.
"""
from app import config

_llm = None
_llm_incercat = False


def obtine_llm():
    """Clientul Gemini (creat leneș, o singură dată) sau None dacă nu există cheie."""
    global _llm, _llm_incercat
    if _llm_incercat:
        return _llm
    _llm_incercat = True
    if not config.GOOGLE_API_KEY:
        print("[AI] GOOGLE_API_KEY lipsește — funcțiile AI rulează în regim degradat.")
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # timeout + max_retries mici: dacă API-ul e lent sau fără cotă, aplicația
        # cade RAPID pe variantele fără AI (indicii pe reguli, banca de întrebări),
        # în loc să blocheze cererea minute întregi cu retry-uri.
        _llm = ChatGoogleGenerativeAI(
            model=config.MODEL_LLM,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.6,
            timeout=25,
            max_retries=1,
        )
    except Exception as e:  # pragma: no cover - depinde de mediu
        print(f"[AI] Modelul nu a putut fi inițializat: {e}")
        _llm = None
    return _llm


def text_din_continut(continut) -> str:
    """Extrage textul dintr-un răspuns LangChain.

    Modelele Gemini recente pot întoarce conținutul ca LISTĂ de blocuri
    ({'type': 'text', 'text': ...}), nu ca șir simplu — normalizăm aici.
    """
    if isinstance(continut, str):
        return continut
    if isinstance(continut, list):
        parti = []
        for bloc in continut:
            if isinstance(bloc, str):
                parti.append(bloc)
            elif isinstance(bloc, dict) and bloc.get("type") == "text":
                parti.append(bloc.get("text", ""))
        return "".join(parti)
    return str(continut or "")


def construieste_embeddings():
    """Modelul de embeddings Google (sau None — RAG-ul cade pe BM25)."""
    if not config.RAG_EMBEDDINGS or not config.GOOGLE_API_KEY:
        return None
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model=config.MODEL_EMBEDDINGS,
            google_api_key=config.GOOGLE_API_KEY,
        )
    except Exception as e:  # pragma: no cover
        print(f"[RAG] Embeddings indisponibile, rămân pe BM25: {e}")
        return None
