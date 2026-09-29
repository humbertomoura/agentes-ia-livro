"""Testes do Capítulo 78: coleta os testes da própria listagem do livro."""
import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parents[1] / "tecnico" / "cap78_runtime_duravel.py"
_SPEC = importlib.util.spec_from_file_location("cap78_runtime_duravel", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["cap78_runtime_duravel"] = _MOD
_SPEC.loader.exec_module(_MOD)

globals().update({k: v for k, v in vars(_MOD).items() if k.startswith("test_")})
