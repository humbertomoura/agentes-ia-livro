"""O código em tecnico/ precisa ser idêntico às listagens do manuscrito."""
import pathlib
import subprocess
import sys

import pytest
from scripts import extrair_codigo

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_check_ignora_manuscrito_sem_versao_tecnica(tmp_path, monkeypatch, capsys):
    (tmp_path / "manuscrito").mkdir()
    (tmp_path / "manuscrito" / "Agentes_IA_Essencial_v1.docx").touch()
    monkeypatch.setattr(extrair_codigo, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["extrair_codigo.py", "--check"])

    assert extrair_codigo.main() == 0
    assert "verificação ignorada" in capsys.readouterr().out


@pytest.mark.skipif(not list((ROOT / "manuscrito").glob("Agentes_IA_v*.docx")),
                    reason="manuscrito não versionado neste clone")
def test_codigo_igual_ao_manuscrito():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "extrair_codigo.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
