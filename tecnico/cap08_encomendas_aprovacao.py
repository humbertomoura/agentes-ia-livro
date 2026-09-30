"""Código extraído do Capítulo 08 — Mão na massa: encomendas com aprovação.

Fonte: Agentes_IA_Essencial_v1.docx
Arquivo gerado automaticamente por scripts/extrair_codigo.py.
Não edite este arquivo manualmente.
"""

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

from dataclasses import dataclass, field
from runtime import executar
 
 
@dataclass
class Execucao:
    sessao: dict                  # quem é o cliente
    vistos: list = field(default_factory=list)
    pendentes: list = field(default_factory=list)
    trilha: list = field(default_factory=list)
    estado: str = "PRONTO"
    resposta: str = ""
    voltas: int = 0
 
 
def resumir(r):
    if not r["ok"]:
        return r["erro"]
    extra = " (repetido)" if r.get("repetido") else ""
    dados = {k: v for k, v in r.items()
             if k not in ("ok", "repetido")}
    return f"{dados}{extra}"
 
 
def continuar(ex, decidir, aprovados, max_voltas=6):
    ex.estado = "EM_ANDAMENTO"
    while ex.voltas < max_voltas:
        if not ex.pendentes:            # pede ao modelo
            pedidos, resposta = decidir(ex.vistos)
            if not pedidos:
                ex.estado = "SUCESSO"
                ex.resposta = resposta
                return ex
            ex.pendentes = list(pedidos)
        while ex.pendentes:             # executa em ordem
            id_p, nome, args = ex.pendentes[0]
            r = executar(nome, args, ex.sessao, id_p,
                         aprovados)
            volta = ex.voltas + 1
            ex.trilha.append(
                f"[{volta}] {id_p} {nome}: {resumir(r)}")
            if r.get("erro") == "PRECISA_APROVACAO":
                ex.estado = "BLOQUEADO"  # para e espera
                return ex
            ex.vistos.append((nome, r))
            ex.pendentes.pop(0)
        ex.voltas += 1
    ex.estado = "LIMITE_ATINGIDO"
    return ex

from controle import Execucao, continuar
 
 
def modelo_simulado(vistos):
    """Finge ser o LLM: devolve (pedidos, resposta)."""
    if not vistos:
        return [("p1", "consultar_agenda",
                 {"dia": "sexta"})], ""
    nome, ultimo = vistos[-1]
    if nome == "consultar_agenda":
        bolo = {"produto": "bolo de cenoura",
                "dia": "sexta"}
        # Por engano, o modelo pede a mesma coisa 2 vezes.
        return [("p2", "registrar_encomenda", bolo),
                ("p3", "registrar_encomenda", bolo)], ""
    return [], f"Encomenda {ultimo['numero']} confirmada!"
 
 
aprovados = set()
ex = Execucao(sessao={"cliente": "Dona Lurdes"})
ex = continuar(ex, modelo_simulado, aprovados)
 
while ex.estado == "BLOQUEADO":
    id_p = ex.pendentes[0][0]
    ex.trilha.append(f"    >> Dona Cida aprovou {id_p}")
    aprovados.add(id_p)        # aprovação humana
    ex = continuar(ex, modelo_simulado, aprovados)
 
for linha in ex.trilha:
    print(linha)
print("estado:", ex.estado)
print("resposta:", ex.resposta)

for pedido in pedidos:
    try:
        args = json.loads(pedido.arguments)
        r = executar(pedido.name, args, sessao,
                     pedido.call_id, aprovados)
    except json.JSONDecodeError:
        r = {"ok": False, "erro": "DADOS_MALFORMADOS"}
    if r.get("erro") == "PRECISA_APROVACAO":
        guardar_pendentes(pedidos, pedido)  # BLOQUEADO
        break
    historico.append({
        "type": "function_call_output",
        "call_id": pedido.call_id,
        "output": json.dumps(r, ensure_ascii=False)})
