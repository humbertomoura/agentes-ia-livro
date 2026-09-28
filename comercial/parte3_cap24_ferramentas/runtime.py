from dataclasses import dataclass

CAPACIDADE = 5
AGENDA = {"sexta": 2, "sábado": 5}  # já marcados
ENCOMENDAS = {}                 # número -> dados
JA_FEITAS = {}                  # intenção -> resultado


# ---------- as ferramentas ----------
def consultar_agenda(args, sessao):
    return {"vagas": CAPACIDADE - AGENDA[args["dia"]]}


def registrar_encomenda(args, sessao):
    numero = f"ENC-{len(ENCOMENDAS) + 1:03d}"
    cliente = sessao["cliente"]     # vem da sessão
    ENCOMENDAS[numero] = {**args, "cliente": cliente}
    AGENDA[args["dia"]] += 1
    return {"numero": numero}


def validar_dia(args):
    if args.get("dia") not in AGENDA:
        return "dia inválido"


def validar_encomenda(args):
    if validar_dia(args):
        return "dia inválido"
    if AGENDA[args["dia"]] >= CAPACIDADE:
        return "dia lotado"


def intencao_encomenda(args, sessao):
    # Mesma cliente + mesmo produto + mesmo dia =
    # mesma intenção, não importa quantas vezes
    # o modelo peça.
    return "|".join([sessao["cliente"],
                     args["produto"], args["dia"]])


# ---------- o registro ----------
@dataclass(frozen=True)
class Ferramenta:
    executar: object
    validar: object
    so_leitura: bool
    precisa_aprovacao: bool = False
    intencao: object = None


REGISTRO = {
    "consultar_agenda": Ferramenta(
        consultar_agenda, validar_dia, so_leitura=True),
    "registrar_encomenda": Ferramenta(
        registrar_encomenda, validar_encomenda,
        so_leitura=False, precisa_aprovacao=True,
        intencao=intencao_encomenda),
}


# ---------- o executor ----------
def executar(nome, args, sessao, id_pedido, aprovados):
    f = REGISTRO.get(nome)
    if f is None:
        return {"ok": False, "erro": "NAO_EXISTE"}
    chave = None
    if f.intencao:
        chave = f.intencao(args, sessao)
    if chave in JA_FEITAS:          # já foi feito?
        return {"ok": True, **JA_FEITAS[chave],
                "repetido": True}
    problema = f.validar(args)      # forma e sentido
    if problema:
        return {"ok": False, "erro": problema}
    if f.precisa_aprovacao and id_pedido not in aprovados:
        return {"ok": False, "erro": "PRECISA_APROVACAO"}
    resultado = f.executar(args, sessao)
    if chave:
        JA_FEITAS[chave] = resultado
    return {"ok": True, **resultado}
