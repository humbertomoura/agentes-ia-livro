# Agentes de IA na Prática

**Do problema à solução em Python — código-fonte e exemplos do livro**

> **Todo mundo fala de agentes de IA. Este livro mostra como construir um, passo a passo.**

Aqui você encontra os exemplos de *Agentes de IA na Prática: Do problema à solução em Python*, de **Humberto Jorge de Moura Costa**. A proposta é compreender e implementar os mecanismos internos de um agente antes de depender das abstrações de um framework.

O fio condutor é a **padaria da Dona Cida**, um cenário didático que evolui de decisões simples para ferramentas, aprovação humana, memória e consulta a documentos.

**O que esperar deste repositório:**

- **5 exemplos progressivos e independentes**, correspondentes aos capítulos práticos do livro.
- **Código em Python**, acompanhado de saídas esperadas e testes automatizados.
- **Execução local sem chave de API** para os cinco exemplos didáticos. Uma demonstração adicional do capítulo 15 utiliza a API da OpenAI.
- **Foco nos fundamentos:** os exemplos ilustram componentes de agentes, não um sistema integrado pronto para produção.

## Exemplos por capítulo

| Parte | Capítulo | O que você vai explorar |
|---|---:|---|
| **1 · Fundamentos** | 8 | Agente reativo baseado em regras, observação e estado interno, sem LLM |
| **2 · Ciclo do agente** | 15 | Chamadas de ferramentas, controle do ciclo e comparação entre simulação e LLM real |
| **3 · Ferramentas** | 24 | Validação, aprovação humana, retomada e prevenção de operações duplicadas |
| **4 · Contexto e memória** | 33 | Seleção, atualização, validade, controle de acesso e compactação da memória |
| **5 · Recuperação de informações** | 42 | Busca didática em documentos, filtros de acesso, citações e respostas sem evidências |

Cada pasta contém um arquivo `saida_esperada.txt`. Os testes conferem se as cinco demonstrações locais produzem as saídas registradas nesses arquivos.

## Comece por aqui

Você precisa de **Python 3.11 ou superior**. O apêndice *Prepare seu ambiente*, no livro, explica a configuração passo a passo.

Clone o repositório, crie um ambiente virtual e instale as dependências:

```bash
git clone https://github.com/humbertomoura/agentes-ia-livro.git
cd agentes-ia-livro
python -m venv .venv
```

No Linux ou macOS, ative o ambiente com `source .venv/bin/activate`. No Windows PowerShell, use `.\.venv\Scripts\Activate.ps1`.

```bash
python -m pip install -r requirements-dev.txt
```

Execute o primeiro exemplo a partir da raiz do repositório:

```bash
python comercial/parte1_cap08_ar_condicionado/rodar.py
```

Experimente também os demais capítulos:

```bash
python comercial/parte2_cap15_atendente/simulado.py
python comercial/parte3_cap24_ferramentas/demo.py
python comercial/parte4_cap33_caderno/demo.py
python comercial/parte5_cap42_pasta/demo.py
```

Esses cinco comandos não exigem chave de API nem fazem chamadas a um LLM externo.

### Sem instalar nada: Google Colab

Abra um notebook no Google Colab e execute:

```python
!git clone https://github.com/humbertomoura/agentes-ia-livro.git
%cd agentes-ia-livro
!python comercial/parte1_cap08_ar_condicionado/rodar.py
```

## Experimento opcional: LLM real (capítulo 15)

O arquivo `comercial/parte2_cap15_atendente/real.py` demonstra o uso de ferramentas por meio da API da OpenAI. **Este exemplo exige chave de API, acesso à internet e pode gerar custos.**

Defina `OPENAI_API_KEY` e `OPENAI_MODEL` com sua chave e o identificador de um modelo compatível com a Responses API e chamadas de ferramentas. Em seguida, execute:

```bash
python comercial/parte2_cap15_atendente/real.py
```

**Segurança:** nunca publique sua chave de API. As respostas do LLM real podem variar entre execuções.

## Testes e reprodução dos resultados

Na raiz do repositório, execute:

```bash
python -m pytest -q
```

Os testes automatizados comparam as saídas dos cinco exemplos didáticos, verificam o ciclo de ferramentas com um cliente simulado e testam uma regra de isolamento de informações entre clientes.

Não é necessário acesso à internet nem chave de API durante a execução dos testes.

## Encontrou um problema?

Abra uma [issue no GitHub](https://github.com/humbertomoura/agentes-ia-livro/issues) ou envie uma mensagem para **livro@humbertomoura.com.br**.

Informe, sempre que possível, o capítulo, o arquivo envolvido, sua versão do Python, o comportamento observado e a saída esperada.

## Licença e direitos autorais

O **código-fonte** está disponível sob a licença MIT (consulte `LICENSE`). O **texto, as figuras e os demais conteúdos editoriais do livro** não fazem parte dessa licença e têm seus direitos reservados.

---

**Agentes de IA na Prática — Do problema à solução em Python**

*Humberto Jorge de Moura Costa · Professor e pesquisador em Computação*
