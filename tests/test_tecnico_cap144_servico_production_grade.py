"""Testes do Capítulo 144: coleta os testes da própria listagem do livro."""
import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parents[1] / "tecnico" / "cap144_servico_production_grade.py"
_SPEC = importlib.util.spec_from_file_location("cap144_servico_production_grade", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["cap144_servico_production_grade"] = _MOD
_SPEC.loader.exec_module(_MOD)

globals().update({k: v for k, v in vars(_MOD).items() if k.startswith("test_")})
