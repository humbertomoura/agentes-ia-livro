import re
from busca import permitidos
from lexical import busca_por_palavras
from significado import busca_por_significado

def juntar(*listas, k=60):
    """Fusão pela posição (RRF): não compara notas."""
    total = {}
    for lista in listas:
        for pos, (doc, _) in enumerate(lista, start=1):
            total[doc] = total.get(doc, 0) + 1 / (k + pos)
    return sorted(total, key=total.get, reverse=True)

def buscar(pergunta, perfil, limite=3):
    docs = permitidos(perfil)
    ordem = juntar(busca_por_palavras(pergunta, docs),
                   busca_por_significado(pergunta, docs))
    return [{"id": f"E{n}", "fonte": d[0], "texto": d[1]}
            for n, d in enumerate(ordem[:limite], 1)]

def responder(pergunta, perfil, gerar):
    evidencias = buscar(pergunta, perfil)
    if not evidencias:
        return "NÃO ENCONTREI", "Não achei na pasta."
    resposta = gerar(pergunta, evidencias)
    citadas = set(re.findall(r"\[(E\d+)\]", resposta))
    existem = {e["id"] for e in evidencias}
    if not citadas or citadas - existem:
        return "RESPOSTA SEM FONTE VÁLIDA", resposta
    return "OK", resposta
