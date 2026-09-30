# Guia do livro — Agentes de Inteligência Artificial

Documento de referência para manter a consistência entre partes, versões e conversas de revisão. Anexe este arquivo e o docx mais recente a cada nova rodada de revisão.

## 1. Versões e públicos

| | Versão técnica | Versão comercial |
|---|---|---|
| Título de trabalho | *Agentes de Inteligência Artificial: Fundamentos, Arquiteturas, Protocolos e Sistemas Agênticos em Produção* | *Agentes de Inteligência Artificial: um guia prático para entender, construir e colocar agentes de IA em produção* |
| Público | Graduação, pós, profissionais de TI | Brasileiros curiosos, estudantes, gestores, devs iniciantes |
| Tom | Acadêmico-técnico | Conversado, "você", sem jargão desnecessário |
| Código | Inglês (identificadores, comentários, traces) | Português |
| Formato | Livro-texto | Ebook KDP (e impresso 6×9) |
| Tamanho | 17 partes, 153 capítulos | Volume único essencial: 7 partes, 27 capítulos, 2 apêndices, cerca de 306 páginas, 26 figuras; inclui "Sobre esta edição" e "Sobre o autor" |
| Arquivo atual | `Agentes_IA_v26.docx` | `Agentes_IA_Essencial_v1.docx` |

## 2. Processo

1. O autor escreve a parte técnica.
2. Revisão em lotes de 2 a 3 partes: leitura completa, execução de todo o código, casos de borda, conferência de referências e de atualidade.
3. Correções aplicadas diretamente no docx (nova versão numerada: v11, v12...).
4. Código novo entra neste repositório com testes; a suíte inteira roda a cada lote.
5. Com a versão técnica completa: passada global de consistência e curadoria da versão comercial.
6. Versão comercial: um único volume essencial (decisão de set. 2026), escrito capítulo a capítulo, salvando o docx após cada capítulo.

## 3. Formato do capítulo (técnico)

- Rótulo `CAPÍTULO N` (parágrafo com quebra de página), título em Heading 1, subtítulo de uma linha.
- Caixa "Objetivos de aprendizagem".
- Seções numeradas `N.M` em Heading 2.
- Caixas de destaque num único estilo visual (título em negrito + corpo). Tipos usados: Princípio, Regra de projeto, Definição, Heurística, Estado atual — mês de ano.
- Fechamento: Síntese do capítulo (lista), Questões de revisão (4–5), Exercício de aplicação.
- Cada parte abre com texto de apresentação, "Mapa da Parte" (tabela capítulo × pergunta central) e caixa de princípio; fecha com Encerramento e Referências da parte (ABNT, ordem alfabética).
- Linhas de tabela não quebram entre páginas; títulos presos ao parágrafo seguinte.

## 4. Formato do capítulo (comercial)

- Abertura com uma cena do cotidiano; subtítulo curto.
- Caixas: **Na vida real**, **Pegadinha**, **Dica**, **Anote aí**, **Resumo rápido** (fim do capítulo), **Mão na massa** (fim do capítulo).
- Tabelas com no máximo 3 colunas. Linhas de código com no máximo 58 caracteres.
- Figuras próprias (paleta: verde-petróleo `#0E7C7B`, laranja `#E07A1F`, fundos claros), com legenda numerada.
- Cada parte fecha com texto de encerramento, glossário e "Para ir além".
- Estilo de escrita: frases de tamanho variado, sem travessão antes de "revelações", sem "além disso"/"vale destacar", sem listas de três por hábito, títulos em caixa de frase, aspas retas.

## 5. Personagens e analogias (comercial)

- **Dona Cida:** dona da padaria; o fio condutor do livro.
- **Dona Lurdes:** cliente fiel; prefere bolo sem lactose; retira às 9h.
- **Seu Antônio:** cliente; retira às 7h.
- **Júlia:** funcionária nova (capacidade × autoridade × autonomia).
- **Seu Zé:** forneiro da padaria (essencial, Parte III: passagem de bastão).
- Analogias já usadas (não repetir com outro sentido): bancada = contexto; comanda = estado; caderno = memória; câmera = histórico/logs; cardápio = catálogo de ferramentas; garçom/gerente/cozinha = modelo/controlador/executor; farmácia = três conferências; botão do elevador = idempotência; prova com consulta = RAG; triagem e entrevista = retrieval e reranking; checklist do piloto = workflow; save do videogame = checkpoint; tomada padrão de três pinos = MCP; vendedor do moinho = agente externo (A2A); acompanhamento do pedido no app de delivery = AG-UI; telefone sem fio = perda de informação entre agentes.

## 6. Decisões técnicas canônicas

- **O modelo propõe; o sistema decide.** Regras críticas vivem fora do modelo.
- **Contexto, estado e memória** são coisas diferentes (Parte IV).
- **Máquina de estados canônica (Parte II):** READY, RUNNING, BLOCKED, PAUSED, SUCCESS, FAILURE, LIMIT_REACHED, CANCELLED. Na comercial: Pronto, Em andamento, Bloqueado, Pausado, Sucesso, Falha, Limite atingido, Cancelado.
- **Loop canônico:** tool calling nativo; término natural quando o modelo não pede ferramentas; sucesso só após verificação do controlador; validação nunca derruba o processo.
- **Ferramentas:** registro com validador, timeout, perfil de leitura, aprovação e chave de intenção; aprovação **por chamada**; idempotência pela **intenção**, nunca pelo `call_id`; identidade vem da sessão.
- **Memória:** portões de escrita e leitura; chave de assunto; supersessão com histórico; validade; resumo acumulado; nada vira política.
- **RAG:** filtro de acesso antes de qualquer pontuação (inclusive estatísticas do BM25); abstenção quando não há sinal; citações verificadas.
- **Modelo de referência nos exemplos:** OpenAI Responses API, `OPENAI_MODEL` com padrão `gpt-6-astra` (verificar a cada edição). Conceitos sempre neutros em relação ao fornecedor.
- **LGPD:** citar arts. 5º II, 6º, 11 e 18 quando houver dados pessoais; exclusão alcança cópias derivadas (resumos, índices, embeddings).

## 7. Checklist de revisão por lote

- [ ] Todo código roda; testes cobrem o que o texto afirma (inclusive casos negativos).
- [ ] Referências completas, citadas no texto e ordenadas; nada atribuído de forma vaga.
- [ ] Afirmações sobre produtos e APIs conferidas na data; caixas "Estado atual" atualizadas.
- [ ] Consistência com as decisões da seção 6 e com as partes anteriores (remissões corretas).
- [ ] Formato da seção 3; tabelas e diagramas legíveis em tela pequena.
- [ ] Pendências anotadas em `docs/PENDENCIAS.md`.

## 8. Versão comercial essencial

Decisão de setembro de 2026: em vez de converter as 17 partes técnicas, a versão comercial é um volume único de 330 a 360 páginas. As Partes I–V do comercial v1 (271 p.) foram condensadas para cerca de 140 páginas; as Partes VI–XVII da técnica viram 17 capítulos novos, e três capítulos foram escritos só para o essencial (19, 20 e a primeira metade do 24).

| Parte | Capítulos | Origem |
|---|---|---|
| I Entendendo agentes | 1–5 | comercial v1, caps. 1–15 |
| II Mãos, memória e conhecimento | 6–11 | comercial v1, caps. 16–42 |
| III Processos e equipes | 12–14 | técnica VI e VII |
| IV Conectando tudo | 15–17 | técnica VIII |
| V Agentes no trabalho | 18–20 | técnica X; 19 (WhatsApp e voz) e 20 (saúde, educação, serviço público) escritos para o essencial |
| VI Confiança | 21–23 | técnica XI, XII e XIII |
| VII Produção e futuro | 24–27, apêndices A e B, glossário | 24 inclui "por onde começar na empresa" (novo); técnica IX, XIV–XVII; modelos abertos no 25 |

- Um glossário só, no fim do livro; os fechamentos de parte trazem encerramento e "Para ir além", sem glossário próprio.
- Cinco capítulos "Mão na massa" (5 atendente, 8 encomendas com aprovação, 11 respostas com fonte, 13 encomenda do casamento, 26 projeto final) e mensagens JSON de MCP no 15. Código em `comercial/`, com testes e saída idêntica à impressa.
- Saíram do texto (continuam no repositório): código do ar-condicionado e do caderno de memória; tipos clássicos de agente, BDI e PEAS; detalhes de runtime, filas e multi-region; comparação detalhada de frameworks.
- Fio narrativo: a padaria cresce (encomendas grandes com aprovação, equipe de agentes, fornecedores conectados por protocolo, tentativa de golpe, sistema completo no projeto final).
- Geração do docx: `essencial/build.py` e `make.py`; cada capítulo é um arquivo de marcação em `essencial/cap/`. `@KEEP` reaproveita elementos do comercial v1 sem alteração; `@SUB` ajusta remissões dentro deles; figuras reaproveitadas são renumeradas com `@FIG`.
- Estados: Bloqueado = esperando algo de fora (aprovação, pagamento, resposta); Pausado = parada decidida por alguém (caps. 4, 8, 12, 13).
- Tamanho dos capítulos: nenhum abaixo de ~8 páginas; capítulos muito curtos foram fundidos (equipes, agentes especializados, avaliação+observabilidade, começar+produção).
- Kindle: caixas são parágrafos com borda e fundo (não tabelas); sumário com links para os capítulos; primeira linha das tabelas marcada como cabeçalho; texto alternativo das figuras igual à legenda. Tudo isso é feito automaticamente por `postprocess()` em `build.py`.
- Datas: fatos de plataforma são conferidos na data registrada na página "Sobre esta edição"; evitar "em setembro de 2026" espalhado no texto (exceto em quadros que precisam de data própria, como o da disputa Meta × CADE).
- Figuras novas: `essencial/figs/make_figs.py` (matplotlib, paleta do guia), inseridas com `@IMG caminho|n.m|legenda`.
- Repositório: github.com/humbertomoura/agentes-ia-livro — código sob licença MIT (LICENSE-CODE); texto e figuras com direitos reservados. Mantém README, ERRATA.md e CHANGELOG.md. (citado no "Antes de começar", no apêndice A e na página da edição).
- Toda remissão aponta para a numeração nova (conferir com a varredura de "capítulo N" e "Parte N" a cada capítulo).
