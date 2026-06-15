"""CodeSpace 3.0 — punctul de asamblare al aplicației FastAPI.

Pornire:  python main.py    (sau)    uvicorn main:app --reload
La prima pornire se creează schema bazei de date și conturile implicite;
conținutul cursului se încarcă separat, cu `python seed.py`.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.bootstrap import asigura_date_minime
from app.db import SesiuneLocala
from app.routers import (auth, curs, exercitii, gamificare, profesor,
                         progres, quiz, recapitulare, test_adaptiv, tutor)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asigura_date_minime()
    # Indexul RAG se construiește din lecții (gol și inofensiv înainte de seed)
    from app.ai import rag
    db = SesiuneLocala()
    try:
        rag.index.construieste(db)
    except Exception as e:  # nu bloca pornirea dacă indexarea eșuează
        print(f"[RAG] Index neconstruit la pornire: {e}")
    finally:
        db.close()
    yield


app = FastAPI(
    title="CodeSpace API",
    version="3.0",
    description="Sistem inteligent pentru învățarea programării — backend.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINI_PERMISE,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

for modul in (auth, curs, exercitii, quiz, recapitulare, test_adaptiv,
              tutor, progres, gamificare, profesor):
    app.include_router(modul.router)


@app.get("/")
def stare():
    return {"aplicatie": "CodeSpace", "versiune": "3.0", "status": "online",
            "ai_activ": config.AI_ACTIV}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
