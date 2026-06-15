"""Tutorele AI: chat cu streaming (SSE), ancorat în lecții, cu istoric persistent.

Formatul fluxului SSE:
  event: surse   + data: [lista lecțiilor citate]   (o singură dată, la început)
  data: {"text": "fragment de răspuns"}             (de mai multe ori)
  data: [DONE]                                      (la final)
"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.ai import tutor
from app.ai.llm import obtine_llm, text_din_continut
from app.db import SesiuneLocala
from app.deps import cu_limita_ai, get_db, utilizator_curent
from app.engine import gamification
from app.models import MesajChat, Utilizator
from app.schemas import IntrebareChat

router = APIRouter(prefix="/tutor", tags=["tutore AI"])


@router.get("/istoric")
def istoric(user: Utilizator = Depends(utilizator_curent), db: Session = Depends(get_db)):
    mesaje = db.execute(
        select(MesajChat).where(MesajChat.user_id == user.id)
        .order_by(MesajChat.id.desc()).limit(50)
    ).scalars().all()
    mesaje.reverse()
    return [{"rol": m.rol, "continut": m.continut, "surse": m.surse_json,
             "creat_la": m.creat_la} for m in mesaje]


@router.delete("/istoric")
def sterge_istoric(user: Utilizator = Depends(utilizator_curent),
                   db: Session = Depends(get_db)):
    db.execute(delete(MesajChat).where(MesajChat.user_id == user.id))
    db.commit()
    return {"mesaj": "Conversația a fost ștearsă."}


def _sse(date: dict | str) -> str:
    if isinstance(date, str):
        return f"data: {date}\n\n"
    return f"data: {json.dumps(date, ensure_ascii=False, default=str)}\n\n"


@router.post("/intreaba")
def intreaba(date: IntrebareChat, user: Utilizator = Depends(cu_limita_ai),
             db: Session = Depends(get_db)):
    # Mesajul studentului se salvează imediat (intră în istoric chiar dacă AI-ul pică)
    db.add(MesajChat(user_id=user.id, rol="user", continut=date.intrebare))
    gamification.inregistreaza_activitate(db, user.id)
    db.commit()

    prompt, surse = tutor.pregateste_chat(db, user.id, date.intrebare, date.lectie_slug)
    user_id = user.id

    async def flux():
        yield f"event: surse\n{_sse(surse)}"
        complet = []
        llm = obtine_llm()
        if llm is None:
            text = ("Tutorele AI nu este disponibil momentan (lipsește cheia API). "
                    "Am căutat totuși în curs — lecțiile citate mai jos acoperă subiectul tău. "
                    "Deschide-le din lista de surse.")
            if not surse:
                text = ("Tutorele AI nu este disponibil momentan și nu am găsit lecții "
                        "relevante pentru întrebarea ta. Încearcă o reformulare.")
            complet.append(text)
            yield _sse({"text": text})
        else:
            try:
                async for fragment in llm.astream(prompt):
                    text = text_din_continut(getattr(fragment, "content", ""))
                    if text:
                        complet.append(text)
                        yield _sse({"text": text})
            except Exception as e:
                # Mesaj prietenos, fără payload-ul brut al API-ului
                text_eroare = str(e)
                if "503" in text_eroare or "UNAVAILABLE" in text_eroare:
                    mesaj_eroare = ("\n\n*(Modelul AI este momentan supraîncărcat — "
                                    "încearcă din nou în câteva secunde. Între timp, "
                                    "lecțiile citate mai jos acoperă subiectul.)*")
                elif "429" in text_eroare:
                    mesaj_eroare = ("\n\n*(Cota API a fost atinsă pentru moment — "
                                    "așteaptă un minut și încearcă din nou.)*")
                else:
                    mesaj_eroare = "\n\n*(Răspunsul s-a întrerupt — încearcă din nou.)*"
                complet.append(mesaj_eroare)
                yield _sse({"text": mesaj_eroare})

        # Salvăm răspunsul asistentului într-o sesiune proprie, după streaming
        sesiune = SesiuneLocala()
        try:
            sesiune.add(MesajChat(user_id=user_id, rol="asistent",
                                  continut="".join(complet), surse_json=surse))
            sesiune.commit()
        finally:
            sesiune.close()
        yield _sse("[DONE]")

    return StreamingResponse(flux(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})
