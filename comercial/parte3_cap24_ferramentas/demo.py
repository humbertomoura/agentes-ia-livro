from controle import Execucao, continuar


def modelo_simulado(vistos):
    """Finge ser o LLM: devolve (pedidos, resposta)."""
    if not vistos:
        return [("p1", "consultar_agenda",
                 {"dia": "sexta"})], ""
    nome, ultimo = vistos[-1]
    if nome == "consultar_agenda":
        bolo = {"produto": "bolo de cenoura",
                "dia": "sexta"}
        # Por engano, o modelo pede a mesma coisa 2 vezes.
        return [("p2", "registrar_encomenda", bolo),
                ("p3", "registrar_encomenda", bolo)], ""
    return [], f"Encomenda {ultimo['numero']} confirmada!"


aprovados = set()
ex = Execucao(sessao={"cliente": "Dona Lurdes"})
ex = continuar(ex, modelo_simulado, aprovados)

while ex.estado == "BLOQUEADO":
    id_p = ex.pendentes[0][0]
    ex.trilha.append(f"    >> Dona Cida aprovou {id_p}")
    aprovados.add(id_p)        # aprovação humana
    ex = continuar(ex, modelo_simulado, aprovados)

for linha in ex.trilha:
    print(linha)
print("estado:", ex.estado)
print("resposta:", ex.resposta)
