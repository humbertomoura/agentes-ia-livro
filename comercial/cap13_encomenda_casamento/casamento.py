import hashlib
import json

LIMITE_APROVACAO = 1000
AUTORIZADOS = {"dona_cida"}
FINAIS = {"Sucesso", "Falha", "Cancelado"}


class Armazem:
    """Guarda o estado como texto, como um banco."""

    def __init__(self):
        self.dados = {}

    def salvar(self, chave, estado):
        self.dados[chave] = json.dumps(estado)

    def ler(self, chave):
        return json.loads(self.dados[chave])


class Forno:
    def __init__(self):
        self.reservas = {}
        self.liberadas = set()

    def reservar(self, chave, dia):
        if chave not in self.reservas:
            numero = f"F{len(self.reservas) + 1}"
            self.reservas[chave] = numero
        return self.reservas[chave]

    def liberar(self, numero):
        self.liberadas.add(numero)


class Pix:
    def __init__(self):
        self.cobrancas = {}
        self.estornos = set()

    def gerar(self, chave, valor):
        if chave not in self.cobrancas:
            numero = f"PIX{len(self.cobrancas) + 1}"
            self.cobrancas[chave] = (numero, valor)
        return self.cobrancas[chave][0]

    def estornar(self, numero):
        self.estornos.add(numero)


def versao(pedido):
    texto = json.dumps(pedido, sort_keys=True)
    return hashlib.sha256(texto.encode()).hexdigest()[:10]


def conferir(estado, ctx):
    p = estado["pedido"]
    if p["salgados"] <= 0 or p["andares"] <= 0:
        return "falhar", "quantidade inválida"
    return "seguir", {}


def calcular(estado, ctx):
    p = estado["pedido"]
    kg = p["salgados"] * 0.03 + p["andares"] * 1.5
    return "seguir", {"farinha_kg": round(kg, 1)}


def aprovar(estado, ctx):
    p = estado["pedido"]
    if p["valor"] <= LIMITE_APROVACAO:
        return "seguir", {"aprovado_por": "regra"}
    ap = estado.get("aprovacao")
    if ap is None:
        return "esperar", "aguardando a Dona Cida"
    if ap["versao"] != versao(p):
        return "esperar", "pedido mudou: aprovar de novo"
    return "seguir", {"aprovado_por": ap["quem"]}


def reservar(estado, ctx):
    p = estado["pedido"]
    chave = f"forno:{p['id']}:{p['dia']}"
    numero = ctx["forno"].reservar(chave, p["dia"])
    return "seguir", {"reserva": numero}


def cobrar(estado, ctx):
    p = estado["pedido"]
    chave = f"sinal:{p['id']}"
    valor = round(p["valor"] * 0.3, 2)
    numero = ctx["pix"].gerar(chave, valor)
    if ctx.get("cair_em") == "cobrar":
        ctx["cair_em"] = None
        raise RuntimeError("queda de energia")
    return "seguir", {"cobranca": numero}


PASSOS = [("conferir", conferir),
          ("calcular", calcular),
          ("aprovar", aprovar),
          ("reservar", reservar),
          ("cobrar", cobrar)]


class Workflow:
    def __init__(self, armazem, ctx):
        self.armazem = armazem
        self.ctx = ctx

    def iniciar(self, pedido):
        estado = {"pedido": pedido, "passo": 0,
                  "status": "Pronto", "trilha": []}
        self.armazem.salvar(pedido["id"], estado)
        return self.rodar(pedido["id"])

    def rodar(self, id_pedido):
        estado = self.armazem.ler(id_pedido)
        if estado["status"] in FINAIS:
            return estado
        estado["status"] = "Em andamento"
        while estado["passo"] < len(PASSOS):
            nome, passo = PASSOS[estado["passo"]]
            acao, info = passo(estado, self.ctx)
            if acao == "esperar":
                estado["status"] = "Bloqueado"
                estado["motivo"] = info
                self.armazem.salvar(id_pedido, estado)
                return estado
            if acao == "falhar":
                estado["status"] = "Falha"
                estado["motivo"] = info
                self.armazem.salvar(id_pedido, estado)
                return estado
            estado.update(info)
            estado["trilha"].append(nome)
            estado["passo"] += 1
            self.armazem.salvar(id_pedido, estado)
        estado["status"] = "Sucesso"
        estado.pop("motivo", None)
        self.armazem.salvar(id_pedido, estado)
        return estado

    def versao_atual(self, id_pedido):
        estado = self.armazem.ler(id_pedido)
        return versao(estado["pedido"])

    def aprovar(self, id_pedido, quem, versao_vista):
        if quem not in AUTORIZADOS:
            raise PermissionError(f"{quem} não aprova")
        estado = self.armazem.ler(id_pedido)
        estado["aprovacao"] = {"quem": quem,
                               "versao": versao_vista}
        self.armazem.salvar(id_pedido, estado)
        return self.rodar(id_pedido)

    def alterar(self, id_pedido, **mudancas):
        estado = self.armazem.ler(id_pedido)
        if estado["status"] != "Bloqueado":
            raise ValueError("só altera pedido parado")
        estado["pedido"].update(mudancas)
        self.armazem.salvar(id_pedido, estado)
        return self.rodar(id_pedido)

    def cancelar(self, id_pedido):
        estado = self.armazem.ler(id_pedido)
        if "reserva" in estado:
            self.ctx["forno"].liberar(estado["reserva"])
        if "cobranca" in estado:
            self.ctx["pix"].estornar(estado["cobranca"])
        estado["status"] = "Cancelado"
        self.armazem.salvar(id_pedido, estado)
        return estado
