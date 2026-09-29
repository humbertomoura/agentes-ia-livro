"""Testes do Capítulo 136: coleta os testes da própria listagem do livro."""
import importlib.util
import pathlib
import sys

_PATH = pathlib.Path(__file__).resolve().parents[1] / "tecnico" / "cap136_agent_loop_minimo.py"
_SPEC = importlib.util.spec_from_file_location("cap136_agent_loop_minimo", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["cap136_agent_loop_minimo"] = _MOD
_SPEC.loader.exec_module(_MOD)

globals().update({k: v for k, v in vars(_MOD).items() if k.startswith("test_")})
