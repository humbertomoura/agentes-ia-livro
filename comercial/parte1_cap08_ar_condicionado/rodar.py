from agente import AgenteArCondicionado

leituras = [
    (19.0, True), (20.5, True), (21.5, True), (22.3, True),
    (23.8, True), (22.6, True), (21.9, True), (24.0, False),
]

agente = AgenteArCondicionado()

for temperatura, aberta in leituras:
    obs = agente.perceber(temperatura, aberta)  # observar
    modo = agente.decidir(obs)                  # decidir
    agente.agir(modo)                           # agir
    situacao = "aberta" if aberta else "fechada"
    print(f"{temperatura:4.1f} °C, loja {situacao}: {modo}")
