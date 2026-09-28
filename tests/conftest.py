"""Configuração comum dos testes.

Nenhum teste chama uma API real: onde o livro usa um modelo,
os testes usam clientes falsos e determinísticos.
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


class _Resposta:
    def __init__(self, texto):
        self.output_text = texto
        self.output = []


class _ResponsesQueEcoaResumo:
    """Resumidor falso: devolve o resumo anterior + as mensagens.

    Serve para testar a propriedade que importa no Cap. 33:
    o resumo anterior precisa chegar ao modelo na compactação.
    """

    def create(self, model, input, **kwargs):
        anterior = ""
        for item in input:
            conteudo = item.get("content", "") if isinstance(item, dict) else ""
            if "Previous summary:" in conteudo:
                anterior = conteudo.split("Previous summary:", 1)[1].strip()
        mensagens = [
            item["content"] for item in input
            if isinstance(item, dict) and item.get("role") in ("user", "assistant")
        ]
        return _Resposta(anterior + " | " + "; ".join(mensagens))


class _ClienteFalso:
    def __init__(self):
        self.responses = _ResponsesQueEcoaResumo()


@pytest.fixture
def fake_client():
    """Fixture usada por test_cumulative_compaction (Cap. 33, técnico)."""
    return _ClienteFalso()
