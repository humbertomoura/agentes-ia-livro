@CHAPTER  |Glossário|Os termos do livro, em ordem alfabética

Este glossário reúne os termos das sete partes. Termos em inglês aparecem entre parênteses quando é assim que você vai encontrá-los em documentação e artigos.

@TABLE
Termo | O que significa
A2A (Agent2Agent) | Protocolo aberto para agentes de sistemas diferentes conversarem e trabalharem juntos.
Abster-se | Responder que não encontrou a informação, em vez de inventar.
Ação | Algo que o agente faz e que produz efeito no ambiente.
AG-UI | Protocolo aberto que padroniza a comunicação entre agentes e interfaces, por eventos.
Agência | O quanto um sistema age por conta própria no mundo, em vez de apenas responder.
Agente | Sistema que observa um ambiente, decide com base em objetivos e regras, age e usa o resultado para decidir o próximo passo.
Agente de dados | Agente que transforma perguntas em consultas a bancos de dados e explica o resultado.
Agente de pesquisa (deep research) | Agente que planeja, busca, anota evidências e escreve um relatório com fontes.
Agente de programação | Agente que lê, edita e testa código num repositório.
Agente persistente | Agente que fica ligado por longos períodos, acompanha um assunto e age quando algo muda.
Ambiente | O "mundo" onde o agente trabalha e produz efeitos.
AP2 (Agent Payments Protocol) | Protocolo aberto para dar a agentes mandatos de pagamento verificáveis.
Aprovação por pedido | Autorização registrada por alguém de confiança para um pedido específico, verificada pelo executor.
Área isolada (sandbox) | Ambiente separado onde o agente roda código e usa arquivos, com rede e recursos limitados.
Arquivo de instruções do projeto | Arquivo com os procedimentos da equipe para o agente seguir, como o AGENTS.md.
Artefato | Resultado guardado fora da conversa, com identificador, autor e origem.
Atendimento (WhatsApp) | Trecho da conversa sobre um assunto, com começo e fim, tratado como uma sessão.
Autonomia | Quanto o agente pode decidir e agir sem intervenção humana.
Autoridade | O conjunto de ações que o agente tem permissão para executar.
Avaliação (eval) | Conjunto de casos de teste, com critérios, rodado a cada mudança no agente.
Backoff | Esperar um pouco mais a cada nova tentativa depois de um erro passageiro.
BM25 | Método clássico de busca por palavras, que valoriza termos raros e frequentes no trecho.
Busca de ferramentas | Mecanismo que encontra e carrega só as ferramentas relevantes, em vez de mostrar o catálogo inteiro.
Busca híbrida | Combinação da busca por palavras com a busca por significado.
Busca por significado | Busca que compara vetores (embeddings) e acha sentidos parecidos com palavras diferentes.
Cadeia de raciocínio (chain-of-thought) | Raciocínio intermediário que o modelo usa para chegar a uma resposta. Conforme o modelo e a API, ele pode ficar escondido; não é uma interface estável do sistema.
Caderno de evidências | Lista de fatos encontrados, cada um com fonte, data e trecho que o sustenta.
Camada semântica | Dicionário com as definições oficiais das métricas de uma empresa.
Capacidade | O que o agente consegue fazer tecnicamente.
Cartão do agente (Agent Card) | Documento em que um agente anuncia nome, habilidades, endereço e autenticação.
Chamada de ferramenta (tool calling) | Mecanismo em que o modelo devolve um pedido estruturado de ferramenta e a aplicação o executa.
Chamada programática de ferramentas | O modelo escreve um pequeno programa que chama várias ferramentas num ambiente isolado e devolve só o resultado.
Chave de idempotência | Código que representa a intenção do negócio e impede que o mesmo pedido seja executado duas vezes.
Checklist de prontidão | Lista de condições, cada uma com prova, exigida antes de ligar o agente em produção.
Checkpoint | Fotografia guardada do estado de uma tarefa para permitir a retomada.
Citação fiel | Citação cuja fonte realmente sustenta a afirmação.
Compensação | Ação nova que desfaz o efeito de uma anterior quando não há "desfazer" direto.
Contaminação | Quando as perguntas de um teste vazam para o treinamento do modelo.
Context rot | Perda de qualidade quando o contexto fica grande e ruidoso.
Contexto | A informação que o modelo vê numa decisão específica. A bancada.
Contrapressão (backpressure) | Defesa do sistema quando chega mais trabalho do que ele consegue atender.
Controlador | A parte do sistema que aplica estados, limites e portões e tem a palavra final.
Cross-encoder | Reordenador que lê pergunta e trecho juntos para dar uma nota ao par.
Deriva (drift) | Piora lenta do agente causada por mudanças no mundo, no modelo ou nas ferramentas.
Embedding (vetor) | Lista de números que representa o sentido de um texto.
Engenharia de contexto | Escolher, ordenar e resumir o que o modelo vê a cada decisão.
Envenenamento de ferramentas | Ataque em que um servidor traz ferramentas com descrições ou comportamento maliciosos.
Envenenamento de memória | Ataque que planta informação falsa ou ordens na memória para durar entre conversas.
Especialista como ferramenta | Agente consultado por outro, que continua dono da conversa.
Estado | A situação da tarefa em andamento. A comanda.
Etiquetas (metadados) | Informações sobre o trecho: origem, versão, validade e quem pode ver.
Evento | Mensagem curta que informa algo que aconteceu: texto novo, passo iniciado, estado alterado.
Excesso de agência | Risco de dar ao agente ferramentas, permissões ou autonomia além do necessário.
Executor | A parte do sistema que confere e executa os pedidos de ferramenta.
Ferramenta (tool) | Interface pela qual o agente consulta informações ou age no mundo externo.
Ficha do pedido | Registro enxuto dos fatos que importam para controlar a tarefa, separado do histórico.
Fila | Lugar onde os pedidos esperam para ser atendidos por um número controlado de execuções.
Formulário (schema) | A descrição dos campos, tipos, opções e limites de uma ferramenta.
Framework de agentes | Biblioteca que traz prontas peças como estado, retomada, esperas, traces e coordenação.
Guardrail | Mecanismo que faz valer as regras, conferindo entradas, saídas e ações.
Habilidade (skill) | Conhecimento de procedimento reutilizável que ensina o agente a resolver um tipo de tarefa.
Histórico | A sequência completa de mensagens, pedidos de ferramenta e resultados.
Host | Aplicação onde o agente vive e que decide quais servidores MCP conectar.
Idempotência | Propriedade de uma operação que, repetida com a mesma intenção, tem o mesmo efeito de uma vez só.
Injeção de instruções | Texto malicioso, lido de fora, que tenta dar ordens ao modelo.
Interface declarativa | Tela descrita pelo agente com componentes de um catálogo e desenhada pela aplicação.
Invariante | Regra que o sistema garante durante toda a execução, faça o modelo o que fizer.
Janela de contexto | O tamanho máximo de texto que cabe numa chamada ao modelo.
JSON-RPC | Formato padrão de pedido e resposta usado pelo MCP e por outros protocolos.
Mandato de pagamento | Autorização estreita, verificável e com prazo para um agente pagar em nome de alguém.
MCP (Model Context Protocol) | Protocolo aberto que liga aplicações de IA a ferramentas e dados de outros sistemas.
Memória | Informação guardada para uso em momentos ou conversas futuras. O caderno.
Memória de acontecimentos (episódica) | Lembranças do que aconteceu, quando e com que resultado.
Memória de fatos (semântica) | Fatos e preferências que podem ser atualizados.
Memória de procedimentos (procedural) | Como fazer: receitas, checklists, arquivos como AGENTS.md.
Modelo como juiz | Modelo de linguagem usado para dar nota a respostas segundo critérios escritos.
Modelo de pesos abertos | Modelo que pode ser baixado e rodado na infraestrutura de quem o usa.
Modelo de raciocínio | Modelo que pensa internamente antes de responder, inclusive entre chamadas de ferramenta.
Modelo em quarentena | Modelo sem ferramentas que lê conteúdo não confiável e devolve só dados estruturados.
Modo estrito | Recurso que obriga o modelo a preencher o formulário exatamente no formato definido.
Modo sombra | Fase em que o agente prepara as respostas e uma pessoa confere e envia.
OAuth | Padrão de autorização que permite dar acesso limitado sem entregar a senha.
Observação | O que o agente consegue ver do ambiente num dado momento.
OpenTelemetry | Padrão aberto para registrar traces, métricas e registros de software.
Orçamento | Limite de passos, tempo, tokens, custo ou ações externas.
Pacote de evidências | Os trechos escolhidos, com etiquetas estáveis (E1, E2...), entregues ao modelo.
Pacote de tarefa | Recado estruturado com objetivo, contexto, limites, orçamento e formato de retorno.
Passagem de bastão (handoff) | Transferência da conversa inteira para outro agente, que passa a ser o dono.
Plano B (fallback) | Alternativa mais simples usada quando o caminho principal falha.
Plataforma de mensagens comerciais | A WhatsApp Business Platform, usada por empresas para atender e enviar mensagens.
Política de junção | Regra que diz o que fazer com os resultados de passos feitos em paralelo.
Portão (gate) | Verificação entre o pedido do modelo e a execução.
Portão de escrita | Mecanismo que decide se algo é anotado, corrigido, riscado ou deixado para lá.
Portão de leitura | Mecanismo que filtra e escolhe quais anotações voltam para a bancada.
Portão de regressão | Conferência que barra mudanças que quebram casos obrigatórios ou pioram a média.
Primeiro caso de uso | Tarefa escolhida para começar: frequente, delimitada, com erro barato e alguém para medir.
Racionalidade | Escolher a melhor ação possível com a informação disponível.
RAG | Geração aumentada por recuperação: buscar trechos e responder com base neles.
RAG agêntico | RAG em que o agente decide se busca, onde, quantas vezes e quando parar.
ReAct | Padrão que alterna pensamento, ação e observação.
Recurso (MCP) | Informação que um servidor oferece para a aplicação ler e colocar no contexto.
Registro (registry) | Lista oficial que liga cada ferramenta à sua execução e às suas regras.
Regras | Limites impostos de fora ao agente: o que é permitido, obrigatório ou proibido.
Reordenação (reranking) | Segunda etapa, mais cuidadosa, que escolhe os melhores entre os candidatos.
Replanejamento | Mudar a estrutura do plano por causa de uma novidade, preservando o que continua valendo.
Resolução CFM nº 2.454/2026 | Norma do Conselho Federal de Medicina sobre o uso de IA na medicina, em vigor desde agosto de 2026.
Roteamento | Classificar uma entrada e mandá-la para o fluxo certo.
RRF | Fusão de listas pela posição de cada item, sem comparar as notas.
Runtime | A infraestrutura que executa o agente e cuida de sessões, falhas e isolamento.
Saga | Sequência de passos em que cada efeito tem uma compensação prevista.
Servidor MCP | Programa que oferece ferramentas, recursos e prompts de um sistema.
Sistema agêntico | Aplicação em que um ou mais agentes cuidam de decisões dentro de uma arquitetura maior.
Sistema multiagente | Sistema em que dois ou mais agentes, com papéis próprios, trabalham juntos.
SLI e SLO | Indicador de qualidade do serviço e a meta combinada para ele.
Span | Registro de uma etapa dentro de um trace.
Subagente | Agente auxiliar que trabalha com a própria bancada e devolve só um resumo.
Supervisor | Agente que divide o trabalho, chama especialistas e junta os resultados.
Tarefa (A2A) | Unidade de trabalho entre agentes, com identificador, estado e artefatos.
Trace | Registro da execução inteira de um pedido, formado por spans.
Trajetória | O caminho que o agente percorreu: ferramentas, ordem, dados e custo.
Transcrição | Conversão de áudio em texto por um modelo de reconhecimento de fala.
Trecho (chunk) | Unidade de texto que a busca encontra e que faz sentido sozinha.
Trifeta letal | Dados privados, conteúdo de fora e canal de saída juntos no mesmo agente.
Trilha (trajetória) | O registro de tudo o que o agente fez numa execução.
Uso do computador (computer use) | Agente que vê a tela e age com cliques e digitação, como uma pessoa.
Vice-delegado confuso | Quando alguém usa a permissão de outro para fazer o que não poderia.
Vigia (watchdog) | Mecanismo externo que confere prazos e sinais de vida do agente.
Workflow | Roteiro de passos, estado e regras de transição.
Workflow durável | Workflow que salva o estado a cada passo e retoma sem refazer o que já foi feito.
@END
