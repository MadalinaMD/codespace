# CodeSpace 3.0 — Sistem inteligent pentru învățarea programării

Platformă web de tip *Intelligent Tutoring System* (ITS) pentru învățarea
limbajului Python: cursul se adaptează la fiecare student printr-un model
de cunoștințe (Bayesian Knowledge Tracing), recomandă explicabil următorul
pas, evaluează automat codul în sandbox, programează recapitulările cu
algoritmul SM-2 și oferă un tutore AI socratic ancorat în conținutul
cursului (RAG, cu citări).

## Arhitectura — cele patru componente clasice ale unui ITS

| Componentă | Implementare |
|------------|--------------|
| Modelul de domeniu | graf de 35 de concepte Python cu relații de prerechizit; tot conținutul (lecții, exerciții, întrebări) e etichetat pe concepte |
| Modelul studentului | Bayesian Knowledge Tracing per concept (Corbett & Anderson, 1995), actualizat la fiecare răspuns; p(ghicire) diferă pe tip de activitate |
| Modelul pedagogic | recomandator explicabil („de ce acum”), repetiție spațiată SM-2, tutore socratic cu indicii pe 3 niveluri (nu dă soluții), teste adaptive pe conceptele slabe, test de PLASAMENT pentru calibrarea inițială (rezolvă cold start-ul: pondere dublă + propagarea dovezii către prerechizite) |
| Interfața | SPA Vue 3 cu pagini dedicate: hartă de curs, lecții Markdown, editor cu teste instant, harta măiestriei (graful colorat după BKT), VIZUALIZATOR de execuție pas-cu-pas |

### Evaluarea codului — apărare pe straturi

1. **În browser (Pyodide/WebAssembly):** feedback instant, gratuit — browserul
   este sandbox-ul; testele rulează local la „Testează local”.
2. **Pe server (verdictul oficial):** analiză statică AST (listă de module
   permise, fără funcții de sistem) + execuție în proces izolat `python -I`
   cu timeout și ieșire limitată. Scorul și XP-ul se decid EXCLUSIV pe server;
   răspunsurile corecte nu pleacă niciodată spre client înainte de răspuns.

Erorile sunt clasificate într-o taxonomie (14 categorii) care alimentează
feedback-ul imediat, statistica „greșelile tale frecvente” și analiza
misconcepțiilor din panoul profesorului.

### Vizualizatorul de execuție pas-cu-pas

Orice exemplu din lecții, cod din playground sau exercițiu poate fi „filmat”:
`sys.settrace` (rulat tot în Pyodide, în browser) înregistrează fiecare linie
executată — variabilele locale și globale în acel moment, adâncimea apelurilor
(vizibilă la recursivitate), valorile de retur și output-ul progresiv.
Studentul derulează execuția înainte/înapoi ca pe un film (inspirat de
Python Tutor — Philip Guo). La exerciții, butonul „Depanează” trasează
execuția pe primul test picat.

### Soluția de referință — după rezolvare

Odată ce exercițiul e acceptat, serverul dezvăluie soluția profesorului,
pentru comparație — niciodată înainte.

### Panoul profesorului

Heatmap de măiestrie pe concepte, detectarea studenților la risc (reguli
explicabile), erorile frecvente ale clasei, detector de similaritate între
soluții (AST normalizat — redenumirea variabilelor nu păcălește analiza)
și generator AI de conținut cu **validare prin execuție** (un exercițiu
generat e acceptat doar dacă soluția generată trece testele generate)
și aprobare umană obligatorie.

### Degradare grațioasă fără cheie API

Aplicația funcționează complet fără Gemini: indiciile cad pe varianta
construită din taxonomia erorilor, testul adaptiv se construiește din banca
de întrebări (tot pe conceptele slabe BKT), iar tutorele răspunde cu
lecțiile relevante găsite prin RAG.

## Stack

- **Backend:** FastAPI · SQLAlchemy 2 + SQLite · JWT + bcrypt · LangChain + Google Gemini · RAG cu BM25 (embeddings opțional)
- **Frontend:** Vue 3 (Vite) · Vue Router · Pinia · Tailwind CSS 4 · CodeMirror 6 · Pyodide · marked + highlight.js + DOMPurify
- **Teste:** pytest — 55 de teste (algoritmi: BKT, SM-2, sandbox, recomandator; API: fluxuri anti-trișare) + `smoke_test.py` end-to-end pe server live

## Structura proiectului

```
licenta/
├── .env                  # GOOGLE_API_KEY, SECRET_KEY (nu intră în git)
├── backend/
│   ├── main.py           # asamblarea FastAPI (entry point)
│   ├── seed.py           # populare DB cu AUTOVALIDAREA exercițiilor prin execuție
│   ├── smoke_test.py     # verificare end-to-end pe serverul pornit
│   ├── content/          # cursul ca date: concepts.py + capitole/cap01..12.py
│   ├── tests/            # suita pytest
│   └── app/
│       ├── config.py     # toți parametrii (BKT, SM-2, XP, sandbox, praguri)
│       ├── models.py     # schema ORM completă
│       ├── engine/       # nucleul adaptiv: bkt, sm2, recommender, sandbox,
│       │                 #   errors (taxonomie), similarity, gamification
│       ├── ai/           # llm (Gemini), rag (BM25), tutor (socratic), generator
│       └── routers/      # auth, curs, exercitii, quiz, recapitulare,
│                         #   test_adaptiv, tutor (SSE), progres, gamificare, profesor
└── frontend/
    └── src/
        ├── pages/        # Dashboard, Curs, Lecție, Exercițiu, Quiz, Recapitulare,
        │                 #   TestAdaptiv, Tutore, Playground, Profil, Clasament, Profesor
        ├── components/   # CodeEditor, MarkdownView, McqRunner, TestResults,
        │                 #   MasteryMap (graful SVG al conceptelor), ToastStack
        ├── lib/          # pyodide (loader), harness (teste în browser), markdown
        ├── stores/       # Pinia: auth, ui
        └── router/       # rute + garduri de acces
```

## Pornire

### 1. Backend (port 8000)

Cel mai simplu, **din rădăcina proiectului** (funcționează din orice director):
```bash
pip install -r backend/requirements.txt
python run.py --seed      # prima dată: populează baza, apoi pornește serverul
python run.py             # pornirile următoare
```

Sau manual, **din interiorul folderului `backend/`** (altfel uvicorn dă
„Could not import module main”, fiindcă `main.py` se află în `backend/`):
```bash
cd backend
pip install -r requirements.txt
python seed.py            # prima dată: creează și populează baza de date
python main.py            # sau: uvicorn main:app --reload
```
Seed-ul validează fiecare exercițiu prin execuție — dacă o soluție de
referință nu trece propriile teste, popularea eșuează cu un raport precis.

### 2. Frontend (port 5173)
```bash
cd frontend
npm install
npm run dev
```

### 3. Configurare
Copiază `.env.example` în `.env` (în rădăcina proiectului) și completează
`GOOGLE_API_KEY` (opțional) și `SECRET_KEY`.

### Conturi implicite
- **profesor@codespace.ro** / `Profesor123!` — panoul profesorului
- **student@codespace.ro** / `Student123!` — cont de demonstrație

### Teste
```bash
cd backend
python -m pytest tests/ -q        # 55 de teste
python smoke_test.py              # end-to-end (cu serverul pornit)
```

## Conținutul cursului și bibliografia

12 capitole · 31 de lecții · 40 de exerciții autovalidate (135 de teste) ·
100 de întrebări — adaptat în limba română după surse citabile:

> **Downey, Allen B.** — *Think Python: How to Think Like a Computer
> Scientist*, ed. a 2-a, O'Reilly Media, 2015, ISBN 978-1-4919-3936-9.
> Disponibilă liber (Creative Commons): <https://greenteapress.com/thinkpython2/>

> **Python Software Foundation** — *The Python Tutorial*.
> <https://docs.python.org/3/tutorial/>

Fiecare lecție indică la final capitolul-sursă. Algoritmii nucleului:

> **Corbett, A. T., Anderson, J. R.** — *Knowledge tracing: Modeling the
> acquisition of procedural knowledge*, User Modeling and User-Adapted
> Interaction, 4(4), 1995. (modelul studentului)

> **Wozniak, P. A.** — algoritmul SuperMemo SM-2 (1990). (repetiția spațiată)
