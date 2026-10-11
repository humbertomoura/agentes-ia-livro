"""Versão comercial: cada exemplo precisa imprimir exatamente
a saída que aparece no livro (guardada em saida_esperada.txt)."""
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "comercial"

EXEMPLOS = [
    ("parte1_cap08_ar_condicionado", "rodar.py"),
    ("parte2_cap15_atendente", "simulado.py"),
    ("parte3_cap24_ferramentas", "demo.py"),
    ("parte4_cap33_caderno", "demo.py"),
    ("parte5_cap42_pasta", "demo.py"),
]


@pytest.mark.parametrize("pasta,script", EXEMPLOS)
def test_saida_igual_ao_livro(pasta, script):
    diretorio = RAIZ / pasta
    resultado = subprocess.run(
        [sys.executable, script], cwd=diretorio,
        capture_output=True, text=True, check=True)
    esperado = (diretorio / "saida_esperada.txt").read_text(encoding="utf-8")
    assert resultado.stdout == esperado


def test_cap15_real_com_cliente_falso(monkeypatch, capsys):
    """Roda o ciclo real do Cap. 15 trocando a API por um falso:
    duas chamadas no mesmo turno, correlação por call_id e término."""
    fakes = Path(__file__).parent / "fakes"
    modulo = runpy.run_path(str(fakes / "openai_fake_comercial.py"))
    falso = type(sys)("openai")
    falso.OpenAI = modulo["OpenAI"]
    monkeypatch.setitem(sys.modules, "openai", falso)
    diretorio = RAIZ / "parte2_cap15_atendente"
    monkeypatch.chdir(diretorio)
    monkeypatch.syspath_prepend(str(diretorio))
    runpy.run_path(str(diretorio / "real.py"), run_name="__main__")
    saida = capsys.readouterr().out
    assert "sexta tem vaga" in saida


def test_cap33_pedido_de_exclusao_nao_vaza_outra_cliente():
    """Propriedade central do Cap. 33: o portão de leitura
    nunca devolve anotações de outra cliente."""
    diretorio = RAIZ / "parte4_cap33_caderno"
    codigo = (
        "import sys; sys.path.insert(0, '.');"
        "from caderno import anotar;"
        "from lembrar import lembrar;"
        "anotar('A', 'sabor', 'gosta de chocolate', 'cliente');"
        "print(len(lembrar('B', 'chocolate', hoje='2026-01-01')))"
    )
    resultado = subprocess.run(
        [sys.executable, "-c", codigo], cwd=diretorio,
        capture_output=True, text=True, check=True)
    assert resultado.stdout.strip() == "0"
