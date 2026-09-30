from casamento import Armazem, Forno, Pix, Workflow

armazem = Armazem()
ctx = {"forno": Forno(), "pix": Pix()}
wf = Workflow(armazem, ctx)

pedido = {"id": "E42", "salgados": 200,
          "andares": 3, "dia": "14/11", "valor": 1400}

e = wf.iniciar(pedido)
print("1.", e["status"], "-", e["motivo"])

vista = wf.versao_atual("E42")   # Dona Cida lê
e = wf.alterar("E42", salgados=300, valor=1900)
e = wf.aprovar("E42", "dona_cida", vista)
print("2.", e["status"], "-", e["motivo"])

try:
    wf.aprovar("E42", "julia", wf.versao_atual("E42"))
except PermissionError as erro:
    print("3. recusado:", erro)

ctx["cair_em"] = "cobrar"
try:
    nova = wf.versao_atual("E42")
    wf.aprovar("E42", "dona_cida", nova)
except RuntimeError as erro:
    print("4. caiu:", erro)

wf2 = Workflow(armazem, ctx)   # sistema reiniciado
e = wf2.rodar("E42")
print("5.", e["status"], e["reserva"], e["cobranca"])
print("   passos:", ", ".join(e["trilha"]))
print("   cobranças feitas:", len(ctx["pix"].cobrancas))

e = wf2.cancelar("E42")
print("6.", e["status"], "| forno liberado:",
      ctx["forno"].liberadas, "| estorno:",
      ctx["pix"].estornos)
