# Revisão técnica — Partes VI a XVII (manuscrito v24 → v26)

Revisão capítulo a capítulo, com código extraído do manuscrito e executado,
afirmações datadas conferidas na web e referências normalizadas.

## Correções de código

| Cap. | Problema | Correção |
|---|---|---|
| 51 | `human_input` persistia no estado: uma segunda aprovação herdava a primeira | Engine descarta a decisão após o node que a recebeu; novo teste `test_human_input_is_single_use` |
| 51 | Esgotamento de retry gravava erro como string | Erro estruturado (`type`, `message`) |
| 60 | Faltavam imports e a classe `MultiAgentRuntime` (`__init__`, `start`, `_authorize_edge`, `_consume_hop`) | Código escrito; 8 testes passam |
| 69 | `resultType: "result"` | `"complete"`, conforme MCP 2026-07-28 |
| 78 | Teste usava caminho fixo `/mnt/data`; `reap_expired()` sem retorno | Diretório temporário; `return cur.rowcount` |
| 105 | Métrica local `gen_ai.execute_tool.duration` no namespace reservado | `agent.tool.duration` |
| 144 | `RunStatus` com COMPLETED/FAILED | SUCCESS/FAILURE (máquina canônica) |

## Atualizações de fato (conferidas em set. 2026)

- MCP 2026-07-28: `server/discover` obrigatório no server, `subscriptions/listen`, deprecações por 12 meses (SEP-2577).
- A2A 1.0: estados como enums `TASK_STATE_*`, fim do discriminador `kind`.
- ADK Python 2.9.0: reexecução de node falho como breaking change; grafos em YAML, failover de modelo, MCP SDK 2.x.
- Microsoft Agent Framework: API funcional experimental, só Python.
- SWE-bench Verified abandonado pela OpenAI (23/02/2026); recomendação do SWE-bench Pro.
- OpenAI Evals: somente leitura em 31/10/2026, encerramento em 30/11/2026.
- OWASP: LLM Top 10 2026 (03/08/2026, Excessive Agency em 3º); Agent Control Standard v0.1.
- AI Act: Digital Omnibus (JO de 24/07/2026) adia alto risco para 02/12/2027 e 02/08/2028.
- AP2 doado à FIDO Alliance (abr. 2026), v0.2 "Human Not Present", Verifiable Intent, UCP.
- HiddenBench (30,1% vs. 80,7%), CooperBench (COLM 2026), GKE Agent Sandbox, Agent Executor.

## Editorial

- Notas do processo editorial que vazaram para o texto (caps. 105, 114, 125, 135, 144) reescritas para o leitor.
- Projetos 2, 3 e 4: estados de domínio mapeados para a máquina canônica da Parte II.
- Contagens corrigidas (caps. 51, 52, 133), anglicismos e regência ("pela Anthropic"), "Este capítulo" no lugar de "O projeto final".
- Referências: duplicatas removidas, faltantes incluídas (DMN 1.5, CooperBench, CaMeL, Beurer-Kellner, Digital Omnibus, FIDO), Partes IX–XVII em ordem alfabética.
