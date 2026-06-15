"""RAG (Retrieval-Augmented Generation) peste conținutul lecțiilor.

Strategie:
- chunking conștient de Markdown: lecțiile se împart pe secțiuni (titluri `##`),
  deci fiecare fragment e o idee coerentă, nu o tăietură arbitrară;
- retrieval lexical BM25 (implicit: fără dependențe externe, fără cotă API);
- opțional retrieval semantic cu embeddings Google (RAG_EMBEDDINGS=1).

Validarea contextului regăsit:
1. prag minim de relevanță — fragmentele irelevante nu intră în prompt;
2. deduplicarea surselor pe lecție;
3. răspunsurile vin întotdeauna cu citările lecțiilor-sursă (slug → link în UI).
"""
import math
import re
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

PRAG_SCOR = 0.5
MAX_FRAGMENT = 1500

STOPWORDS = {
    "si", "sa", "se", "la", "de", "in", "un", "o", "cu", "pe", "ce", "este",
    "sunt", "care", "din", "ai", "el", "ea", "iti", "te", "tu", "eu", "noi",
    "the", "a", "an", "to", "of", "is", "are", "for", "ca", "sau", "nu", "da",
    "cum", "mai", "lui", "ei", "fie", "prin", "pentru", "asta", "acest",
    "aceasta", "cand", "unde", "dar", "ori", "fi", "am", "ar", "va", "vor",
}


def _tokenizeaza(text: str) -> list[str]:
    tokens = re.findall(r"[a-zăâîșț0-9_]+", (text or "").lower())
    return [t for t in tokens if len(t) > 1 and t not in STOPWORDS]


def imparte_markdown(continut: str) -> list[str]:
    """Împarte conținutul Markdown în fragmente pe secțiuni `##`."""
    if not continut or not continut.strip():
        return []
    bucati = re.split(r"(?m)^(?=##\s)", continut)
    fragmente = []
    for bucata in bucati:
        bucata = bucata.strip()
        if len(bucata) >= 40:
            fragmente.append(bucata[:MAX_FRAGMENT])
    return fragmente or [continut.strip()[:MAX_FRAGMENT]]


class IndexRAG:
    """Index de căutare peste fragmentele lecțiilor (BM25 + embeddings opțional)."""

    def __init__(self):
        self.fragmente: list[dict] = []
        self._tokenuri: list[list[str]] = []
        self._idf: dict[str, float] = {}
        self._avgdl = 1.0
        self._vectorstore = None

    # ── Construirea indexului din baza de date ──────────────────
    def construieste(self, db: Session) -> None:
        from app.models import Capitol, Lectie
        lectii = db.execute(
            select(Lectie).join(Capitol).order_by(Capitol.ordine, Lectie.ordine)
        ).scalars().all()

        self.fragmente = []
        for lectie in lectii:
            for bucata in imparte_markdown(lectie.continut_md):
                self.fragmente.append({
                    "text": bucata,
                    "lectie_id": lectie.id,
                    "lectie_slug": lectie.slug,
                    "lectie_titlu": lectie.titlu,
                    "capitol_titlu": lectie.capitol.titlu,
                })

        self._construieste_bm25()
        self._incearca_embeddings()
        print(f"[RAG] Index construit: {len(self.fragmente)} fragmente din {len(lectii)} lecții.")

    def _construieste_bm25(self) -> None:
        self._tokenuri = [
            _tokenizeaza(f["text"] + " " + f["lectie_titlu"]) for f in self.fragmente
        ]
        n = len(self._tokenuri)
        if n == 0:
            self._idf, self._avgdl = {}, 1.0
            return
        df = Counter()
        for tokens in self._tokenuri:
            for t in set(tokens):
                df[t] += 1
        self._idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}
        self._avgdl = sum(len(t) for t in self._tokenuri) / n or 1.0

    def _incearca_embeddings(self) -> None:
        from app.ai.llm import construieste_embeddings
        embeddings = construieste_embeddings()
        if embeddings is None:
            self._vectorstore = None
            return
        try:
            from langchain_core.documents import Document
            from langchain_core.vectorstores import InMemoryVectorStore
            documente = [Document(page_content=f["text"], metadata={"idx": i})
                         for i, f in enumerate(self.fragmente)]
            self._vectorstore = InMemoryVectorStore.from_documents(documente, embeddings)
            print("[RAG] Index semantic (embeddings) activ.")
        except Exception as e:  # pragma: no cover
            print(f"[RAG] Indexul semantic a eșuat, rămân pe BM25: {e}")
            self._vectorstore = None

    # ── Căutare ─────────────────────────────────────────────────
    def cauta(self, interogare: str, k: int = 4) -> list[dict]:
        if not self.fragmente:
            return []
        if self._vectorstore is not None:
            return self._cauta_semantic(interogare, k)
        return self._cauta_bm25(interogare, k)

    def _cauta_bm25(self, interogare: str, k: int) -> list[dict]:
        q = _tokenizeaza(interogare)
        if not q:
            return []
        k1, b = 1.5, 0.75
        scoruri = []
        for i, tokens in enumerate(self._tokenuri):
            if not tokens:
                continue
            freq = Counter(tokens)
            dl = len(tokens)
            s = 0.0
            for t in q:
                if t not in freq:
                    continue
                idf = self._idf.get(t, 0.0)
                s += idf * (freq[t] * (k1 + 1)) / (freq[t] + k1 * (1 - b + b * dl / self._avgdl))
            if s > 0:
                scoruri.append((s, i))
        scoruri.sort(reverse=True)
        return [dict(self.fragmente[i], scor=round(s, 3))
                for s, i in scoruri[:k] if s >= PRAG_SCOR]

    def _cauta_semantic(self, interogare: str, k: int) -> list[dict]:
        try:
            gasite = self._vectorstore.similarity_search(interogare, k=k)
            return [dict(self.fragmente[d.metadata["idx"]], scor=None) for d in gasite]
        except Exception:
            return self._cauta_bm25(interogare, k)

    def context_si_surse(self, interogare: str, k: int = 4) -> tuple[str, list[dict]]:
        """(context pentru prompt, surse deduplicate pe lecție — pentru citare)."""
        gasite = self.cauta(interogare, k)
        context = "\n\n---\n\n".join(
            f"[{g['capitol_titlu']} › {g['lectie_titlu']}]\n{g['text']}" for g in gasite
        )
        surse, vazute = [], set()
        for g in gasite:
            if g["lectie_id"] not in vazute:
                vazute.add(g["lectie_id"])
                surse.append({
                    "lectie_id": g["lectie_id"],
                    "lectie_slug": g["lectie_slug"],
                    "lectie": g["lectie_titlu"],
                    "capitol": g["capitol_titlu"],
                })
        return context, surse


# Indexul global, construit la pornirea aplicației și după editarea conținutului
index = IndexRAG()
