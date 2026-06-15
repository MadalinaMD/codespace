"""Teste pentru evaluatorul de cod (analiza AST + execuția izolată)."""
from app.engine import sandbox

TESTE_DUBLU = [
    {"apel": "dublu(2)", "asteptat": "4"},
    {"apel": "dublu(-3)", "asteptat": "-6"},
    {"apel": "dublu(0)", "asteptat": "0"},
]


def test_solutie_corecta_este_acceptata():
    rezultat = sandbox.ruleaza_teste("def dublu(n):\n    return n * 2\n", TESTE_DUBLU)
    assert rezultat.status == "acceptat"
    assert rezultat.teste_trecute == 3
    assert all(r["trecut"] for r in rezultat.rezultate)


def test_solutie_gresita_pica_testele():
    rezultat = sandbox.ruleaza_teste("def dublu(n):\n    return n + 2\n", TESTE_DUBLU)
    assert rezultat.status == "teste_esuate"
    assert rezultat.teste_trecute == 1  # dublu(2) == 4 din întâmplare
    assert rezultat.eroare_categorie == "raspuns_gresit"
    picat = next(r for r in rezultat.rezultate if not r["trecut"])
    assert picat["obtinut"] is not None and picat["asteptat"] is not None


def test_eroarea_de_sintaxa_este_clasificata():
    rezultat = sandbox.ruleaza_teste("def dublu(n)\n    return n * 2\n", TESTE_DUBLU)
    assert rezultat.status == "eroare"
    assert rezultat.eroare_categorie == "sintaxa"


def test_eroarea_de_nume_este_clasificata():
    rezultat = sandbox.ruleaza_teste("def dublu(n):\n    return m * 2\n", TESTE_DUBLU)
    assert rezultat.status == "teste_esuate"
    assert rezultat.eroare_categorie == "nume_nedefinit"


def test_importul_nepermis_este_blocat_inainte_de_executie():
    rezultat = sandbox.ruleaza_teste("import os\ndef dublu(n):\n    return n * 2\n", TESTE_DUBLU)
    assert rezultat.status == "blocat"
    assert rezultat.eroare_categorie == "import_blocat"


def test_importul_permis_functioneaza():
    cod = "import math\ndef dublu(n):\n    return int(math.floor(n)) * 2\n"
    rezultat = sandbox.ruleaza_teste(cod, TESTE_DUBLU)
    assert rezultat.status == "acceptat"


def test_functiile_de_sistem_sunt_blocate():
    rezultat = sandbox.ruleaza_teste("def dublu(n):\n    return eval('n * 2')\n", TESTE_DUBLU)
    assert rezultat.status == "blocat"
    assert rezultat.eroare_categorie == "cod_periculos"


def test_atributele_interne_sunt_blocate():
    cod = "def dublu(n):\n    return (lambda: 1).__globals__\n"
    rezultat = sandbox.ruleaza_teste(cod, TESTE_DUBLU)
    assert rezultat.status == "blocat"


def test_bucla_infinita_da_timeout():
    cod = "while True:\n    pass\ndef dublu(n):\n    return n * 2\n"
    rezultat = sandbox.ruleaza_teste(cod, TESTE_DUBLU, timeout_s=2)
    assert rezultat.status == "timeout"
    assert rezultat.eroare_categorie == "bucla_infinita"


def test_mod_program_compara_stdout():
    cod = "n = int(input())\nprint(n * n)\n"
    teste = [
        {"stdin": "5\n", "asteptat": "25"},
        {"stdin": "10\n", "asteptat": "100"},
    ]
    rezultat = sandbox.ruleaza_teste(cod, teste, mod="program")
    assert rezultat.status == "acceptat"


def test_mod_program_rezultat_gresit():
    cod = "n = int(input())\nprint(n + n)\n"
    teste = [{"stdin": "5\n", "asteptat": "25"}]
    rezultat = sandbox.ruleaza_teste(cod, teste, mod="program")
    assert rezultat.status == "teste_esuate"
    assert rezultat.rezultate[0]["obtinut"].strip() == "10"


def test_toleranta_la_virgula_mobila():
    cod = "def aduna(a, b):\n    return a + b\n"
    teste = [{"apel": "aduna(0.1, 0.2)", "asteptat": "0.3"}]
    rezultat = sandbox.ruleaza_teste(cod, teste)
    assert rezultat.status == "acceptat"


def test_iesirea_excesiva_este_oprita():
    cod = "for i in range(10**7):\n    print('x' * 50)\n"
    teste = [{"stdin": "", "asteptat": "nimic"}]
    rezultat = sandbox.ruleaza_teste(cod, teste, mod="program", timeout_s=10)
    assert rezultat.status in ("teste_esuate", "eroare", "timeout")


def test_asteptarea_unei_exceptii():
    cod = "def verifica(n):\n    if n < 0:\n        raise ValueError('negativ')\n    return n\n"
    teste = [
        {"apel": "verifica(5)", "asteptat": "5"},
        {"apel": "verifica(-1)", "eroare": "ValueError"},
    ]
    rezultat = sandbox.ruleaza_teste(cod, teste)
    assert rezultat.status == "acceptat"

    # Funcția care NU ridică excepția așteptată pică testul
    cod_gresit = "def verifica(n):\n    return n\n"
    rezultat = sandbox.ruleaza_teste(cod_gresit, teste)
    assert rezultat.status == "teste_esuate"
    assert rezultat.teste_trecute == 1


def test_recursivitatea_infinita_este_clasificata():
    cod = "def dublu(n):\n    return dublu(n)\n"
    rezultat = sandbox.ruleaza_teste(cod, [{"apel": "dublu(1)", "asteptat": "2"}])
    assert rezultat.status == "teste_esuate"
    assert rezultat.eroare_categorie == "recursivitate_infinita"
