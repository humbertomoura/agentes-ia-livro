# Agentes de Inteligência Artificial — código do livro

Código-fonte, testes e guias editoriais do livro **Agentes de Inteligência Artificial**, de Humberto Jorge de Moura Costa, em duas versões:

- **Técnica** (`tecnico/`): identificadores em inglês, exemplos de engenharia (runtime de tools, memória, RAG).
- **Comercial** (`comercial/`): identificadores em português, exemplos com a padaria da Dona Cida.

Todo exemplo do livro está aqui e é testado. Na versão comercial, cada exemplo precisa imprimir **exatamente** a saída que aparece no livro.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
```

Os testes não usam chave de API nem internet. Para rodar os exemplos com um modelo de verdade:

```bash
export OPENAI_API_KEY="sua-chave"   # nunca coloque a chave no código
export OPENAI_MODEL="gpt-6-astra"   # confira o modelo recomendado na documentação
python comercial/parte2_cap15_atendente/real.py
```

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `comercial/parte1_cap08_ar_condicionado` | Agente reativo com histerese |
| `comercial/parte2_cap15_atendente` | Ciclo de tool calling (simulado e real) |
| `comercial/parte3_cap24_ferramentas` | Registro, aprovação, bloqueio e idempotência |
| `comercial/parte4_cap33_caderno` | Memória com portões, substituição e resumo acumulado |
| `comercial/parte5_cap42_pasta` | RAG híbrido, filtro de acesso, abstenção e citações |
| `tecnico/cap15_agent_loop` | Loop real (Responses API) e decisor simulado |
| `tecnico/cap24_tool_runtime` | Runtime de tools com aprovação por chamada |
| `tecnico/cap33_memory_runtime` | Runtime de contexto e memória |
| `tecnico/cap42_rag_runtime` | Runtime híbrido de RAG |
| `tests/` | Testes de todas as versões |
| `docs/` | Guia do livro, estrutura proposta e pendências |

## Situação das partes

| Parte | Técnica | Comercial |
|---|---|---|
| I — Fundamentos | revisada | pronta |
| II — Agent Loop | revisada | pronta |
| III — Tools | revisada | pronta |
| IV — Contexto e Memória | revisada | pronta |
| V — RAG | revisada (v10) | pronta |
| VI em diante | a escrever | após a curadoria final |

## Licença

O **código** deste repositório está sob a licença MIT (ver `LICENSE`). O **texto do livro** não faz parte do repositório e tem todos os direitos reservados.
