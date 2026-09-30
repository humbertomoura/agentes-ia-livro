import re


def numero(msg):
    achado = re.search(r"\bE\d+\b", msg.upper())
    return achado.group(0) if achado else "E0"


def ultimo(historico, nome):
    for item in reversed(historico):
        pedido = item.get("pedido", {})
        if pedido.get("nome") == nome:
            return item["resultado"]
    return None


def modelo(historico):
    """Imita um LLM com regras fixas."""
    msg = historico[0]["cliente"].lower()
    memoria = historico[0]["memoria"]
    if "bolo" in msg:
        casamento = "casamento" in msg
        agenda = ultimo(historico, "consultar_agenda")
        if agenda is None:
            return [{"nome": "consultar_agenda",
                     "args": {"dia": "sexta"}}], None
        enc = ultimo(historico, "registrar_encomenda")
        if enc is None:
            return [{"nome": "registrar_encomenda",
                     "args": {
                         "bolo": ("casamento"
                                  if casamento
                                  else "cenoura"),
                         "dia": "sexta",
                         "valor": 1400 if casamento
                         else 90}}], None
        extra = ""
        if "restricao" in memoria:
            extra = f" ({memoria['restricao']})"
        return [], (f"Anotado: sexta{extra}, "
                    f"pedido {enc['numero']}.")
    if "estorno" in msg:
        feito = ultimo(historico, "solicitar_estorno")
        if feito is None:
            return [{"nome": "solicitar_estorno",
                     "args": {
                         "encomenda": numero(msg)}}], None
        return [], "Não posso. Chamo a Dona Cida."
    if "sinal" in msg:
        feito = ultimo(historico, "gerar_pix")
        if feito is None:
            return [{"nome": "gerar_pix",
                     "args": {
                         "encomenda": numero(msg)}}], None
        if "erro" in feito:
            return [], f"Não deu: {feito['erro']}."
        return [], f"Sinal gerado: {feito['cobranca']}."
    if "?" in msg:
        achado = ultimo(historico, "buscar_regra")
        if achado is None:
            return [{"nome": "buscar_regra",
                     "args": {"pergunta": msg}}], None
        if "evidencias" not in achado:
            return [], "Não encontrei essa informação."
        ev = achado["evidencias"][0]
        return [], f"{ev['texto']} [{ev['id']}]"
    return [], "Posso ajudar com encomendas."
