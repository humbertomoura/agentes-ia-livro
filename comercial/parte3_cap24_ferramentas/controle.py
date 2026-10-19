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


FINAIS = {"SUCESSO", "FALHA", "LIMITE_ATINGIDO", "CANCELADO"}


def continuar(ex, decidir, aprovados, max_voltas=6):
    if ex.estado in FINAIS:     # execução encerrada não age mais
        return ex
    ex.estado = "EM_ANDAMENTO"
    while ex.voltas < max_voltas:
        if not ex.pendentes:            # pede ao modelo
            pedidos, resposta = decidir(ex.vistos)
            if not pedidos:             # o modelo terminou
                ex.estado = "SUCESSO" if resposta else "FALHA"
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
