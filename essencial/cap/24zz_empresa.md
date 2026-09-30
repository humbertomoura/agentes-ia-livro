@PART VII|Produção e futuro|Por onde começar na sua empresa, o caminho do protótipo ao sistema que aguenta o dia a dia, a escolha de framework e de modelo, um projeto final com a padaria inteira e um olhar para o que vem por aí.

@CHAPTER CAPÍTULO 24|Por onde começar e como chegar à produção|Escolher o primeiro caso, fazer as contas e ligar o agente sem se queimar

Quando a Dona Cida decidiu que queria "um agente de IA", a primeira ideia foi ambiciosa: um agente que cuidasse de tudo, do WhatsApp ao estoque, das compras às redes sociais. O Rafa sugeriu outra coisa: começar pelas perguntas de horário e cardápio, que tomavam uma hora por dia da Júlia. Três meses depois, o agente respondia essas perguntas sozinho, a Júlia tinha uma hora a mais para o balcão, e a Dona Cida já sabia o que funcionava e o que não funcionava. Só então vieram as encomendas.

Este capítulo é para quem precisa decidir: gestores, donos de negócio, quem vai defender o projeto numa reunião. Ele junta o que o livro ensinou num roteiro para o primeiro passo.

## Comece pelo problema, não pela tecnologia

A pergunta errada é "onde dá para usar agentes?". A certa é "que trabalho repetitivo, frequente e bem delimitado está custando caro hoje?". Um bom primeiro caso costuma ter cinco características.

@TABLE
Característica | Por que importa | Na padaria
Volume alto | O ganho aparece rápido | Dezenas de perguntas de horário por dia
Assunto delimitado | Fica fácil testar e explicar | Horário, cardápio, preços
Erro barato e reversível | O aprendizado não custa caro | Uma resposta errada se corrige na hora
Dados disponíveis | O agente tem de onde tirar as respostas | Cardápio e horários já escritos
Alguém para medir | Sem dono, ninguém sabe se melhorou | A Júlia sabe quanto tempo gastava
@END

Casos com erro caro e irreversível, como pagamentos, decisões sobre pessoas ou qualquer coisa regulada, podem vir depois, quando a equipe já tiver aprendido a avaliar, observar e conter o agente.

@BOX PEGADINHA|O projeto-vitrine
O primeiro projeto costuma ser escolhido para impressionar a diretoria: o agente que faz tudo, apresentado num evento. Esse projeto quase sempre atrasa, custa mais e termina como demonstração. Um primeiro projeto pequeno que funciona de verdade ensina mais e convence mais do que um grande que ninguém usa.
@END

## Agente, workflow ou nada disso?

Antes de qualquer orçamento, volte ao capítulo 3. Muitas tarefas que chegam como "precisamos de um agente" se resolvem com um formulário melhor, uma automação simples ou um workflow sem IA. O agente se justifica quando o caminho depende do que for encontrado: mensagens em linguagem livre, casos que variam, informação espalhada. Se a tarefa cabe numa regra, escreva a regra.

## Fazendo as contas

O retorno de um agente vem, em geral, de três lugares: tempo de pessoas liberado para trabalho de mais valor, atendimento mais rápido (menos clientes desistindo) e trabalho que antes não era feito, como responder de madrugada. O custo também tem três partes, e a primeira costuma ser esquecida.

@TABLE
Custo | O que inclui | Na padaria
Construção | Desenvolvimento, integrações, conjunto de avaliação | Algumas semanas do Rafa
Operação | Uso do modelo por conversa, infraestrutura, ferramentas | Centavos por conversa, somados no mês
Supervisão | Pessoas revisando, aprovando, corrigindo e melhorando | Parte do tempo da Júlia e da Dona Cida
@END

Uma conta simples ajuda a decidir. A Júlia gastava uma hora por dia com perguntas de horário e cardápio. Se o agente resolve 80% delas, sobram 48 minutos por dia, cerca de 20 horas por mês. Do outro lado, o custo do modelo para 1.500 conversas no mês, mais o tempo de supervisão. Para o custo do modelo, a conta é esta: conversas por mês × tokens lidos e escritos por conversa × preço por token × câmbio. Um exemplo com números redondos, só para mostrar o cálculo: cada conversa dá cerca de quatro voltas; em cada volta, o modelo lê uns 3.000 tokens (instruções, histórico e resultados) e escreve uns 200. São 12.000 tokens lidos e 800 escritos por conversa. Com um modelo que cobre US$ 1 por milhão de tokens lidos e US$ 5 por milhão escritos, cada conversa custa US$ 0,016, cerca de R$ 0,09 com o dólar a R$ 5,50. As 1.500 conversas do mês ficam perto de R$ 130. Troque pelos preços e pelo câmbio do dia: modelos maiores podem custar várias vezes isso, e modelos pequenos, bem menos. O cache de prompt, que reaproveita o começo fixo das instruções, costuma baratear a parte lida.

Se a conta fechar com folga mesmo com estimativas pessimistas, vale testar. Se só fechar com estimativas otimistas, repense o caso.

@BOX DICA|Meça antes de ligar
Antes de colocar o agente no ar, meça como o trabalho é feito hoje: quantas mensagens por dia, quanto tempo cada uma leva, quantas ficam sem resposta, quantos erros acontecem. Sem esse retrato do antes, qualquer resultado depois vira opinião.
@END

## Comprar ou construir?

Existem três caminhos, e nenhum é sempre o melhor.

**Comprar pronto.** Plataformas de atendimento e de produtividade já trazem agentes configuráveis. É o caminho mais rápido e costuma ser o certo para casos comuns, como atendimento de dúvidas. O preço é menos controle sobre as regras, os dados e a evolução.

**Montar sobre uma plataforma.** Usar um framework ou os serviços de agentes dos grandes fornecedores (capítulo 25) para construir algo próprio, com as regras da empresa. Dá mais controle e exige alguém técnico na equipe.

**Construir do zero.** Faz sentido quando o agente é o coração do negócio ou quando as exigências de dados e regulação não cabem em nada pronto.

Em qualquer caminho, as perguntas do livro servem como checklist de compra: o que o agente decide sozinho? O que acontece quando erra? Onde ficam os dados? Dá para ver o que ele fez em cada conversa? Dá para desligar? Um fornecedor que não sabe responder a essas perguntas está vendendo uma demonstração.

## Como saber se deu certo

Combine, antes de começar, o que vai contar como sucesso, com números. Para o agente da padaria, foram quatro: porcentagem de perguntas resolvidas sem a Júlia, tempo até a primeira resposta, número de respostas erradas por semana (conferidas por amostragem) e satisfação das clientes numa pergunta simples no fim do atendimento. O agente passou para a fase seguinte, as encomendas, só quando os quatro números ficaram bons por um mês inteiro.

## E as pessoas?

"O agente vai substituir a Júlia?" é a pergunta que todo mundo faz e quase ninguém responde em voz alta. Na padaria, a resposta foi não: a Júlia deixou de responder "que horas abre?" e passou a cuidar das encomendas grandes, das clientes que querem conversar e da supervisão do próprio agente. Mas essa não é uma resposta automática. Em muitas empresas, agentes vão mudar funções, e algumas tarefas vão desaparecer.

O que o livro pode dizer é isto: os agentes que funcionam bem hoje precisam de pessoas que os supervisionem, corrijam e melhorem. Envolver desde o começo quem faz o trabalho, e que conhece os casos difíceis, deixa o agente melhor e a mudança mais justa. Esconder o projeto da equipe costuma produzir o pior dos dois mundos: um agente pior e uma equipe desconfiada.


## Do protótipo à produção

Escolhido o caso e feita a conta, começa a outra metade do trabalho. Fazer um bolo lindo para a família no domingo é uma coisa. Fazer cinquenta bolos iguais por dia, todos os dias, com a cozinha funcionando mesmo quando o forneiro falta e o gás acaba, é outra. A receita é a mesma. O que muda é tudo em volta: organização, estoque, plano B, controle de qualidade.

Com agentes acontece o mesmo. O protótipo que funcionou na tela do Rafa, com três conversas de teste, é a receita do domingo. A produção é a padaria em dia de movimento.

## O que o protótipo não mostra

Um protótipo costuma rodar com uma pessoa, uma conversa de cada vez, dados de teste e alguém olhando cada resposta. Em produção, tudo isso some. Muitas conversas acontecem ao mesmo tempo; os sistemas externos ficam lentos ou fora do ar; o fornecedor do modelo impõe limites de uso; as clientes escrevem coisas que ninguém previu; e ninguém está olhando cada resposta.

@TABLE
No protótipo | Em produção | O que precisa existir
Uma conversa por vez | Dezenas ao mesmo tempo | Fila, limites por cliente e por ferramenta
Tudo responde rápido | Sistemas lentos e fora do ar | Tempo limite, novas tentativas, plano B
Estado na memória do programa | Servidor reinicia no meio da tarefa | Estado salvo e retomada (capítulo 12)
Custo irrelevante | Conta do mês chega | Orçamento por conversa e acompanhamento (capítulo 21)
Alguém olha tudo | Ninguém olha tudo | Avaliação, alarmes e portões (capítulo 21)
Um desenvolvedor usa | Clientes de verdade usam | Identidade, permissões e LGPD (capítulo 23)
@END

## Filas e freio de mão coletivo

Na sexta-feira à tarde, véspera de fim de semana, chegam oitenta mensagens em meia hora. Se o sistema tentar atender todas ao mesmo tempo, estoura o limite de uso do fornecedor do modelo, a agenda do forno fica lenta e todo mundo recebe erro. O jeito certo é o da fila do banco: as conversas entram numa **fila**, e um número controlado de atendimentos acontece ao mesmo tempo.

Quando a fila cresce demais, o sistema precisa se defender antes de cair, e isso tem nome: **contrapressão** (*backpressure*). Ele pode avisar "estamos com muitas mensagens, respondemos em alguns minutos", dar prioridade a quem já está no meio de uma encomenda ou adiar tarefas que podem esperar, como o resumo do dia. O que ele não pode fazer é aceitar tudo e falhar com todo mundo.

@BOX DICA|Limite por ferramenta, não só pelo total
A agenda do forno aguenta poucas consultas por segundo; a busca de preços, muitas. Cada ferramenta deve declarar quanto aguenta, e o sistema respeita esse limite mesmo que o total de conversas esteja baixo. Um único cliente insistente também não pode ocupar todos os atendimentos.
@END

## Tempo e dinheiro

Duas contas decidem se um agente em produção se paga.

**Tempo de resposta.** Quem manda mensagem no WhatsApp espera resposta em segundos. Agentes que dão várias voltas no ciclo demoram. Ajuda mostrar o progresso (capítulo 17), usar um modelo menor e mais rápido para tarefas simples, como classificar a mensagem, e deixar o modelo maior para o que exige raciocínio.

**Custo.** Cada volta relê o contexto. Os truques do capítulo 9 (bancada enxuta, começo fixo para aproveitar o cache, resumo do que é antigo) são, em produção, economia direta. Vale também colocar um teto por conversa: passou do teto, o agente encerra com o estado Limite atingido e chama uma pessoa, em vez de continuar gastando.

## Onde o agente executa: a área isolada

Agentes que rodam código, instalam pacotes, baixam arquivos ou usam o navegador precisam de um lugar próprio para trabalhar, separado do resto dos sistemas. É a **área isolada** (*sandbox*), que apareceu nos capítulos 7 e 18. Em produção, ela deixa de ser detalhe e vira projeto, com perguntas que precisam de resposta antes de ligar o agente:

@TABLE
Pergunta | Resposta segura | Por que importa
Que arquivos ele enxerga? | Só a pasta da tarefa, nunca o disco inteiro | Um erro ou um golpe não alcança o resto
Para onde ele pode se conectar? | Só uma lista de endereços permitidos | Bloqueia envio de dados para fora
Que senhas ele tem? | Nenhuma no ambiente; o sistema usa as credenciais por ele, na hora | O modelo nunca lê um segredo
Código gerado roda onde? | Num contêiner descartável, sem acesso à rede interna | Código errado ou malicioso morre ali
Arquivos baixados são confiáveis? | Não: são conteúdo de fora, tratados como dados | Um PDF pode trazer instruções escondidas
Pacotes podem ser instalados? | Só de fontes e versões aprovadas | Pacote falso é um golpe comum
Quanto recurso pode gastar? | Limites de CPU, memória, disco e tempo | Um laço infinito não derruba o servidor
Usuários diferentes compartilham? | Nunca: uma área por tarefa ou por cliente | Dados de um não vazam para o outro
@END

Os grandes fornecedores oferecem áreas isoladas prontas, e ferramentas de contêiner resolvem boa parte do resto. O importante é que a resposta a cada linha da tabela seja uma configuração do sistema, e não uma instrução no prompt pedindo ao modelo que "não mexa em nada".

## O checklist de prontidão

Antes de ligar o agente para as clientes, a padaria passou por uma lista curta. Cada item foi respondido com um "sim, e aqui está a prova":

- o conjunto de avaliação roda e os casos obrigatórios passam (capítulo 21);
- cada ferramenta tem nível de risco, e as de risco alto exigem aprovação (capítulo 7);
- o estado das tarefas longas sobrevive a uma reinicialização (capítulo 12);
- existem traces, indicadores com metas e alarmes (capítulo 21);
- as credenciais são as mínimas, e nenhuma aparece para o modelo (capítulo 23);
- código gerado e navegação rodam em área isolada, com rede e arquivos restritos;
- existe um jeito fácil de a cliente falar com uma pessoa;
- existe um botão de desligar, e a Dona Cida sabe onde fica.

## Ligar aos poucos

Mesmo com tudo pronto, ninguém liga o agente para todas as clientes no primeiro dia. Uma estratégia comum é começar no modo **sombra**: o agente prepara as respostas, mas uma pessoa confere e envia. Depois, ele passa a atender sozinho uma pequena parte das conversas, por exemplo só as dúvidas de horário e preço. Só então ganha as encomendas, e bem depois os pagamentos. Cada passo dura o suficiente para os números mostrarem que está tudo bem.

@IMG /home/claude/ess/figs/f28_1.png|24.1|Ligar aos poucos: cada fase dá ao agente um pouco mais de autonomia.

@BOX NA VIDA REAL|Duas semanas no modo sombra
Nas duas primeiras semanas, o agente da padaria só escrevia rascunhos, e a Júlia enviava. Ela corrigiu 14 de 600 respostas. Dez eram questão de tom; quatro eram erros de verdade, e viraram casos de avaliação. Na terceira semana, o agente passou a responder sozinho perguntas de horário e cardápio. As encomendas vieram um mês depois.
@END

@RESUMO
Comece por um trabalho repetitivo, frequente, delimitado, com erro barato e alguém para medir.
Antes de orçar um agente, confira se um formulário, uma automação ou um workflow não resolvem.
A conta tem retorno (tempo, rapidez, trabalho novo) e três custos: construção, operação e supervisão.
Comprar, montar sobre uma plataforma ou construir: as perguntas do livro servem de checklist em qualquer caminho.
Meça o antes, combine os números do sucesso e envolva quem faz o trabalho desde o começo.
Produção muda tudo em volta do agente: volume, falhas, custo, falta de supervisão e usuários reais.
Filas e contrapressão protegem o sistema nos picos; cada ferramenta declara quanto aguenta.
Tempo de resposta e custo por conversa são contas de sobrevivência; tetos por conversa evitam surpresas.
O checklist de prontidão exige prova para cada item, inclusive um botão de desligar.
Ligar aos poucos, começando pelo modo sombra, deixa os números mostrarem quando é seguro avançar.
@END

@MAO
Escolha três tarefas da sua empresa ou do seu trabalho e dê uma nota de 1 a 5 para cada uma nas cinco características do primeiro caso. Para a melhor colocada, faça a conta de retorno e custo com números aproximados e escreva os quatro indicadores que diriam se o projeto deu certo.

Depois, monte o plano de lançamento desse mesmo agente. Divida em pelo menos quatro fases, do modo sombra ao atendimento completo, e diga, para cada fase, que tipo de conversa o agente atende e qual número precisa estar bom para passar à fase seguinte.
@END
