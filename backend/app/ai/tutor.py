"""Tutorele socratic: chat ancorat în lecții, indicii progresive și test adaptiv.

Principii:
- Chatul e ancorat RAG în conținutul cursului și citează lecțiile-sursă.
- Tutorele cunoaște modelul studentului (conceptele slabe) și se adaptează.
- La exercițiile notate NU dă soluții: indicii pe 3 niveluri, tot mai concrete.
- Fără cheie API totul degradează grațios: indicii pe reguli (din taxonomia
  erorilor), test adaptiv din banca de întrebări.
"""
import json
import random
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import config
from app.ai import rag
from app.ai.llm import obtine_llm, text_din_continut
from app.engine import bkt, errors
from app.models import (Concept, Exercitiu, Intrebare, Lectie, MesajChat,
                        StareConcept)

# ── Profilul studentului pentru prompt ──────────────────────────
def profil_student(db: Session, user_id: int) -> str:
    stari = db.execute(
        select(StareConcept).where(StareConcept.user_id == user_id,
                                   StareConcept.nr_observatii > 0)
        .order_by(StareConcept.p_cunoastere)
    ).scalars().all()
    if not stari:
        return "Student la început de drum, fără istoric încă."
    slabe = [s for s in stari if s.p_cunoastere < config.PRAG_CONCEPT_SLAB][:3]
    bune = [s for s in stari if s.p_cunoastere >= config.PRAG_STAPANIRE][:3]
    parti = []
    if slabe:
        parti.append("concepte slabe: " +
                     ", ".join(f"{s.concept.nume} ({round(s.p_cunoastere * 100)}%)" for s in slabe))
    if bune:
        parti.append("concepte stăpânite: " + ", ".join(s.concept.nume for s in bune))
    return "; ".join(parti) or "Progres mediu, fără concepte critice."


def istoric_recent(db: Session, user_id: int, limita: int = config.ISTORIC_CHAT_CONTEXT) -> str:
    mesaje = db.execute(
        select(MesajChat).where(MesajChat.user_id == user_id)
        .order_by(MesajChat.id.desc()).limit(limita)
    ).scalars().all()
    mesaje.reverse()
    return "\n".join(
        f"{'Student' if m.rol == 'user' else 'Tutore'}: {m.continut[:400]}" for m in mesaje
    ) or "(conversație nouă)"


PROMPT_CHAT = """Ești tutorele AI al platformei CodeSpace — un profesor de Python socratic, prietenos și concis. Răspunzi în limba română.

REGULI:
1. Folosește ÎN PRIMUL RÂND informațiile din CONTEXT (lecțiile cursului). Dacă subiectul nu e acoperit de context, spune sincer acest lucru și oferă o explicație scurtă și corectă de bază.
2. Ghidează studentul să gândească singur: pune o întrebare de verificare la final, sugerează pași mici. Nu rezolva în locul lui exercițiile platformei.
3. Răspuns compact: maxim 8 propoziții. Exemple de cod scurte (sub 6 linii), doar dacă ajută.
4. Ține cont de profilul studentului — dacă întrebarea atinge un concept slab al lui, explică mai răbdător.

PROFIL STUDENT: {profil}

CONTEXT (din lecții):
{context}

CONVERSAȚIA RECENTĂ:
{istoric}

ÎNTREBAREA STUDENTULUI: {intrebare}"""


def pregateste_chat(db: Session, user_id: int, intrebare: str,
                    lectie_slug: str | None) -> tuple[str, list[dict]]:
    """Construiește promptul complet și sursele citate (înainte de streaming)."""
    titlu_lectie = ""
    if lectie_slug:
        lectie = db.execute(select(Lectie).where(Lectie.slug == lectie_slug)).scalar_one_or_none()
        if lectie:
            titlu_lectie = lectie.titlu
    context, surse = rag.index.context_si_surse(f"{titlu_lectie} {intrebare}".strip(), k=4)
    prompt = PROMPT_CHAT.format(
        profil=profil_student(db, user_id),
        context=context or "(nu există context relevant în lecții)",
        istoric=istoric_recent(db, user_id),
        intrebare=intrebare,
    )
    return prompt, surse


# ── Indicii progresive la exerciții ─────────────────────────────
INSTRUCTIUNI_NIVEL = {
    1: "NIVEL 1 — orientare: indică doar conceptul sau ideea pe care studentul "
       "trebuie să o revadă. Nu pomeni linii de cod, nu da pași concreți. Maxim 3 propoziții.",
    2: "NIVEL 2 — localizare: arată CE anume e greșit (zona din cod, condiția, "
       "cazul-limită ratat) și de ce, conceptual. NU scrie codul corect. Maxim 4 propoziții.",
    3: "NIVEL 3 — aproape de soluție: descrie pașii algoritmici exacți (pseudocod "
       "pe puncte), dar NU scrie cod Python funcțional. Maxim 6 puncte scurte.",
}

PROMPT_INDICIU = """Ești tutorele platformei CodeSpace. Un student lucrează la un exercițiu notat și a cerut un indiciu. NU ai voie să scrii soluția sau cod Python complet — doar îndrumare, conform nivelului cerut.

{instructiuni_nivel}

EXERCIȚIUL: {titlu}
{enunt}

CODUL STUDENTULUI:
```python
{cod}
```

REZULTATUL EVALUĂRII: {rezultat}

Scrie indiciul în română, direct, fără introduceri."""


def _descrie_rezultat(rezultat) -> str:
    """Rezumat textual al rezultatului rulării, pentru promptul indiciului."""
    if rezultat is None:
        return "Studentul nu a rulat încă testele."
    if rezultat.status == "acceptat":
        return "Toate testele trec."
    parti = [f"{rezultat.teste_trecute}/{rezultat.teste_total} teste trec."]
    if rezultat.eroare_mesaj:
        parti.append(f"Eroare: {rezultat.eroare_mesaj}")
    for r in rezultat.rezultate or []:
        if not r.get("trecut"):
            parti.append(f"Primul test picat: {r.get('descriere')} → obținut {r.get('obtinut')}, "
                         f"așteptat {r.get('asteptat')}.")
            break
    return " ".join(parti)


def genereaza_indiciu(db: Session, exercitiu: Exercitiu, cod: str,
                      rezultat, nivel: int) -> str:
    llm = obtine_llm()
    if llm is not None:
        prompt = PROMPT_INDICIU.format(
            instructiuni_nivel=INSTRUCTIUNI_NIVEL[nivel],
            titlu=exercitiu.titlu,
            enunt=exercitiu.enunt_md[:1500],
            cod=(cod or "(gol)")[:3000],
            rezultat=_descrie_rezultat(rezultat),
        )
        try:
            raspuns = text_din_continut(llm.invoke(prompt).content).strip()
            if raspuns:
                return raspuns
        except Exception as e:
            print(f"[AI] Indiciu LLM eșuat, folosesc varianta pe reguli: {e}")
    return _indiciu_pe_reguli(exercitiu, rezultat, nivel)


def _indiciu_pe_reguli(exercitiu: Exercitiu, rezultat, nivel: int) -> str:
    """Indiciu determinist din taxonomia erorilor — funcționează fără AI."""
    if rezultat is None or not rezultat.eroare_categorie:
        baza = "Recitește cerința pas cu pas și verifică ce ar trebui să returneze funcția pentru fiecare exemplu din teste."
        if nivel == 1:
            return baza
        teste = exercitiu.teste
        exemplu = teste[0] if teste else None
        detaliu = (f" Începe cu primul test: {exemplu.apel or exemplu.stdin!r} trebuie să dea {exemplu.asteptat}."
                   if exemplu else "")
        return baza + detaliu

    descriere = errors.descrie(rezultat.eroare_categorie)
    if nivel == 1:
        return f"{descriere['titlu']}: {descriere['explicatie']}"
    parti = [f"{descriere['titlu']}: {descriere['explicatie']}", descriere["sfat"]]
    if nivel >= 2 and rezultat.eroare_mesaj:
        parti.append(f"Detaliu tehnic: {rezultat.eroare_mesaj}")
    if nivel >= 3:
        picat = next((r for r in (rezultat.rezultate or []) if not r.get("trecut")), None)
        if picat:
            parti.append(f"Urmărește pe hârtie ce se întâmplă la {picat.get('descriere')}: "
                         f"codul tău produce {picat.get('obtinut')}, dar rezultatul corect e "
                         f"{picat.get('asteptat')}. Unde diverge calculul?")
        parti.append(f"Lecția asociată („{exercitiu.lectie.titlu}”) conține un exemplu foarte apropiat.")
    return "\n\n".join(parti)


# ── Testul adaptiv ──────────────────────────────────────────────
PROMPT_TEST = """Ești profesor de Python pe platforma CodeSpace. Generează {numar} întrebări grilă în ROMÂNĂ pentru conceptul „{concept}”, dificultate medie, pe baza materialului de curs de mai jos.

MATERIAL:
{context}

Răspunde STRICT cu un JSON valid (fără text în plus, fără markdown), o listă de obiecte:
[{{"text": "Întrebarea?", "corecta": "Răspunsul corect", "gresite": ["Greșit 1", "Greșit 2", "Greșit 3"], "explicatie": "De ce e corect răspunsul, într-o propoziție."}}]

Reguli: întrebări practice (ce afișează codul / ce valoare rezultă), variante plauzibile dar clar greșite, o singură variantă corectă."""


def _extrage_json(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    inceput, sfarsit = text.find("["), text.rfind("]")
    if inceput != -1 and sfarsit != -1:
        text = text[inceput:sfarsit + 1]
    return text


def valideaza_intrebari_generate(brut: str) -> list[dict]:
    """Validarea structurală a ieșirii LLM: doar elementele complete trec."""
    date = json.loads(_extrage_json(brut))
    if not isinstance(date, list):
        raise ValueError("Răspunsul AI nu este o listă.")
    valide = []
    for element in date:
        if not isinstance(element, dict):
            continue
        text = str(element.get("text", "")).strip()
        corecta = str(element.get("corecta", "")).strip()
        gresite = [str(g).strip() for g in element.get("gresite", []) if str(g).strip()]
        explicatie = str(element.get("explicatie", "")).strip()
        if text and corecta and len(gresite) >= 3 and corecta not in gresite:
            valide.append({"text": text, "corecta": corecta,
                           "gresite": gresite[:3], "explicatie": explicatie})
    return valide


def alege_concepte_slabe(db: Session, user_id: int,
                         numar: int = config.TEST_ADAPTIV_CONCEPTE) -> list[Concept]:
    stari = db.execute(
        select(StareConcept).where(StareConcept.user_id == user_id,
                                   StareConcept.nr_observatii > 0)
        .order_by(StareConcept.p_cunoastere)
    ).scalars().all()
    concepte = [s.concept for s in stari[:numar]]
    if not concepte:
        # Student nou: primele concepte din curs
        concepte = db.execute(
            select(Concept).order_by(Concept.ordine).limit(numar)
        ).scalars().all()
    return concepte


def _intrebari_din_banca(db: Session, concepte: list[Concept], numar: int) -> list[dict]:
    """Fallback fără AI: întrebări din banca de întrebări, pe conceptele slabe."""
    ids = [c.id for c in concepte]
    candidate = db.execute(
        select(Intrebare).join(Intrebare.concepte)
        .where(Concept.id.in_(ids), Intrebare.activa)
        .distinct()
    ).scalars().all()
    random.shuffle(candidate)
    rezultat = []
    for intrebare in candidate[:numar]:
        slug = next((c.slug for c in intrebare.concepte if c.id in ids), "")
        rezultat.append({
            "text": intrebare.text,
            "corecta": intrebare.varianta_corecta,
            "gresite": list(intrebare.gresite_json),
            "explicatie": intrebare.explicatie,
            "concept_slug": slug,
            "sursa": "banca",
        })
    return rezultat


def intrebari_plasament(db: Session, maxim: int = 10) -> tuple[list[dict], list[str]]:
    """Întrebările testului de PLASAMENT: câte una pe concept, răspândite
    uniform pe toată întinderea cursului — calibrarea inițială a modelului BKT.

    Rezolvă problema de "cold start": fără date, sistemul nu știe de unde să
    înceapă cu un student care nu e începător. Zece răspunsuri pe concepte
    distribuite spun mai mult decât zece pe același capitol.
    """
    concepte = db.execute(select(Concept).order_by(Concept.ordine)).scalars().all()
    folosite: set[int] = set()
    candidate: list[tuple[Concept, Intrebare]] = []
    for concept in concepte:
        intrebare = db.execute(
            select(Intrebare).join(Intrebare.concepte)
            .where(Concept.id == concept.id, Intrebare.activa,
                   Intrebare.id.notin_(folosite or {0}))
            .order_by(Intrebare.dificultate, Intrebare.id)
            .limit(1)
        ).scalars().first()
        if intrebare is not None:
            candidate.append((concept, intrebare))
            folosite.add(intrebare.id)

    # Răspândire uniformă dacă există mai multe candidate decât locuri
    if len(candidate) > maxim:
        pas = len(candidate) / maxim
        candidate = [candidate[int(i * pas)] for i in range(maxim)]

    intrebari = [{
        "text": intrebare.text,
        "corecta": intrebare.varianta_corecta,
        "gresite": list(intrebare.gresite_json),
        "explicatie": intrebare.explicatie,
        "concept_slug": concept.slug,
        "sursa": "banca",
    } for concept, intrebare in candidate]
    return intrebari, [concept.slug for concept, _ in candidate]


def genereaza_intrebari_adaptive(db: Session, user_id: int) -> tuple[list[dict], list[str]]:
    """Întrebările testului adaptiv + conceptele vizate.

    Încearcă generarea LLM pe conceptele slabe; completează din banca de
    întrebări dacă AI-ul lipsește sau produce prea puține elemente valide.
    """
    concepte = alege_concepte_slabe(db, user_id)
    tinta = config.TEST_ADAPTIV_INTREBARI
    per_concept = max(1, round(tinta / max(len(concepte), 1)))
    intrebari: list[dict] = []

    llm = obtine_llm()
    if llm is not None:
        for concept in concepte:
            context, _ = rag.index.context_si_surse(concept.nume, k=3)
            prompt = PROMPT_TEST.format(numar=per_concept, concept=concept.nume,
                                        context=context or concept.descriere or concept.nume)
            try:
                brut = text_din_continut(llm.invoke(prompt).content)
                for intrebare in valideaza_intrebari_generate(brut)[:per_concept]:
                    intrebare["concept_slug"] = concept.slug
                    intrebare["sursa"] = "ai"
                    intrebari.append(intrebare)
            except Exception as e:
                print(f"[AI] Generarea pentru „{concept.nume}” a eșuat: {e}")

    if len(intrebari) < tinta:
        existente = {i["text"] for i in intrebari}
        for intrebare in _intrebari_din_banca(db, concepte, tinta - len(intrebari) + 4):
            if intrebare["text"] not in existente and len(intrebari) < tinta:
                intrebari.append(intrebare)

    random.shuffle(intrebari)
    return intrebari[:tinta], [c.slug for c in concepte]
