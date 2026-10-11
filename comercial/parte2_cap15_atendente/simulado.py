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
