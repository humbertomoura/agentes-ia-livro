class AgenteArCondicionado:
    """Agente reativo com memória curta (histerese)."""

    def __init__(self):
        self.faixa_aberta = (21.0, 23.0)
        self.faixa_fechada = (17.0, 27.0)
        self.modo_atual = "desligado"  # estado interno

    def perceber(self, temperatura, loja_aberta):
        # Organiza os sinais do ambiente numa observação.
        return {"temperatura": temperatura,
                "loja_aberta": loja_aberta}

    def decidir(self, obs):
        # Política de decisão: regras + estado interno.
        if obs["loja_aberta"]:
            minimo, maximo = self.faixa_aberta
        else:
            minimo, maximo = self.faixa_fechada
        meio = (minimo + maximo) / 2
        t = obs["temperatura"]

        if t < minimo:
            return "aquecer"
        if t > maximo:
            return "resfriar"
        # Na faixa: mantém o modo atual até chegar ao meio.
        if self.modo_atual == "aquecer" and t < meio:
            return "aquecer"
        if self.modo_atual == "resfriar" and t > meio:
            return "resfriar"
        return "desligado"

    def agir(self, modo):
        # Atuador: aqui só guardamos o modo; na vida real,
        # enviaríamos um comando ao aparelho.
        self.modo_atual = modo
