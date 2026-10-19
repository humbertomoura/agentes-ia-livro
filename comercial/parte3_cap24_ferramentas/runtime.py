import json
from dataclasses import dataclass

CAPACIDADE = 5
AGENDA = {"sexta": 2, "sábado": 5}  # já marcados
PRODUTOS = ("bolo de cenoura", "bolo de chocolate")
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


# ---------- as regras ----------
def conferir_forma(args, campos):
    """Forma: exatamente os campos esperados, cada um
    com um dos valores permitidos."""
    if not isinstance(args, dict) or set(args) != set(campos):
        return "campos inválidos"
    for nome, permitidos in campos.items():
        if args[nome] not in permitidos:
            return f"{nome} inválido"


def dia_tem_vaga(args):
    # Sentido: uma regra do negócio que muda com o tempo.
    if AGENDA[args["dia"]] >= CAPACIDADE:
        return "dia lotado"


def intencao_encomenda(args, sessao):
    # Simplificação didática: mesma cliente + mesmo
    # produto + mesmo dia desta semana = mesma intenção.
    # Um sistema real dá a cada encomenda nova um ID de
    # operação e reaproveita esse ID nas repetições.
    return (sessao["cliente"], args["produto"],
            args["dia"])


def congelar(args):
    """Uma cópia canônica e imutável dos argumentos."""
    return json.dumps(args, sort_keys=True, ensure_ascii=False)


# ---------- o registro ----------
@dataclass(frozen=True)
class Ferramenta:
    executar: object
    campos: dict                # campo -> valores permitidos
    so_leitura: bool
    precondicao: object = None
    precisa_aprovacao: bool = False
    intencao: object = None


DIAS = tuple(AGENDA)
REGISTRO = {
    "consultar_agenda": Ferramenta(
        consultar_agenda, {"dia": DIAS}, so_leitura=True),
    "registrar_encomenda": Ferramenta(
        registrar_encomenda, {"dia": DIAS, "produto": PRODUTOS},
        so_leitura=False, precondicao=dia_tem_vaga,
        precisa_aprovacao=True, intencao=intencao_encomenda),
}


# ---------- o executor ----------
def executar(nome, args, sessao, id_pedido, aprovados):
    f = REGISTRO.get(nome)
    if f is None:
        return {"ok": False, "erro": "NAO_EXISTE"}
    problema = conferir_forma(args, f.campos)   # 1. forma
    if problema:
        return {"ok": False, "erro": problema}
    chave = f.intencao(args, sessao) if f.intencao else None
    if chave in JA_FEITAS:                      # 2. já feito?
        return {"ok": True, **JA_FEITAS[chave],
                "repetido": True}
    if f.precondicao:                           # 3. sentido
        problema = f.precondicao(args)
        if problema:
            return {"ok": False, "erro": problema}
    proposta = (sessao["cliente"], nome, congelar(args))
    if (f.precisa_aprovacao                     # 4. aprovação
            and aprovados.get(id_pedido) != proposta):
        return {"ok": False, "erro": "PRECISA_APROVACAO"}
    resultado = f.executar(args, sessao)
    if chave:
        JA_FEITAS[chave] = resultado
    return {"ok": True, **resultado}
