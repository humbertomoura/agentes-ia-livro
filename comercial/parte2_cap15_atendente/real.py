import json
import os
from openai import OpenAI
from ferramentas import FERRAMENTAS

cliente = OpenAI()  # usa a chave em OPENAI_API_KEY
MODELO = os.getenv("OPENAI_MODEL", "gpt-6-astra")

INSTRUCOES = (
    "Você é o atendente da padaria da Dona Cida. "
    "Consulte agenda e preços antes de responder.")


def ferramenta(nome, descricao, campo):
    return {"type": "function", "name": nome,
            "description": descricao, "strict": True,
            "parameters": {
                "type": "object",
                "properties": {campo: {"type": "string"}},
                "required": [campo],
                "additionalProperties": False}}


TOOLS = [
    ferramenta("consultar_agenda",
               "Diz quantas vagas há no dia.",
               "dia"),
    ferramenta("consultar_preco",
               "Diz o preço de um produto da padaria.",
               "produto"),
]

pergunta = "Tem bolo de cenoura pro sábado? Quanto fica?"
historico = [{"role": "user", "content": pergunta}]

for volta in range(5):
    resposta = cliente.responses.create(
        model=MODELO, instructions=INSTRUCOES,
        input=historico, tools=TOOLS)
    historico.extend(resposta.output)  # guarda tudo
    pedidos = [item for item in resposta.output
               if item.type == "function_call"]
    if not pedidos:                 # o modelo terminou
        print(resposta.output_text)
        break
    for pedido in pedidos:
        try:
            args = json.loads(pedido.arguments)
            resultado = FERRAMENTAS[pedido.name](**args)
        except Exception as erro:   # erro vira aviso
            resultado = {"erro": str(erro)}
        historico.append({
            "type": "function_call_output",
            "call_id": pedido.call_id,
            "output": json.dumps(resultado,
                                 ensure_ascii=False)})
else:
    print("Limite de voltas atingido sem resposta final.")
