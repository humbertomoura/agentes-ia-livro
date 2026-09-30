import sys, glob; sys.path.insert(0, '/home/claude/ess')
from build import *
PARTS = ['PARTE I — ENTENDENDO AGENTES', 'PARTE II — MÃOS, MEMÓRIA E CONHECIMENTO',
         'PARTE III — PROCESSOS E EQUIPES', 'PARTE IV — CONECTANDO TUDO',
         'PARTE V — AGENTES NO TRABALHO', 'PARTE VI — CONFIANÇA', 'PARTE VII — PRODUÇÃO E FUTURO']
TOC = [('item', 'Antes de começar'), ('part', PARTS[0])] + [('item', t) for t in [
 '1. O que é um agente, afinal?', '2. Por dentro de um agente', '3. Quanto poder dar ao agente',
 '4. O ciclo do agente', '5. Mão na massa: o atendente da Dona Cida', 'Fechando a Parte I']] + [('part', PARTS[1])] + [('item', t) for t in [
 '6. As mãos do agente', '7. Ferramentas que não quebram nada', '8. Mão na massa: encomendas com aprovação',
 '9. A bancada e o caderno', '10. Consultar antes de responder', '11. Mão na massa: respostas com fonte',
 'Fechando a Parte II']] + [('part', PARTS[2])] + [('item', t) for t in [
 '12. Quando o roteiro é melhor que o improviso', '13. Mão na massa: a encomenda do casamento',
 '14. Equipes de agentes', 'Fechando a Parte III']] + [('part', PARTS[3])] + [('item', t) for t in [
 '15. MCP: a tomada universal', '16. A2A: agente conversa com agente', '17. O agente na tela',
 'Fechando a Parte IV']] + [('part', PARTS[4])] + [('item', t) for t in [
 '18. Agentes especializados', '19. Agente no WhatsApp e por voz',
 '20. Agentes em saúde, educação e serviço público', 'Fechando a Parte V']] + [('part', PARTS[5])] + [('item', t) for t in [
 '21. Saber se está indo bem e enxergar por dentro', '22. Golpes contra agentes',
 '23. Permissões, privacidade e regras', 'Fechando a Parte VI']] + [('part', PARTS[6])] + [('item', t) for t in [
 '24. Por onde começar e como chegar à produção', '25. Como escolher framework e modelo',
 '26. Projeto final: a padaria inteira', '27. O que vem por aí', 'Fechando a Parte VII',
 'Apêndice A: prepare seu ambiente', 'Apêndice B: mapa de frameworks', 'Glossário', 'Sobre o autor']]
title = title_page('AGENTES DE', 'INTELIGÊNCIA ARTIFICIAL', 'Um guia prático para entender, construir e',
                   'colocar agentes de IA em produção', PARTS,
                   'Humberto Jorge de Moura Costa', '1ª edição · 2026')
COLOFAO = parse('''@CHAPTER  |Sobre esta edição|

© 2026 Humberto Jorge de Moura Costa. Todos os direitos reservados. Nenhuma parte deste livro pode ser reproduzida sem autorização do autor, exceto em citações curtas com indicação da fonte.

1ª edição, 2026.

Fatos sobre produtos, protocolos, preços e regras conferidos até 29 de setembro de 2026. Tecnologias e normas mudam rápido: antes de decidir com base nelas, confira a documentação oficial na data.

Todo o código do livro, com testes automáticos, está em **github.com/humbertomoura/agentes-ia-livro**. Correções e atualizações são publicadas no mesmo endereço.

Marcas e nomes de produtos citados pertencem a seus respectivos donos e aparecem apenas para fins de identificação.
''')
files = sorted(glob.glob('/home/claude/ess/cap/*.md'))
build2(files, sys.argv[1], title + COLOFAO, toc(TOC))
print('ok', len(files), 'arquivos')
