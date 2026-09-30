"""Código extraído do Capítulo 05 — Mão na massa: o atendente da Dona Cida.

Fonte: Agentes_IA_Essencial_v1.docx
Arquivo gerado automaticamente por scripts/extrair_codigo.py.
Não edite este arquivo manualmente.
"""

# Dados de mentira da padaria
CAPACIDADE = 5                      # bolos por dia
AGENDA = {"sexta": 2, "sábado": 5}  # já encomendados
PRECOS = {"bolo de cenoura": 60.0,
          "bolo de chocolate": 70.0}
 
 
def consultar_agenda(dia):
    return {"vagas": CAPACIDADE - AGENDA.get(dia, 0)}
 
 
def consultar_preco(produto):
    if produto not in PRECOS:
        return {"erro": f"não temos {produto}"}
    return {"preco": PRECOS[produto]}
 
 
FERRAMENTAS = {"consultar_agenda": consultar_agenda,
               "consultar_preco": consultar_preco}

from ferramentas import FERRAMENTAS
 
 
def chave(nome, args):
    # ex.: "consultar_agenda:sábado"
    return nome + ":" + ",".join(args.values())
 
 
def reais(valor):
    return f"R$ {valor:.2f}".replace(".", ",")
 
 
def modelo_simulado(pedido, vistos):
    """Finge ser o LLM: devolve (pedidos, resposta)."""
    if not vistos:
        # Primeira volta: pede duas ferramentas juntas.
        return [("consultar_agenda", {"dia": "sábado"}),
                ("consultar_preco",
                 {"produto": "bolo de cenoura"})], None
    preco = vistos["consultar_preco:bolo de cenoura"]
    preco = reais(preco["preco"])
    if vistos["consultar_agenda:sábado"]["vagas"] > 0:
        return [], f"Tem vaga no sábado! Fica {preco}."
    if "consultar_agenda:sexta" not in vistos:
        return [("consultar_agenda",
                 {"dia": "sexta"})], None
    if vistos["consultar_agenda:sexta"]["vagas"] > 0:
        return [], (f"Sábado lotou, mas sexta tem vaga! "
                    f"Fica {preco}. Posso anotar?")
    return [], "Sexta e sábado lotados. Outro dia?"
 
 
def rodar_agente(pedido, decidir, max_voltas=5):
    vistos, trilha = {}, []
    for volta in range(1, max_voltas + 1):
        pedidos, resposta = decidir(pedido, vistos)
        if not pedidos:               # o modelo terminou
            return "SUCESSO", resposta, trilha
        for nome, args in pedidos:
            if nome in FERRAMENTAS:   # portão simples
                resultado = FERRAMENTAS[nome](**args)
            else:                     # vira aviso
                resultado = {"erro": "não existe"}
            vistos[chave(nome, args)] = resultado
            linha = f"[{volta}] {chave(nome, args)}"
            trilha.append(f"{linha} -> {resultado}")
    return "LIMITE_ATINGIDO", None, trilha
 
 
estado, resposta, trilha = rodar_agente(
    "Tem bolo de cenoura pro sábado? Quanto fica?",
    modelo_simulado)
for linha in trilha:
    print(linha)
print("estado:", estado)
print("resposta:")
print(resposta)

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
