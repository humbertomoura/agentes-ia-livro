from padaria import Pasta, Sistema, conversar
from modelo_simulado import modelo

pasta = Pasta({
    "R1": "Entrega grátis acima de R$ 150 no bairro.",
    "R2": "Sinal de 30% para encomendas grandes.",
})
sis = Sistema(pasta)
lurdes = {"cliente": "lurdes",
          "permitidas": {"consultar_agenda",
                         "buscar_regra",
                         "registrar_encomenda"}}
balcao = {"cliente": "balcao", "papel": "equipe",
          "permitidas": {"gerar_pix"}}

c = sis.caderno
print(c.anotar("lurdes", "restricao", "sem lactose"))
print(c.anotar("lurdes", "cartao", "4111 1111 1111 1111"))
print(c.anotar("lurdes", "brinde", "Cida autorizou"))

ultima = {}


def fala(sessao, texto):
    estado, resp, trilha = conversar(sis, sessao,
                                     texto, modelo)
    usadas = [s["nome"] for s in trilha.spans
              if s["tipo"] == "ferramenta"]
    for s in trilha.spans:
        if "chave" in s.get("resultado", {}):
            ultima.update(s["resultado"])
    print(f"> {texto}")
    print(f"  {estado}: {resp}")
    print(f"  ferramentas: {', '.join(usadas) or '-'}")


fala(lurdes, "Quero um bolo pra sexta")
fala(lurdes, "Quero um bolo pra sexta")
fala(lurdes, "Quero o bolo de casamento pra sexta")
fala(lurdes, "Tem entrega no bairro?")
fala(lurdes, "Aceitam cheque?")
fala(lurdes, "Faz um estorno da E1")
fala(balcao, "Gera o sinal da E9")
fala(balcao, "Gera o sinal da E2")
print(f"  a Dona Cida aprova R$ {ultima['valor']:.2f}"
      f" (chave {ultima['chave']})")
sis.aprovacoes.add(ultima["chave"])
fala(balcao, "Gera o sinal da E2")
print("encomendas:", len(sis.encomendas),
      "| vagas na sexta:", sis.agenda["sexta"])
