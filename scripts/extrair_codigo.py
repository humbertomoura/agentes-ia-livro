"""Extrai as listagens Python da edição comercial do manuscrito (.docx).

Uso:
    python scripts/extrair_codigo.py
        Regrava os snapshots extraídos do manuscrito.

    python scripts/extrair_codigo.py --check
        Apenas compara. Retorna código 1 se algum snapshot divergir.

Se não houver manuscrito em manuscrito/, a verificação é ignorada.
Usa apenas a biblioteca padrão.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]

# Se preferir outra pasta para os snapshots, altere somente esta linha.
PASTA_SAIDA = ROOT / "tecnico"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

# A edição comercial atual possui implementação substancial
# nestes cinco capítulos.
CAPITULOS = {
    "cap05_atendente_dona_cida":
        "Mão na massa: o atendente da Dona Cida",

    "cap08_encomendas_aprovacao":
        "Mão na massa: encomendas com aprovação",

    "cap11_respostas_com_fonte":
        "Mão na massa: respostas com fonte",

    "cap13_encomenda_casamento":
        "Mão na massa: a encomenda do casamento",

    "cap26_padaria_inteira":
        "Projeto final: a padaria inteira",
}


# Blocos de terminal que não devem virar Python.
SHELL = re.compile(
    r"\s*(?:"
    r"python(?:3)?(?:\s+-m)?\s+|"
    r"pip(?:3)?\s+|"
    r"uv\s+|"
    r"source\s+|"
    r"\.venv[\\/]|"
    r"\$\s+"
    r")"
)


def normalizar(texto: str) -> str:
    """Normaliza texto vindo do Word para comparações de títulos."""
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("\u00ad", "")   # soft hyphen
    texto = texto.replace("\u2011", "-")  # non-breaking hyphen
    return " ".join(texto.split()).strip().casefold()


def numero_versao(path: pathlib.Path) -> int:
    """Extrai vN do nome; arquivos sem versão recebem -1."""
    achado = re.search(r"(?:^|[_-])v(\d+)", path.stem, re.I)
    return int(achado.group(1)) if achado else -1


def manuscrito() -> pathlib.Path | None:
    pasta = ROOT / "manuscrito"

    if not pasta.exists():
        return None

    docs = list(pasta.glob("Agentes_IA*.docx"))

    if not docs:
        return None

    # Maior versão primeiro; mtime desempata.
    docs.sort(
        key=lambda p: (numero_versao(p), p.stat().st_mtime)
    )

    return docs[-1]


def texto_paragrafo(el: ET.Element) -> str:
    return "".join(
        t.text or ""
        for t in el.iter(W + "t")
    )


def estilo_paragrafo(el: ET.Element) -> str:
    st = el.find(f"{W}pPr/{W}pStyle")
    return st.get(W + "val") if st is not None else ""


def preenchimento(el: ET.Element) -> str:
    ppr = el.find(W + "pPr")

    if ppr is None:
        return ""

    shd = ppr.find(W + "shd")

    if shd is None:
        return ""

    return (shd.get(W + "fill") or "").upper()


def usa_consolas(el: ET.Element) -> bool:
    """Confere se ao menos um run usa Consolas."""
    for run in el.findall(W + "r"):
        fonts = run.find(f"{W}rPr/{W}rFonts")

        if fonts is None:
            continue

        valores = {
            fonts.get(W + "ascii"),
            fonts.get(W + "hAnsi"),
            fonts.get(W + "eastAsia"),
            fonts.get(W + "cs"),
        }

        if "Consolas" in valores:
            return True

    return False


def eh_codigo(el: ET.Element) -> bool:
    """Reconhece os blocos monoespaçados da edição comercial."""

    if el.tag != W + "p":
        return False

    style = estilo_paragrafo(el)

    # Compatibilidade caso uma edição futura volte
    # a usar um estilo específico.
    if normalizar(style) in {
        "código",
        "codigo",
        "code",
    }:
        return True

    # Na edição comercial atual, código e saída aparecem
    # como parágrafos de fundo cinza e fonte Consolas.
    return (
        preenchimento(el) == "F3F4F6"
        and usa_consolas(el)
    )


def paragrafos(path: pathlib.Path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")

    root = ET.fromstring(xml)
    body = root.find(W + "body")

    resultado = []

    if body is None:
        return resultado

    for el in body:
        if el.tag != W + "p":
            resultado.append(
                {
                    "style": "",
                    "text": "",
                    "codigo": False,
                }
            )
            continue

        resultado.append(
            {
                "style": estilo_paragrafo(el),
                "text": texto_paragrafo(el),
                "codigo": eh_codigo(el),
            }
        )

    return resultado


def encontrar_secao(paras, titulo: str) -> tuple[int, int]:
    heads = [
        i
        for i, p in enumerate(paras)
        if p["style"] == "Heading1"
    ]

    esperado = normalizar(titulo)

    candidatos = [
        i
        for i in heads
        if normalizar(paras[i]["text"]) == esperado
    ]

    if not candidatos:
        disponiveis = "\n".join(
            f"  - {paras[i]['text']!r}"
            for i in heads
        )

        raise RuntimeError(
            f"\nSeção não encontrada no manuscrito:\n"
            f"  {titulo!r}\n\n"
            f"Cabeçalhos disponíveis:\n"
            f"{disponiveis}"
        )

    inicio = candidatos[-1]

    fim = next(
        (i for i in heads if i > inicio),
        len(paras),
    )

    return inicio, fim


def blocos_da_secao(paras, inicio: int, fim: int):
    """Obtém blocos cinza e o texto que aparece antes de cada um."""

    blocos = []
    atual = []
    texto_anterior = ""
    anterior_do_bloco = ""

    for p in paras[inicio:fim]:
        text = p["text"]

        if p["codigo"]:
            if not atual:
                anterior_do_bloco = texto_anterior

            atual.append(text)

        else:
            if atual:
                blocos.append(
                    (anterior_do_bloco, atual)
                )
                atual = []

            if text.strip():
                texto_anterior = text.strip()

    if atual:
        blocos.append(
            (anterior_do_bloco, atual)
        )

    return blocos


def bloco_eh_saida(texto_anterior: str) -> bool:
    """Saídas impressas usam o mesmo visual dos blocos de código."""
    anterior = normalizar(texto_anterior)

    return (
        "a saída" in anterior
        or "a saida" in anterior
        or anterior.startswith("saída:")
        or anterior.startswith("saida:")
    )


def bloco_eh_shell(bloco: list[str]) -> bool:
    primeira = next(
        (linha for linha in bloco if linha.strip()),
        "",
    )

    return bool(SHELL.match(primeira))


def listagem(
    paras,
    titulo: str,
    nome: str,
    documento: pathlib.Path,
) -> str:

    inicio, fim = encontrar_secao(paras, titulo)

    blocos = blocos_da_secao(
        paras,
        inicio,
        fim,
    )

    codigo = []

    for anterior, bloco in blocos:

        # O livro usa o mesmo quadro cinza
        # para mostrar a saída dos programas.
        if bloco_eh_saida(anterior):
            continue

        # Ignora comandos de instalação/terminal.
        if bloco_eh_shell(bloco):
            continue

        codigo.append("\n".join(bloco))

    corpo_codigo = "\n\n".join(codigo).strip()

    if not corpo_codigo:
        raise RuntimeError(
            f"Nenhum bloco de código encontrado em {titulo!r}"
        )

    cap = re.search(r"\d+", nome)
    numero = cap.group(0) if cap else "?"

    cabecalho = (
        f'"""Código extraído do Capítulo {numero} — '
        f'{paras[inicio]["text"]}.\n\n'
        f'Fonte: {documento.name}\n'
        f'Arquivo gerado automaticamente por '
        f'scripts/extrair_codigo.py.\n'
        f'Não edite este arquivo manualmente.\n'
        f'"""\n\n'
    )

    # __future__ precisa ficar logo depois da docstring.
    linhas = corpo_codigo.splitlines()

    futuro = [
        linha
        for linha in linhas
        if linha.startswith("from __future__")
    ]

    if futuro:
        linhas = [
            linha
            for linha in linhas
            if not linha.startswith("from __future__")
        ]

        cabecalho += futuro[0] + "\n\n"

    return (
        cabecalho
        + "\n".join(linhas).strip()
        + "\n"
    )


def corpo(texto: str) -> str:
    """Ignora a docstring gerada na comparação."""

    if not texto.startswith('"""'):
        return texto.strip()

    partes = texto.split('"""', 2)

    if len(partes) < 3:
        return texto.strip()

    return partes[2].strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="não altera arquivos; apenas verifica divergências",
    )
    args = parser.parse_args()

    doc = manuscrito()

    if doc is None:
        print(
            "manuscrito não encontrado em manuscrito/ "
            "— verificação ignorada"
        )
        return 0

    print(f"manuscrito: {doc.relative_to(ROOT)}")

    paras = paragrafos(doc)

    PASTA_SAIDA.mkdir(
        parents=True,
        exist_ok=True,
    )

    divergentes = []

    for nome, titulo in CAPITULOS.items():
        novo = listagem(
            paras,
            titulo,
            nome,
            doc,
        )

        destino = PASTA_SAIDA / f"{nome}.py"

        atual = (
            destino.read_text(encoding="utf-8")
            if destino.exists()
            else ""
        )

        if corpo(atual) == corpo(novo):
            print(f"OK  {nome}")
            continue

        divergentes.append(nome)

        if args.check:
            print(f"DIF {nome}")
        else:
            destino.write_text(
                novo,
                encoding="utf-8",
            )
            print(f"GRV {nome}")

    if args.check and divergentes:
        print(
            "\nDivergem do manuscrito:",
            ", ".join(divergentes),
        )
        return 1

    if args.check:
        print("\nTodos os códigos estão sincronizados.")
    elif divergentes:
        print(
            "\nRegravados:",
            ", ".join(divergentes),
        )
    else:
        print("\nNenhuma alteração.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
