"""Testes do Capítulo 51: coleta os testes da própria listagem do livro."""
import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parents[1] / "tecnico" / "cap51_workflow_duravel.py"
_SPEC = importlib.util.spec_from_file_location("cap51_workflow_duravel", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["cap51_workflow_duravel"] = _MOD
_SPEC.loader.exec_module(_MOD)

globals().update({k: v for k, v in vars(_MOD).items() if k.startswith("test_")})
