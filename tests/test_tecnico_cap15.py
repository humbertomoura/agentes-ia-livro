"""Cap. 15 (técnico): o decisor simulado precisa chegar ao diagnóstico."""
from tecnico.cap15_agent_loop.simulated import run_simulated


def test_simulated_reaches_diagnosis():
    answer = run_simulated()
    assert "database authentication failed" in answer
