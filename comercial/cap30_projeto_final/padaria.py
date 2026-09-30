import hashlib
import json
import re

FINAIS = {"Sucesso", "Falha", "Limite atingido",
          "Bloqueado"}


class Trilha:
    """Um trace simples: uma lista de spans."""

    def __init__(self, conversa):
        self.conversa = conversa
        self.spans = []

    def span(self, tipo, **dados):
        self.spans.append({"tipo": tipo, **dados})


class Pasta:
    """RAG mínimo: busca por palavras com citação."""

    def __init__(self, trechos):
        self.trechos = trechos

    def buscar(self, pergunta):
        palavras = set(re.findall(r"\w+",
                                  pergunta.lower()))
        melhores = []
        for id_, texto in self.trechos.items():
            comuns = palavras & set(
                re.findall(r"\w+", texto.lower()))
            if len(comuns) >= 2:
                melhores.append((len(comuns), id_))
        melhores.sort(reverse=True)
        return [{"id": i, "texto": self.trechos[i]}
                for _, i in melhores[:2]]


class Caderno:
    """Memória com portões de escrita e leitura."""

    PROIBIDO = re.compile(
        r"\d{4} ?\d{4} ?\d{4} ?\d{4}|autoriz|desconto",
        re.I)

    def __init__(self):
        self.notas = {}

    def anotar(self, cliente, assunto, texto):
        if self.PROIBIDO.search(texto):
            return "recusado"
        self.notas[(cliente, assunto)] = texto
        return "anotado"

    def ler(self, cliente):
        return {a: t for (c, a), t in self.notas.items()
                if c == cliente}


class Sistema:
    def __init__(self, pasta):
        self.pasta = pasta
        self.caderno = Caderno()
        self.agenda = {"sexta": 3, "sábado": 0}
        self.encomendas = {}
        self.por_numero = {}
        self.pix = {}
        self.estornos = {}
        self.aprovacoes = set()

    # ---- ferramentas (o que o modelo pode pedir) ----
    def consultar_agenda(self, sessao, dia):
        return {"dia": dia,
                "vagas": self.agenda.get(dia, 0)}

    def buscar_regra(self, sessao, pergunta):
        achados = self.pasta.buscar(pergunta)
        if not achados:
            return {"status": "não encontrei"}
        return {"evidencias": achados}

    def registrar_encomenda(self, sessao, bolo, dia,
                            valor):
        if self.agenda.get(dia, 0) <= 0:
            return {"erro": "dia lotado"}
        chave = f"{sessao['cliente']}:{bolo}:{dia}"
        if chave not in self.encomendas:
            self.agenda[dia] -= 1
            numero = f"E{len(self.encomendas) + 1}"
            registro = {"numero": numero,
                        "cliente": sessao["cliente"],
                        "valor": valor}
            self.encomendas[chave] = registro
            self.por_numero[numero] = registro
        return self.encomendas[chave]

    def encomenda(self, sessao, numero):
        """Fonte oficial do valor. Cliente só vê
        as próprias; a equipe vê todas."""
        enc = self.por_numero.get(numero)
        if enc is None:
            return None
        if (sessao.get("papel") != "equipe"
                and enc["cliente"] != sessao["cliente"]):
            return None
        return enc

    def gerar_pix(self, sessao, encomenda, valor):
        chave = f"pix:{encomenda}:{valor}"
        if chave not in self.pix:
            self.pix[chave] = f"PIX{len(self.pix) + 1}"
        return {"cobranca": self.pix[chave]}

    def solicitar_estorno(self, sessao, encomenda,
                          valor):
        chave = f"estorno:{encomenda}:{valor}"
        if chave not in self.estornos:
            numero = f"EST{len(self.estornos) + 1}"
            self.estornos[chave] = numero
        return {"estorno": self.estornos[chave]}


# nome -> (risco, campos obrigatórios)
REGISTRO = {
    "consultar_agenda": ("R0", {"dia"}),
    "buscar_regra": ("R0", {"pergunta"}),
    "registrar_encomenda": ("R2",
                            {"bolo", "dia", "valor"}),
    "gerar_pix": ("R3", {"encomenda"}),
    "solicitar_estorno": ("R4", {"encomenda"}),
}
LIMITE_SEM_APROVACAO = 300


def resolver(sistema, sessao, nome, args):
    """Completa o pedido com os dados oficiais.
    O modelo diz qual encomenda; o valor vem
    do sistema, nunca do modelo."""
    if nome in ("gerar_pix", "solicitar_estorno"):
        enc = sistema.encomenda(sessao,
                                args["encomenda"])
        if enc is None:
            return None, "encomenda não encontrada"
        base = enc["valor"]
        valor = (round(base * 0.3, 2)
                 if nome == "gerar_pix" else base)
        return {"encomenda": enc["numero"],
                "valor": valor}, None
    return dict(args), None


def sentido(acao):
    """Validação semântica: o formulário certo
    ainda pode trazer um pedido sem sentido."""
    if "valor" in acao and not acao["valor"] > 0:
        return "valor precisa ser positivo"
    return None


def digital(nome, acao):
    """Impressão digital da ação exata."""
    texto = json.dumps({"acao": nome, **acao},
                       sort_keys=True)
    return hashlib.sha256(
        texto.encode()).hexdigest()[:10]


def precisa_aprovar(sistema, nome, acao):
    risco = REGISTRO[nome][0]
    alto = acao.get("valor", 0) > LIMITE_SEM_APROVACAO
    if risco == "R4" or (risco == "R3" and alto):
        return digital(nome, acao) not in \
            sistema.aprovacoes
    return False


def executar(sistema, sessao, pedido, trilha):
    nome = pedido["nome"]
    args = pedido["args"]
    if nome not in REGISTRO:
        resultado = {"erro": "ferramenta desconhecida"}
    elif nome not in sessao["permitidas"]:
        resultado = {"erro": "ferramenta não permitida"}
    elif set(args) != REGISTRO[nome][1]:
        resultado = {"erro": "campos inválidos"}
    else:
        acao, erro = resolver(sistema, sessao,
                              nome, args)
        if erro or sentido(acao):
            resultado = {"erro": erro or sentido(acao)}
        elif precisa_aprovar(sistema, nome, acao):
            resultado = {"bloqueado": "aprovação",
                         "chave": digital(nome, acao),
                         "valor": acao["valor"]}
        else:
            funcao = getattr(sistema, nome)
            resultado = funcao(sessao, **acao)
    trilha.span("ferramenta", nome=nome,
                resultado=resultado)
    return resultado


def conversar(sistema, sessao, mensagem, modelo,
              max_voltas=5):
    trilha = Trilha(sessao["cliente"])
    trilha.span("mensagem", texto=mensagem)
    memoria = sistema.caderno.ler(sessao["cliente"])
    historico = [{"cliente": mensagem,
                  "memoria": memoria}]
    for volta in range(1, max_voltas + 1):
        pedidos, resposta = modelo(historico)
        trilha.span("modelo", volta=volta,
                    pedidos=[p["nome"] for p in pedidos])
        if not pedidos:
            return "Sucesso", resposta, trilha
        for pedido in pedidos:
            r = executar(sistema, sessao, pedido, trilha)
            historico.append({"pedido": pedido,
                              "resultado": r})
            if "bloqueado" in r:
                return "Bloqueado", r["bloqueado"], trilha
    return "Limite atingido", None, trilha
