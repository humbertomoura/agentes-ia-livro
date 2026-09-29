"""Testes do Capítulo 69: coleta os testes da própria listagem do livro."""
import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parents[1] / "tecnico" / "cap69_adaptadores_protocolo.py"
_SPEC = importlib.util.spec_from_file_location("cap69_adaptadores_protocolo", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["cap69_adaptadores_protocolo"] = _MOD
_SPEC.loader.exec_module(_MOD)

globals().update({k: v for k, v in vars(_MOD).items() if k.startswith("test_")})
