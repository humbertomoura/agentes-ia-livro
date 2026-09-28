# Estrutura proposta para as partes restantes

Objetivo: reduzir sobreposições e envelhecimento rápido, passando de 17 para 14 partes, mais apêndices.

| Nova | Parte | Origem na estrutura atual | Situação |
|---|---|---|---|
| I | Fundamentos | I | pronta |
| II | Agent Loop | II | pronta |
| III | Tools | III | pronta |
| IV | Contexto e Memória | IV | pronta |
| V | RAG e Agentic RAG | V | pronta |
| VI | Workflows e execução durável | VI (+ HITL e retomada de IX) | a escrever |
| VII | Sistemas multiagentes | VII | a escrever |
| VIII | Protocolos: MCP, A2A, AG-UI/A2UI | VIII | a escrever |
| IX | Runtimes, infraestrutura e system design | IX + XIV | a escrever |
| X | Agentes especializados | X | a escrever |
| XI | Avaliação e observabilidade | XI + XII | a escrever |
| XII | Segurança e governança | XIII (síntese do que já está em III–V + modelo de ameaças, identidade, regulação) | a escrever |
| XIII | Projetos integradores | XVI | a escrever |
| XIV | Fronteiras (inclui treinamento de agentes: fine-tuning e RL) | XVII | a escrever |
| Apêndice A | Frameworks e plataformas (versão curta no livro; comparações vivas no repositório) | XV | a escrever |
| Apêndice B | Prepare seu ambiente | novo | a escrever |

## Justificativas

- **Avaliação e observabilidade** medem a mesma coisa por ângulos diferentes (trajetória, custo, qualidade); separadas, repetem conceitos.
- **Runtimes e system design** tratam das mesmas peças (filas, persistência, escala, custo, deploy).
- **Segurança** já foi tratada em cada parte (ferramentas, memória, RAG); a parte dedicada vira síntese com modelo de ameaças, identidade e regulação (LGPD, EU AI Act), sem repetir.
- **Frameworks** mudam em meses; no livro ficam os critérios de escolha, e as comparações atualizáveis ficam no repositório.

## Lotes de revisão sugeridos

1. VI + VII
2. VIII + IX
3. X + XI
4. XII + XIII + XIV + apêndices
5. Passada global e curadoria comercial
