# Agentes de IA na Prática — código do livro

Código-fonte dos capítulos práticos do livro **Agentes de IA na Prática: do problema à solução em Python**, de Humberto Jorge de Moura Costa.

Todos os exemplos usam a padaria da Dona Cida, a personagem que acompanha o livro, e rodam sem chave de API, exceto o `real.py` do capítulo 15. Cada exemplo imprime exatamente a saída mostrada no livro, e os testes garantem isso.

## Capítulos

| Capítulo | Pasta | O que o exemplo mostra |
|---|---|---|
| 8 | `comercial/parte1_cap08_ar_condicionado` | Um agente simples, sem IA, com estado interno |
| 15 | `comercial/parte2_cap15_atendente` | O ciclo de chamadas de ferramenta, simulado e com modelo real |
| 24 | `comercial/parte3_cap24_ferramentas` | Ferramentas com aprovação, bloqueio, retomada e sem duplicar pedidos |
| 33 | `comercial/parte4_cap33_caderno` | Memória com portões, substituição, validade e resumo acumulado |
| 42 | `comercial/parte5_cap42_pasta` | Busca em documentos com filtro de acesso, "não encontrei" e citações |

## Como rodar

Precisa do Python 3.11 ou mais recente. O apêndice "Prepare seu ambiente", no fim do livro, explica cada passo.

```bash
python -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

cd comercial/parte1_cap08_ar_condicionado
python rodar.py
```

Cada pasta tem um `saida_esperada.txt` para você comparar com o que apareceu na tela.

### Sem instalar nada (Google Colab)

```
!git clone https://github.com/humbertomoura/agentes-ia-livro.git
%cd agentes-ia-livro/comercial/parte1_cap08_ar_condicionado
!python rodar.py
```

### Com um modelo de verdade (capítulo 15)

```bash
export OPENAI_API_KEY="sua-chave"   # Windows: $env:OPENAI_API_KEY = "sua-chave"
export OPENAI_MODEL="gpt-6-astra"   # confira o modelo recomendado na documentação
python comercial/parte2_cap15_atendente/real.py
```

Nunca coloque a chave dentro do código nem a publique em repositórios.

## Testes

```bash
pytest -q
```

Os testes não usam internet nem chave de API.

## Encontrou um erro?

Abra uma *issue* neste repositório, dizendo o capítulo e o que aconteceu.

## Licença

O código está sob a licença MIT (ver `LICENSE`). O texto do livro não faz parte deste repositório e tem todos os direitos reservados.
