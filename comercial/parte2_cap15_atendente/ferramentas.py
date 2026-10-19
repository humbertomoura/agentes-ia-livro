# Dados de mentira da padaria
CAPACIDADE = 5                      # bolos por dia
AGENDA = {"sexta": 2, "sábado": 5}  # já encomendados
PRECOS = {"bolo de cenoura": 60.0,
          "bolo de chocolate": 70.0}


def consultar_agenda(dia):
    if dia not in AGENDA:       # desconhecido não é "livre"
        return {"erro": f"não aceitamos encomendas para {dia}"}
    return {"vagas": CAPACIDADE - AGENDA[dia]}


def consultar_preco(produto):
    if produto not in PRECOS:
        return {"erro": f"não temos {produto}"}
    return {"preco": PRECOS[produto]}


FERRAMENTAS = {"consultar_agenda": consultar_agenda,
               "consultar_preco": consultar_preco}
