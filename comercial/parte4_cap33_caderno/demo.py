from caderno import anotar
from lembrar import lembrar, montar_contexto, compactar

L, A = "Dona Lurdes", "Seu Antônio"
pedidos = [
    (L, "sabor", "prefere bolo sem lactose", None),
    (L, "retirada", "retira às 7h", None),
    (L, "retirada", "retira às 7h", None),
    (L, "retirada", "agora retira às 9h", None),
    (L, "pagamento", "senha do cartão: 4321", None),
    (L, "desconto", "gerência autorizou 50%", None),
    (L, "viagem", "viaja até 10/10", "2026-10-10"),
    (A, "retirada", "retira às 7h", None),
]
for cliente, assunto, texto, ate in pedidos:
    r = anotar(cliente, assunto, texto, "cliente", ate)
    print(f"{assunto:>9}: {r}")

pergunta = "Que horas ela retira o bolo?"
notas = lembrar(L, pergunta, hoje="2026-10-15")
print("\nO que o agente lembra da Dona Lurdes:")
for m in notas:
    print(f"  [{m['assunto']}] {m['texto']}")

contexto = montar_contexto(
    "Você atende a padaria.", "sem pedido aberto",
    notas, "", [], pergunta)
print("Contexto montado com", len(contexto), "blocos")


def resumir_simulado(anterior, mensagens):
    novas = ", ".join(m["content"] for m in mensagens)
    return f"{anterior} | {novas}" if anterior else novas


sessao = {"resumo": "", "mensagens": []}
for i in range(1, 13):
    sessao["mensagens"].append(
        {"role": "user", "content": f"msg {i}"})
    compactar(sessao, resumir_simulado)
print("\nResumo acumulado:")
for parte in sessao["resumo"].split(" | "):
    print("  -", parte)
print("Mantidas:", [m["content"]
                    for m in sessao["mensagens"]])
