"""Teste de API end-to-end (FastAPI TestClient) — cu accent pe anti-trișare."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app import config
from app.deps import get_db
from app.engine import gamification
from app.models import StareConcept
from main import app
from tests.conftest import (creeaza_capitol, creeaza_concept,
                            creeaza_exercitiu, creeaza_intrebare,
                            creeaza_lectie)


@pytest.fixture()
def client(db):
    """TestClient cu baza de date în memorie injectată în aplicație."""
    def _get_db_test():
        yield db

    app.dependency_overrides[get_db] = _get_db_test
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def curs(db):
    """Conținut minimal: un capitol cu lecție, exercițiu și 3 întrebări."""
    gamification.seed_realizari(db)
    capitol = creeaza_capitol(db, slug="cap-test")
    concept = creeaza_concept(db, "concept_test")
    lectie = creeaza_lectie(db, capitol, "lectie-test", concepte=[concept])
    exercitiu = creeaza_exercitiu(db, lectie, concepte=[concept])
    intrebari = [creeaza_intrebare(db, capitol, concepte=[concept],
                                   text=f"Întrebarea {i}?") for i in range(3)]
    db.commit()
    return {"capitol": capitol, "concept": concept, "lectie": lectie,
            "exercitiu": exercitiu, "intrebari": intrebari}


def _token(client, email="student.api@test.ro"):
    client.post("/auth/inregistrare", json={
        "nume": "Student API", "email": email, "parola": "Parola123!"})
    raspuns = client.post("/auth/login", json={"email": email, "parola": "Parola123!"})
    assert raspuns.status_code == 200
    return {"Authorization": f"Bearer {raspuns.json()['token']}"}


# ── Autentificare ───────────────────────────────────────────────
def test_inregistrare_login_si_profil(client):
    antet = _token(client)
    raspuns = client.get("/auth/eu", headers=antet)
    assert raspuns.status_code == 200
    assert raspuns.json()["rol"] == "student"


def test_email_duplicat_respins(client):
    date = {"nume": "Test", "email": "dublu@test.ro", "parola": "Parola123!"}
    assert client.post("/auth/inregistrare", json=date).status_code == 200
    assert client.post("/auth/inregistrare", json=date).status_code == 400


def test_acces_fara_token_respins(client):
    assert client.get("/curs").status_code == 401  # fără antet de autorizare


def test_resetarea_parolei_genereaza_o_parola_functionala(client):
    _token(client, email="uituc@test.ro")  # creează contul

    # Cerem resetarea — primim o parolă temporară
    raspuns = client.post("/auth/reset-parola", json={"email": "uituc@test.ro"})
    assert raspuns.status_code == 200
    parola_noua = raspuns.json()["parola_temporara"]
    assert len(parola_noua) >= 8

    # Parola veche nu mai merge, cea nouă da
    assert client.post("/auth/login", json={"email": "uituc@test.ro",
                                            "parola": "Parola123!"}).status_code == 401
    login = client.post("/auth/login", json={"email": "uituc@test.ro", "parola": parola_noua})
    assert login.status_code == 200 and login.json()["token"]


def test_resetarea_pentru_email_inexistent_da_404(client):
    raspuns = client.post("/auth/reset-parola", json={"email": "nuexista@test.ro"})
    assert raspuns.status_code == 404


# ── Quiz: scoring exclusiv pe server ────────────────────────────
def test_quizul_nu_dezvaluie_raspunsul_corect(client, curs):
    antet = _token(client)
    raspuns = client.post(f"/quiz/incepe/{curs['capitol'].slug}", headers=antet)
    assert raspuns.status_code == 200
    date = raspuns.json()
    for intrebare in date["intrebari"]:
        assert set(intrebare.keys()) == {"id", "text", "variante"}
        assert len(intrebare["variante"]) == 4  # corecta + 3 greșite, amestecate


def test_quiz_raspuns_si_finalizare(client, curs):
    antet = _token(client)
    inceput = client.post(f"/quiz/incepe/{curs['capitol'].slug}", headers=antet).json()
    tentativa_id = inceput["tentativa_id"]

    # Răspundem corect la prima întrebare (corecta e "4" din fabrică)
    prima = inceput["intrebari"][0]
    verdict = client.post(f"/quiz/{tentativa_id}/raspunde", headers=antet,
                          json={"intrebare_id": prima["id"], "raspuns": "4"}).json()
    assert verdict["corect"] is True
    assert verdict["corecta"] == "4"  # dezvăluit DOAR după răspuns

    # Răspuns dublu la aceeași întrebare: respins
    din_nou = client.post(f"/quiz/{tentativa_id}/raspunde", headers=antet,
                          json={"intrebare_id": prima["id"], "raspuns": "4"})
    assert din_nou.status_code == 400

    # Greșim a doua întrebare, apoi finalizăm
    a_doua = inceput["intrebari"][1]
    client.post(f"/quiz/{tentativa_id}/raspunde", headers=antet,
                json={"intrebare_id": a_doua["id"], "raspuns": "greșit"})
    final = client.post(f"/quiz/{tentativa_id}/finalizeaza", headers=antet).json()
    assert final["scor"] == 1
    assert final["total"] == 3
    assert final["prima_tentativa"] is True
    assert final["xp_castigat"] == 1 * config.XP_INTREBARE_QUIZ


def test_xp_doar_la_prima_tentativa(client, curs):
    antet = _token(client)
    for asteptat_prima in (True, False):
        inceput = client.post(f"/quiz/incepe/{curs['capitol'].slug}", headers=antet).json()
        final = client.post(f"/quiz/{inceput['tentativa_id']}/finalizeaza",
                            headers=antet).json()
        assert final["prima_tentativa"] is asteptat_prima
        if not asteptat_prima:
            assert final["xp_castigat"] == 0


# ── Exerciții: evaluare pe server + modelul studentului ─────────
def test_trimiterea_solutiei_corecte(client, curs, db):
    antet = _token(client)
    exercitiu_id = curs["exercitiu"].id
    raspuns = client.post(f"/exercitii/{exercitiu_id}/trimite", headers=antet,
                          json={"cod": "def dublu(n):\n    return n * 2\n"})
    date = raspuns.json()
    assert date["status"] == "acceptat"
    assert date["prima_rezolvare"] is True
    assert date["xp_castigat"] == config.XP_EXERCITIU

    # Modelul studentului a învățat din succes (exercițiu: dovadă puternică)
    stare = db.execute(select(StareConcept)).scalars().first()
    assert stare is not None and stare.p_cunoastere > config.BKT_P_INIT

    # Retrimiterea nu mai dă XP
    din_nou = client.post(f"/exercitii/{exercitiu_id}/trimite", headers=antet,
                          json={"cod": "def dublu(n):\n    return n * 2\n"}).json()
    assert din_nou["prima_rezolvare"] is False
    assert din_nou["xp_castigat"] == 0


def test_solutia_gresita_clasifica_eroarea(client, curs):
    antet = _token(client)
    raspuns = client.post(f"/exercitii/{curs['exercitiu'].id}/trimite", headers=antet,
                          json={"cod": "def dublu(n):\n    return m * 2\n"}).json()
    assert raspuns["status"] == "teste_esuate"
    assert raspuns["eroare"]["categorie"] == "nume_nedefinit"
    assert raspuns["xp_castigat"] == 0


def test_indiciile_se_deblocheaza_secvential(client, curs, monkeypatch):
    monkeypatch.setattr("app.ai.tutor.obtine_llm", lambda: None)  # varianta pe reguli
    antet = _token(client)
    exercitiu_id = curs["exercitiu"].id

    sarit = client.post(f"/exercitii/{exercitiu_id}/indiciu", headers=antet,
                        json={"cod": "", "nivel": 2})
    assert sarit.status_code == 400

    primul = client.post(f"/exercitii/{exercitiu_id}/indiciu", headers=antet,
                         json={"cod": "def dublu(n):\n    return n + 2\n", "nivel": 1})
    assert primul.status_code == 200
    assert len(primul.json()["continut"]) > 10


def test_indiciile_reduc_xp(client, curs, monkeypatch):
    monkeypatch.setattr("app.ai.tutor.obtine_llm", lambda: None)
    antet = _token(client)
    exercitiu_id = curs["exercitiu"].id
    client.post(f"/exercitii/{exercitiu_id}/indiciu", headers=antet,
                json={"cod": "", "nivel": 1})
    raspuns = client.post(f"/exercitii/{exercitiu_id}/trimite", headers=antet,
                          json={"cod": "def dublu(n):\n    return n * 2\n"}).json()
    assert raspuns["xp_castigat"] == config.XP_EXERCITIU - config.XP_PENALIZARE_INDICIU


# ── Recapitulare SM-2 ───────────────────────────────────────────
def test_intrebarea_gresita_intra_in_recapitulare(client, curs):
    antet = _token(client)
    inceput = client.post(f"/quiz/incepe/{curs['capitol'].slug}", headers=antet).json()
    prima = inceput["intrebari"][0]
    client.post(f"/quiz/{inceput['tentativa_id']}/raspunde", headers=antet,
                json={"intrebare_id": prima["id"], "raspuns": "greșit"})

    coada = client.get("/recapitulare", headers=antet).json()
    assert coada["total_scadente"] == 1
    card = coada["carduri"][0]

    verdict = client.post(f"/recapitulare/{card['card_id']}/raspunde", headers=antet,
                          json={"intrebare_id": card["intrebare_id"], "raspuns": "4"}).json()
    assert verdict["corect"] is True
    assert verdict["interval_zile"] == 1.0  # prima repetare SM-2

    # Cardul reprogramat nu mai e scadent azi
    dupa = client.get("/recapitulare", headers=antet).json()
    assert dupa["total_scadente"] == 0


# ── Progres și recomandări ──────────────────────────────────────
def test_recomandarile_au_motive(client, curs):
    antet = _token(client)
    raspuns = client.get("/progres/recomandari", headers=antet).json()
    assert raspuns["recomandari"], "utilizatorul nou primește măcar o recomandare"
    assert all(r.get("motiv") for r in raspuns["recomandari"])


def test_harta_maiestriei(client, curs):
    antet = _token(client)
    harta = client.get("/progres/harta", headers=antet).json()
    assert harta["total"] == 1
    nod = harta["concepte"][0]
    assert nod["stare"] == "nestudiat"
    assert nod["p"] == config.BKT_P_INIT


# ── Securitate și confidențialitate ─────────────────────────────
def test_rutele_profesorului_sunt_protejate(client, curs):
    antet = _token(client)
    assert client.get("/profesor/ansamblu", headers=antet).status_code == 403


def test_clasamentul_nu_expune_emailuri(client, curs):
    antet = _token(client)
    client.post(f"/exercitii/{curs['exercitiu'].id}/trimite", headers=antet,
                json={"cod": "def dublu(n):\n    return n * 2\n"})
    clasament = client.get("/clasament", headers=antet).json()
    assert clasament, "studentul activ apare în clasament"
    assert all("email" not in intrare for intrare in clasament)


def test_exercitiul_nu_expune_solutia_de_referinta(client, curs):
    antet = _token(client)
    detalii = client.get(f"/exercitii/{curs['exercitiu'].id}", headers=antet).json()
    assert "solutie_referinta" not in detalii
    assert "solutie" not in detalii


def test_solutia_de_referinta_apare_dupa_rezolvare(client, curs):
    antet = _token(client)
    exercitiu_id = curs["exercitiu"].id
    client.post(f"/exercitii/{exercitiu_id}/trimite", headers=antet,
                json={"cod": "def dublu(n):\n    return n * 2\n"})
    detalii = client.get(f"/exercitii/{exercitiu_id}", headers=antet).json()
    assert "return n * 2" in detalii["solutie_referinta"]


# ── Testul de plasament (calibrarea inițială BKT) ───────────────
def _curs_cu_prerechizite(db):
    """Trei concepte înlănțuite (a ← b ← c), fiecare cu o întrebare."""
    from tests.conftest import (creeaza_capitol, creeaza_concept,
                                creeaza_intrebare, creeaza_lectie)
    capitol = creeaza_capitol(db, slug="cap-plasament")
    a = creeaza_concept(db, "concept_a")
    b = creeaza_concept(db, "concept_b", prerechizite=[a])
    c = creeaza_concept(db, "concept_c", prerechizite=[b])
    for ordine, concept in enumerate([a, b, c], start=1):
        creeaza_lectie(db, capitol, f"lectie-{concept.slug}", concepte=[concept], ordine=ordine)
        creeaza_intrebare(db, capitol, concepte=[concept], text=f"Întrebare {concept.slug}?")
    db.commit()
    return a, b, c


def test_plasamentul_acopera_concepte_diverse(client, db):
    _curs_cu_prerechizite(db)
    antet = _token(client)
    raspuns = client.post("/test-adaptiv/plasament/incepe", headers=antet)
    assert raspuns.status_code == 200
    date = raspuns.json()
    assert date["total"] == 3
    # Fără răspunsuri corecte în payload
    assert all(set(i.keys()) == {"index", "text", "variante"} for i in date["intrebari"])


def test_plasamentul_propaga_dovada_catre_prerechizite(client, db):
    from app.models import StareConcept
    a, b, c = _curs_cu_prerechizite(db)
    antet = _token(client)
    inceput = client.post("/test-adaptiv/plasament/incepe", headers=antet).json()

    # Răspundem corect la toate ("4" e corecta din fabrică)
    for intrebare in inceput["intrebari"]:
        client.post(f"/test-adaptiv/{inceput['test_id']}/raspunde", headers=antet,
                    json={"index": intrebare["index"], "raspuns": "4"})

    stari = {s.concept_id: s for s in db.query(StareConcept).all()}
    # Conceptul a a primit: propria întrebare + propagare de la b → minim 2 observații
    assert stari[a.id].nr_observatii >= 2
    assert stari[a.id].p_cunoastere > stari[c.id].p_cunoastere * 0.5  # toate au crescut

    final = client.post(f"/test-adaptiv/{inceput['test_id']}/finalizeaza", headers=antet).json()
    assert final["tip"] == "plasament"
    assert final["xp_castigat"] == 0  # plasamentul nu dă XP
    assert "start" in final and final["start"]["lectie_slug"]


def test_plasamentul_recomanda_startul_potrivit(client, db):
    """Student care știe primele concepte → startul sare peste lecțiile lor."""
    a, b, c = _curs_cu_prerechizite(db)
    antet = _token(client)
    inceput = client.post("/test-adaptiv/plasament/incepe", headers=antet).json()
    # Corect la primele două (a, b), greșit la c
    for intrebare in inceput["intrebari"]:
        raspuns = "4" if intrebare["index"] < 2 else "greșit"
        client.post(f"/test-adaptiv/{inceput['test_id']}/raspunde", headers=antet,
                    json={"index": intrebare["index"], "raspuns": raspuns})
    final = client.post(f"/test-adaptiv/{inceput['test_id']}/finalizeaza", headers=antet).json()
    assert final["start"]["lectie_slug"] == "lectie-concept_c"
    assert final["start"]["lectii_sarite"] == 2
