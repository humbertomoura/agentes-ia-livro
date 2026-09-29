# Pendências — versão técnica

Atualizado após a revisão técnica completa (manuscrito v26, set. 2026).

## Verificações de fato ainda em aberto

| Capítulo | Afirmação | O que falta |
|---|---|---|
| 59 | Autoria do CoCoBench citada como "Chen et al., 2026" | Confirmar autores na fonte primária |
| 65–66 | A2A 1.0 lançado em 12/03/2026; entrada na AAIF em 27/08/2026 | Confirmar as duas datas |
| 82 | OpenAI recomenda começar por code mode em computer use | Confirmar na documentação atual (o nome "GPT-6 Astra" foi retirado do box) |

## Código

| Capítulo | Situação |
|---|---|
| 15 | Seções 15.5, 15.6 e 15.9 são fragmentos sem contexto de execução autônomo |
| 33 | O teste `test_cumulative_compaction` usa a fixture `fake_client`, definida só em `tests/conftest.py`; falta uma definição curta no livro ou remissão ao repositório |
| 44 | Trechos 44.1 e 44.3 são fragmentos; rodam contra stubs em `tests/test_tecnico_cap44_sequencia_routing.py` |

## Resolvidas nesta rodada

- Cap. 77/127: a "OpenAI Agents API com harness gerenciado" existe (harness do Codex gerenciado pela OpenAI) — confirmado.
- Cap. 60: classe `MultiAgentRuntime` e imports faltavam no livro — escritos; 8 testes passam.
- Cap. 51: `human_input` reaproveitado aprovava uma segunda aprovação — corrigido; teste novo.
- Cap. 78: teste com caminho fixo `/mnt/data` — corrigido.
