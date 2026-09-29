# Código da versão técnica

Cada arquivo de `tecnico/` é a listagem de um capítulo de implementação, extraída do
manuscrito. Os testes estão dentro da própria listagem; `tests/test_tecnico_*.py` apenas
os coleta. Nenhum teste precisa de chave de API ou de rede.

| Arquivo | Capítulo | Testes |
|---|---|---|
| (fragmentos + stubs) | 44 — Sequência, branching e routing | 8 |
| cap51_workflow_duravel.py | 51 — Workflow durável sem framework | 9 |
| cap60_runtime_multiagente.py | 60 — Runtime multiagente | 8 |
| cap69_adaptadores_protocolo.py | 69 — Adaptadores MCP/A2A/AG-UI | 8 |
| cap78_runtime_duravel.py | 78 — Runtime durável (SQLite, leases) | 9 |
| cap87_portfolio_especialistas.py | 87 — Portfólio de especialistas | 9 |
| cap96_eval_harness.py | 96 — Eval harness | 10 |
| cap105_observabilidade_otel.py | 105 — Observabilidade com OpenTelemetry | 10 |
| cap114_security_gateway.py | 114 — Camada de segurança | 12 |
| cap125_system_design_core.py | 125 — Núcleo de System Design | 11 |
| cap135_portabilidade_frameworks.py | 135 — Portabilidade entre frameworks | 11 |
| cap136_agent_loop_minimo.py | 136 — Projeto 1 | 4 |
| cap144_servico_production_grade.py | 144 — Projeto final | 13 |
| cap153_readiness_gate.py | 153 — Readiness gate | 5 |

## Sincronia com o manuscrito

    python scripts/extrair_codigo.py --check   # falha se tecnico/ divergir do docx
    python scripts/extrair_codigo.py           # regrava tecnico/ a partir do docx

O CI roda a checagem a cada push. Ao corrigir um bug, corrija no manuscrito e regenere.
