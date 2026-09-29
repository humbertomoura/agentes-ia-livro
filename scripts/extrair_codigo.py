"""Extrai as listagens dos capítulos de implementação do manuscrito (.docx).

Uso:
    python scripts/extrair_codigo.py            # regrava tecnico/*.py a partir do docx
    python scripts/extrair_codigo.py --check    # só compara; sai com código 1 se divergir

Usa apenas a biblioteca padrão. O docx esperado fica em manuscrito/.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# arquivo em tecnico/ -> início do título do capítulo (Heading 1)
CAPITULOS = {
    "cap51_workflow_duravel": "Implementando um workflow durável",
    "cap60_runtime_multiagente": "Implementando um runtime multiagente",
    "cap69_adaptadores_protocolo": "Implementando adaptadores de protocolo",
    "cap78_runtime_duravel": "Implementando um runtime durável sem framework",
    "cap87_portfolio_especialistas": "Implementando um portfólio",
    "cap96_eval_harness": "Implementando um eval harness",
    "cap105_observabilidade_otel": "Implementando observabilidade",
    "cap114_security_gateway": "Implementando uma camada de segurança",
    "cap125_system_design_core": "Implementando um núcleo de System Design",
    "cap135_portabilidade_frameworks": "Implementando uma camada de portabilidade",
    "cap136_agent_loop_minimo": "Projeto 1",
    "cap144_servico_production_grade": "Projeto final",
    "cap153_readiness_gate": "Da fronteira à produção",
}
SHELL = re.compile(r"\s*(python -m|pip |\$ |uv )")


def manuscrito() -> pathlib.Path:
    docs = sorted((ROOT / "manuscrito").glob("Agentes_IA_v*.docx"),
                  key=lambda p: int(re.search(r"v(\d+)", p.name).group(1)))
    if not docs:
        sys.exit("nenhum manuscrito em manuscrito/")
    return docs[-1]


def paragrafos(path: pathlib.Path) -> list[tuple[str, str]]:
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    out = []
    for el in root.find(W + "body"):
        if el.tag != W + "p":
            out.append(("", ""))  # tabela interrompe bloco de código
            continue
        st = el.find(f"{W}pPr/{W}pStyle")
        style = st.get(W + "val") if st is not None else ""
        out.append((style, "".join(t.text or "" for t in el.iter(W + "t"))))
    return out


def listagem(paras, titulo: str, nome: str) -> str:
    heads = [i for i, (s, _) in enumerate(paras) if s == "Heading1"]
    inicio = [i for i in heads if paras[i][1].startswith(titulo)][-1]
    fim = next((i for i in heads if i > inicio), len(paras))
    blocos, atual = [], []
    for style, text in paras[inicio:fim]:
        if style == "Código":
            atual.append(text)
        elif atual:
            blocos.append(atual)
            atual = []
    if atual:
        blocos.append(atual)
    corpo = "\n\n".join("\n".join(b) for b in blocos if not SHELL.match(b[0]))
    cap = re.search(r"\d+", nome).group(0)
    cabecalho = (f'"""Código do Capítulo {cap} — {paras[inicio][1]}.\n\n'
                 'Extraído da versão técnica v26 do livro "Agentes de Inteligência Artificial".\n'
                 'Mantenha este arquivo idêntico à listagem publicada no manuscrito.\n"""\n')
    linhas = corpo.split("\n")
    futuro = [l for l in linhas if l.startswith("from __future__")]
    if futuro:
        linhas = [l for l in linhas if not l.startswith("from __future__")]
        cabecalho += futuro[0] + "\n"
    return cabecalho + "\n" + "\n".join(linhas).strip("\n") + "\n"


def corpo(texto: str) -> str:
    """Ignora o docstring de cabeçalho (que cita a versão) na comparação."""
    return texto.split('"""', 2)[-1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    paras = paragrafos(manuscrito())
    divergentes = []
    for nome, titulo in CAPITULOS.items():
        novo = listagem(paras, titulo, nome)
        destino = ROOT / "tecnico" / f"{nome}.py"
        atual = destino.read_text(encoding="utf-8") if destino.exists() else ""
        if corpo(atual) != corpo(novo):
            divergentes.append(nome)
            if not args.check:
                destino.write_text(novo, encoding="utf-8")
    if args.check and divergentes:
        print("divergem do manuscrito:", ", ".join(divergentes))
        return 1
    print("ok" if not divergentes else f"regravados: {', '.join(divergentes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
