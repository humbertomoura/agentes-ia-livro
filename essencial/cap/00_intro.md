@CHAPTER  |Antes de começar|Por que este livro existe e como tirar proveito dele

Em 2023, quase ninguém fora da área de tecnologia falava em "agentes de IA". Hoje o termo aparece em anúncio de banco, em palestra de RH e em conversa de almoço de domingo. Com tanta gente usando a mesma palavra, ela passou a significar quase qualquer coisa: um chatbot de WhatsApp vira "agente", uma automação de planilha vira "agente", e fica difícil separar o que é novidade de verdade do que é marketing.

Este livro nasceu para colocar ordem nessa conversa. Quero explicar agentes de IA do jeito que explico em sala de aula: começando pelo que você já conhece do dia a dia e só depois chegando ao vocabulário técnico e ao código. E quero ir até o fim do caminho: do primeiro ciclo de um agente simples até equipes de agentes que conversam entre si, se conectam a sistemas por protocolos abertos e precisam ser testadas, vigiadas e protegidas contra golpes.

## Para quem é este livro

Este livro foi escrito principalmente para estudantes de computação, desenvolvedores e profissionais de tecnologia que querem entender e construir agentes de IA. Ele também serve a gestores técnicos, arquitetos e profissionais de inovação que precisam entender como essas soluções funcionam e quais riscos envolvem. Os capítulos de conceito quase não têm código. Os capítulos **Mão na massa** trazem programas curtos em Python, com cada linha explicada. A primeira parte dá para acompanhar sem nunca ter programado; do meio para o fim, alguma familiaridade com programação ajuda bastante. Todo o código roda sem conta, sem chave e sem internet, com um modelo simulado; quando vale a pena, mostramos também o trecho que muda para ligar um modelo de verdade.

## Escolha sua trilha

Você não precisa ler tudo na ordem. Quatro caminhos funcionam bem:

- **Quero entender:** os capítulos de conceito, pulando os "Mão na massa" (Partes I a IV, depois 21 a 23 e 27).
- **Quero construir:** tudo, com atenção especial aos capítulos 5, 8, 11, 13 e 26, rodando o código.
- **Quero colocar em produção:** Partes I e II como base, depois as Partes VI e VII.
- **Sou gestor ou arquiteto:** capítulos 1 a 4, 12, 14, 15 a 17, 19 a 25 e 27.

## O que este livro não é

Não é um manual de um framework específico: os exemplos são em Python puro, e o capítulo 25 ajuda a escolher uma ferramenta. Não é um guia de "renda fácil com IA". E o código do livro é um esqueleto para aprender, não um produto pronto para instalar na sua empresa. Ele mostra onde fica cada decisão; transformar isso num sistema de verdade é o assunto da Parte VII.

## Como o livro está organizado

- **Parte I — Entendendo agentes:** o que é um agente, suas peças, quanto poder ele deve receber e como funciona o ciclo que faz tudo andar.
- **Parte II — Mãos, memória e conhecimento:** ferramentas, memória e consulta a documentos, os três recursos que transformam um modelo de linguagem num agente útil.
- **Parte III — Processos e equipes:** quando um roteiro fixo é melhor que a improvisação, como pausar para um humano aprovar e quando vale dividir o trabalho entre vários agentes.
- **Parte IV — Conectando tudo:** MCP, A2A e AG-UI, os protocolos que ligam agentes a ferramentas, a outros agentes e às telas que usamos.
- **Parte V — Agentes no trabalho:** agentes que programam, pesquisam, usam o computador e analisam dados, o agente no WhatsApp e por voz e os cuidados em saúde, educação e serviço público.
- **Parte VI — Confiança:** como saber se o agente está indo bem, como enxergar o que ele fez, como protegê-lo de golpes e como respeitar a LGPD.
- **Parte VII — Produção e futuro:** por onde começar na sua empresa, o caminho do protótipo ao sistema de verdade, a escolha de framework e de modelo, um projeto final completo e o que vem por aí.

## Nossa companheira de viagem: a padaria da Dona Cida

Ao longo do livro, vamos acompanhar um exemplo que volta em quase todos os capítulos. A Dona Cida tem uma padaria de bairro, recebe encomendas de bolo pelo WhatsApp, cobra por Pix e vive sem tempo para responder todo mundo. Ela quer um "agente de IA" para ajudar. Capítulo a capítulo, a padaria cresce: ganha encomendas grandes que precisam de aprovação, uma pequena equipe de agentes, fornecedores conectados, e até sofre uma tentativa de golpe. No fim, montamos o sistema inteiro.

Por que uma padaria? Porque todo mundo entende uma padaria. Se o conceito fizer sentido ali, vai fazer sentido num banco, num hospital ou numa empresa de software.

## Como ler as caixas

Você vai encontrar alguns tipos de caixa espalhados pelo texto:

- **Na vida real:** uma situação do cotidiano que ilustra o conceito.
- **Anote aí:** uma definição ou regra que vale guardar.
- **Pegadinha:** um erro comum que vale a pena evitar.
- **Dica:** um atalho prático ou um conselho de quem já errou antes.
- **Mão na massa:** um exercício curto para fixar o conteúdo.
- **Resumo rápido:** o essencial do capítulo em poucas linhas.

Termos técnicos em inglês aparecem em itálico na primeira vez, com a tradução ou explicação logo ao lado. Não vamos fugir deles. Você vai encontrá-los em documentação, vagas de emprego e artigos, e é melhor conhecê-los aqui, com calma.

@BOX DICA|Quer ir mais fundo?
Uma versão técnica desta obra, bem mais extensa e voltada a cursos de graduação, pós-graduação e profissionais de TI, está em preparação. Todo o código, com testes, está em github.com/humbertomoura/agentes-ia-livro. Sempre que um assunto merecer aprofundamento, você vai encontrar uma indicação.
@END
