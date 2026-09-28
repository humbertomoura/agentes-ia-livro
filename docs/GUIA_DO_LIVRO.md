# Guia do livro — Agentes de Inteligência Artificial

Documento de referência para manter a consistência entre partes, versões e conversas de revisão. Anexe este arquivo e o docx mais recente a cada nova rodada de revisão.

## 1. Versões e públicos

| | Versão técnica | Versão comercial |
|---|---|---|
| Título de trabalho | *Agentes de Inteligência Artificial: Fundamentos, Arquiteturas, Protocolos e Sistemas Agênticos em Produção* | *Agentes de Inteligência Artificial: um guia descomplicado para entender e construir agentes de IA, com exemplos do dia a dia* |
| Público | Graduação, pós, profissionais de TI | Brasileiros curiosos, estudantes, gestores, devs iniciantes |
| Tom | Acadêmico-técnico | Conversado, "você", sem jargão desnecessário |
| Código | Inglês (identificadores, comentários, traces) | Português |
| Formato | Livro-texto | Ebook KDP (e impresso 6×9) |

## 2. Processo

1. O autor escreve a parte técnica.
2. Revisão em lotes de 2 a 3 partes: leitura completa, execução de todo o código, casos de borda, conferência de referências e de atualidade.
3. Correções aplicadas diretamente no docx (nova versão numerada: v11, v12...).
4. Código novo entra neste repositório com testes; a suíte inteira roda a cada lote.
5. Com a versão técnica completa: passada global de consistência e curadoria da versão comercial.

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
- Analogias já usadas (não repetir com outro sentido): bancada = contexto; comanda = estado; caderno = memória; câmera = histórico/logs; cardápio = catálogo de ferramentas; garçom/gerente/cozinha = modelo/controlador/executor; farmácia = três conferências; botão do elevador = idempotência; prova com consulta = RAG; triagem e entrevista = retrieval e reranking.

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
