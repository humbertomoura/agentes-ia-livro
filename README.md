# Agentes de Inteligência Artificial — código do livro

Este repositório traz todo o código dos livros **Agentes de Inteligência Artificial**
(edição comercial) e da versão técnica em preparação, com testes automáticos.

## Rodar em três minutos

    git clone https://github.com/humbertomoura/agentes-ia-livro
    cd agentes-ia-livro
    python -m pip install pytest
    cd comercial/cap13_encomenda_casamento && python demo.py

Nenhum exemplo precisa de chave de API, conta em fornecedor ou internet: todos usam um
modelo simulado. Python 3.10 ou mais novo.

## O que tem aqui

| Pasta | Conteúdo |
|---|---|
| `comercial/cap13_encomenda_casamento` | Workflow durável com aprovação, retomada e compensação |
| `comercial/cap30_projeto_final` | Projeto final: ferramentas, memória, RAG, portões e trilha |
| `tecnico/` | Listagens dos capítulos de implementação da versão técnica |
| `tests/` | Testes de todas as listagens |
| `essencial/` | Fonte do manuscrito comercial e gerador do docx |
| `docs/` | Guia do livro, revisão técnica e pendências |
| `manuscrito/` | Versões do manuscrito |

## Testes

    pytest                              # toda a versão técnica
    ./tests_comercial_novos.sh          # os exemplos do livro comercial

Os testes conferem, entre outras coisas, que a saída impressa no livro é exatamente a que
o código produz. Se um exemplo do livro não bater com o repositório, é erro nosso: abra uma
issue.

## Licença

O **código** deste repositório está sob a licença MIT (veja `LICENSE-CODE`): use, copie,
modifique e distribua à vontade, inclusive em projetos comerciais.

O **texto, as figuras e o conteúdo dos livros** não estão cobertos por essa licença. São
© 2026 Humberto Jorge de Moura Costa, todos os direitos reservados.

## Errata e atualizações

Correções ficam em [`ERRATA.md`](ERRATA.md) e o histórico em [`CHANGELOG.md`](CHANGELOG.md).
Capítulos sobre plataformas e protocolos envelhecem rápido; atualizações são anunciadas aqui.
