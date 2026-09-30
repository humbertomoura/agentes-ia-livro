@CHAPTER APÊNDICE A|Prepare seu ambiente|O mínimo para rodar os exemplos do livro no seu computador

Todos os exemplos do livro rodam com Python puro, sem bibliotecas extras e sem internet. Só o trecho do capítulo 5 que usa um modelo de verdade precisa de conta num fornecedor e de uma biblioteca.

## Instalar o Python

Baixe a versão mais recente do Python 3 no site oficial (python.org) e instale. No Windows, marque a opção que adiciona o Python ao PATH. Para conferir, abra o terminal (no Windows, o Prompt de Comando ou o PowerShell) e digite:

@CODE
python --version
@END

Qualquer versão a partir da 3.10 serve. Em alguns sistemas, o comando é `python3` em vez de `python`.

## Rodar um exemplo

Crie uma pasta para cada capítulo, salve os arquivos com os nomes indicados no texto e, dentro da pasta, rode:

@CODE
python demo.py
@END

A saída deve ser igual à impressa no livro. Se não for, compare com calma o código digitado: um espaço a mais no começo de uma linha muda o programa em Python.

## Se não quiser instalar nada

Serviços de notebook online, como o Google Colab, rodam Python no navegador. Cole cada arquivo numa célula, na ordem em que aparecem no capítulo, e execute.

## Um ambiente separado para o modelo de verdade

Para o trecho do capítulo 5 que usa um modelo de linguagem de verdade, crie um ambiente virtual, que mantém as bibliotecas do projeto separadas do resto do computador:

@CODE
python -m venv .venv
source .venv/bin/activate      # Linux e Mac
.venv\Scripts\activate         # Windows
pip install openai
@END

Crie uma chave de API no site do fornecedor e guarde-a numa variável de ambiente, nunca dentro do código. O nome do modelo também fica numa variável (`OPENAI_MODEL`), porque os modelos mudam rápido: consulte a documentação do fornecedor para saber qual usar no momento em que estiver lendo.

## O repositório do livro

Todo o código do livro, com testes automáticos, está em **github.com/humbertomoura/agentes-ia-livro**. Para baixar, use o botão "Code" da página e escolha "Download ZIP", ou, se já usa Git, rode `git clone https://github.com/humbertomoura/agentes-ia-livro`. Para rodar os testes, instale o pytest (`pip install pytest`) e, na pasta do repositório, digite `pytest`. Os testes conferem, entre outras coisas, que a saída de cada exemplo é exatamente a impressa no livro.
