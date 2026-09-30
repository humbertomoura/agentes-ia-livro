"""Versão comercial: cada exemplo imprime exatamente a saída do livro."""
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1] / "comercial"

EXEMPLOS = [
    ("cap13_encomenda_casamento", "demo.py"),
    ("cap30_projeto_final",       "demo.py"),
]


@pytest.mark.parametrize("pasta,script", EXEMPLOS)
def test_saida_igual_ao_livro(pasta, script):
    diretorio = RAIZ / pasta
    resultado = subprocess.run(
        [sys.executable, script], cwd=diretorio,
        capture_output=True, text=True, check=True)
    esperado = (diretorio / "saida.txt").read_text(encoding="utf-8")
    assert resultado.stdout == esperado
