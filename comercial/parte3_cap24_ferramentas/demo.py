from controle import Execucao, continuar
from runtime import congelar


def modelo_simulado(vistos):
    """Finge ser o LLM: devolve (pedidos, resposta)."""
    if not vistos:
        return [("p1", "consultar_agenda",
                 {"dia": "sexta"})], ""
    nome, ultimo = vistos[-1]
    if not ultimo["ok"]:            # erro vira informação
        return [], f"Não deu certo: {ultimo['erro']}."
    if nome == "consultar_agenda":
        if ultimo["vagas"] == 0:
            return [], "Sexta está lotada. Pode ser outro dia?"
        bolo = {"produto": "bolo de cenoura",
                "dia": "sexta"}
        # Por engano, o modelo pede a mesma coisa 2 vezes.
        return [("p2", "registrar_encomenda", bolo),
                ("p3", "registrar_encomenda", bolo)], ""
    return [], f"Encomenda {ultimo['numero']} confirmada!"


aprovados = {}      # id do pedido -> exatamente o que foi aprovado
ex = Execucao(sessao={"cliente": "Dona Lurdes"})
ex = continuar(ex, modelo_simulado, aprovados)

while ex.estado == "BLOQUEADO":
    id_p, nome, args = ex.pendentes[0]
    ex.trilha.append(f"    >> Dona Cida aprovou {id_p}")
    aprovados[id_p] = (ex.sessao["cliente"], nome,
                       congelar(args))  # cópia congelada
    ex = continuar(ex, modelo_simulado, aprovados)

for linha in ex.trilha:
    print(linha)
print("estado:", ex.estado)
print("resposta:", ex.resposta)
