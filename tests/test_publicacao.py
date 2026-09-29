"""O código em tecnico/ precisa ser idêntico às listagens do manuscrito."""
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.mark.skipif(not list((ROOT / "manuscrito").glob("Agentes_IA_v*.docx")),
                    reason="manuscrito não versionado neste clone")
def test_codigo_igual_ao_manuscrito():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "extrair_codigo.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
