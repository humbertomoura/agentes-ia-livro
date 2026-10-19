from rag import buscar, responder

def mostrar(pergunta, perfil):
    print(f"\n{perfil}: {pergunta}")
    evidencias = buscar(pergunta, perfil)
    for e in evidencias:
        print(f"  [{e['id']}] {e['fonte']}")
    if not evidencias:
        print("  (nenhuma evidência)")

mostrar("Quanto tempo o bolo de cenoura fica no forno?",
        "atendente")
mostrar("Tem multa se a farinha atrasar?", "atendente")
mostrar("Tem multa se a farinha atrasar?", "gerencia")
mostrar("Quem ganhou a Copa de 2002?", "atendente")

def modelo_certo(pergunta, evidencias):
    return "Asse por 40 minutos a 180 graus [E1]."

def modelo_inventa(pergunta, evidencias):
    return "Asse por 50 minutos [E7]."

p = "Quanto tempo o bolo de cenoura fica no forno?"
print()
for gerar in (modelo_certo, modelo_inventa):
    estado, texto = responder(p, "atendente", gerar)
    print(f"{estado}: {texto}")
estado, texto = responder("Quem ganhou a Copa de 2002?",
                          "atendente", modelo_certo)
print(f"{estado}: {texto}")

def so_etiquetas(pergunta, evidencias):
    return "Foi a avó da Dona Cida que inventou [E1]."

estado, texto = responder("Quem inventou o bolo de cenoura?",
                          "atendente", so_etiquetas)
print(f"{estado}: {texto}")
