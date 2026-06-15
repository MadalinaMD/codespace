# -*- coding: utf-8 -*-
"""Verificare end-to-end pe serverul live: parcurge fluxurile principale ale unui
student real, de la înregistrare la recomandări. Rulează cu serverul pornit."""
import sys

import httpx

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BAZA = "http://127.0.0.1:8000"
client = httpx.Client(base_url=BAZA, timeout=30)
pasi_ok = []


def pas(nume, conditie, detaliu=""):
    pasi_ok.append((nume, bool(conditie), detaliu))
    simbol = "OK " if conditie else "FAIL"
    print(f"[{simbol}] {nume}" + (f" -- {detaliu}" if detaliu and not conditie else ""))
    return conditie


# 1. Serverul e online
r = client.get("/")
pas("server online", r.status_code == 200 and r.json()["versiune"] == "3.0", r.text)

# 2. Înregistrare + login
email = "smoke@test.ro"
client.post("/auth/inregistrare", json={"nume": "Smoke Test", "email": email, "parola": "Parola123!"})
r = client.post("/auth/login", json={"email": email, "parola": "Parola123!"})
pas("login", r.status_code == 200, r.text)
token = r.json()["token"]
client.headers["Authorization"] = f"Bearer {token}"

# 3. Cursul: 12 capitole, lecții cu stare
r = client.get("/curs")
capitole = r.json()
pas("curs complet", len(capitole) == 12, f"{len(capitole)} capitole")
prima_lectie = capitole[0]["lectii"][0]
pas("starea lecțiilor", "fundament_gata" in prima_lectie and "vizitata" in prima_lectie)

# 4. Lecția: markdown + exemplu + navigare
r = client.get(f"/lectii/{prima_lectie['slug']}")
lectie = r.json()
pas("conținut lecție", len(lectie["continut_md"]) > 200 and lectie["cod_exemplu"])
pas("navigare lecție", lectie["urmatoarea"] is not None)
client.post(f"/lectii/{prima_lectie['slug']}/vizita")

# 5. Recomandările au motive
r = client.get("/progres/recomandari")
recomandari = r.json()["recomandari"]
pas("recomandări explicabile", len(recomandari) > 0 and all(rec["motiv"] for rec in recomandari))

# 6. Exercițiu: detalii fără soluție + trimitere greșită + corectă
r = client.get("/curs")
lectie_cu_ex = None
for cap in r.json():
    for lec in cap["lectii"]:
        if lec["exercitii_total"] > 0:
            lectie_cu_ex = lec
            break
    if lectie_cu_ex:
        break
detalii_lectie = client.get(f"/lectii/{lectie_cu_ex['slug']}").json()
ex_id = detalii_lectie["exercitii"][0]["id"]
r = client.get(f"/exercitii/{ex_id}")
exercitiu = r.json()
pas("exercițiul nu expune soluția", "solutie" not in str(exercitiu.keys()))
pas("testele sunt vizibile", len(exercitiu["teste"]) >= 1)

r = client.post(f"/exercitii/{ex_id}/trimite", json={"cod": "print(999)"})
verdict_gresit = r.json()
pas("soluția greșită e respinsă", verdict_gresit["status"] != "acceptat", verdict_gresit["status"])

# Exercițiul 1 e mod program (Calcule cu print) — trimitem soluția corectă
solutie_corecta = "print(24 * 60)\nprint(2026 // 7)\nprint(2026 % 7)\n"
r = client.post(f"/exercitii/{ex_id}/trimite", json={"cod": solutie_corecta})
verdict = r.json()
pas("soluția corectă e acceptată", verdict["status"] == "acceptat",
    f"{verdict['status']}: {verdict.get('eroare_mesaj')}")
pas("XP acordat la prima rezolvare", verdict["xp_castigat"] > 0 and verdict["prima_rezolvare"])

# 7. Codul periculos e blocat
r = client.post(f"/exercitii/{ex_id}/trimite", json={"cod": "import os\nprint(os.getcwd())"})
pas("importul periculos e blocat", r.json()["status"] == "blocat")

# 8. Indiciu (AI sau pe reguli — ambele răspund)
r = client.post(f"/exercitii/{ex_id}/indiciu", json={"cod": "print(1)", "nivel": 1})
pas("indiciu nivel 1", r.status_code == 200 and len(r.json()["continut"]) > 10,
    r.text[:120])

# 9. Quiz: fără răspunsuri în payload, notare pe server
slug_capitol = capitole[0]["slug"]
r = client.post(f"/quiz/incepe/{slug_capitol}")
quiz = r.json()
pas("quiz fără răspunsuri în payload",
    all(set(i.keys()) == {"id", "text", "variante"} for i in quiz["intrebari"]))
intrebare = quiz["intrebari"][0]
r = client.post(f"/quiz/{quiz['tentativa_id']}/raspunde",
                json={"intrebare_id": intrebare["id"], "raspuns": intrebare["variante"][0]})
pas("notare pe server", r.status_code == 200 and "corect" in r.json())
r = client.post(f"/quiz/{quiz['tentativa_id']}/finalizeaza")
pas("finalizare quiz", r.status_code == 200 and "scor" in r.json())

# 10. Harta măiestriei reflectă activitatea
r = client.get("/progres/harta")
harta = r.json()
observate = [c for c in harta["concepte"] if c["observatii"] > 0]
pas("modelul BKT s-a actualizat", len(observate) >= 1,
    f"{len(observate)} concepte cu observații")

# 11. Statistici + gamificare
r = client.get("/progres/statistici")
statistici = r.json()
pas("statistici", statistici["streak"] >= 1 and statistici["xp_total"] > 0)
r = client.get("/gamificare/profil")
pas("realizări deblocate", any(re["deblocata"] for re in r.json()["realizari"]))

# 12. Clasament fără emailuri
r = client.get("/clasament")
pas("clasament fără emailuri", all("email" not in i for i in r.json()))

# 13. Profesor: login + panou
r = client.post("/auth/login", json={"email": "profesor@codespace.ro", "parola": "Profesor123!"})
client.headers["Authorization"] = f"Bearer {r.json()['token']}"
r = client.get("/profesor/ansamblu")
pas("panou profesor", r.status_code == 200 and r.json()["lectii"] == 31, r.text[:120])
r = client.get("/profesor/heatmap")
pas("heatmap concepte", r.status_code == 200 and len(r.json()) == 35)
r = client.get("/profesor/studenti")
pas("lista studenți", r.status_code == 200 and len(r.json()) >= 1)

esuate = [(n, d) for n, ok, d in pasi_ok if not ok]
print(f"\n{'='*50}\nRezultat: {len(pasi_ok) - len(esuate)}/{len(pasi_ok)} pași OK")
if esuate:
    sys.exit(1)
