"""Código extraído do Capítulo 11 — Mão na massa: respostas com fonte.

Fonte: Agentes_IA_Essencial_v1.docx
Arquivo gerado automaticamente por scripts/extrair_codigo.py.
Não edite este arquivo manualmente.
"""

import math
import re
import unicodedata
from collections import Counter
 
# Palavras que aparecem em tudo e não ajudam a buscar
VAZIAS = {"a", "o", "as", "os", "de", "da", "do", "das",
          "dos", "e", "em", "no", "na", "se", "que", "um",
          "uma", "por", "para", "com", "ao"}
 
def palavras(texto):
    """Minúsculas, sem acento nem pontuação."""
    t = unicodedata.normalize("NFKD", texto)
    t = t.encode("ascii", "ignore").decode().lower()
    return [p for p in re.findall(r"\w+(?:[.-]\w+)*", t)
            if p not in VAZIAS]
 
# A pasta da padaria, já fatiada em trechos
PASTA = [
    ("receita-cenoura",
     "Bolo de cenoura: asse por 40 minutos a 180 graus.",
     "todos"),
    ("manual-forno",
     "Forno FX-200: preaqueça 15 minutos antes "
     "de assar.",
     "todos"),
    ("vigilancia",
     "Ovos devem ficar refrigerados, conforme a RDC 216.",
     "todos"),
    ("contrato-farinha",
     "Atraso na entrega de farinha gera multa de 2%.",
     "gerencia"),
]
 
def permitidos(perfil):
    """Filtro de acesso: antes de qualquer pontuação."""
    return [d for d in PASTA
            if d[2] == "todos" or perfil == "gerencia"]

from busca import palavras, math, Counter
 
def busca_por_palavras(pergunta, docs, k1=1.5, b=0.75):
    """BM25 simplificado, só sobre os permitidos."""
    textos = [palavras(d[1]) for d in docs]
    if not textos:
        return []
    media = sum(map(len, textos)) / len(textos)
    df = Counter(p for t in textos for p in set(t))
    n, notas = len(textos), []
    for doc, t in zip(docs, textos):
        tf, nota = Counter(t), 0.0
        for p in palavras(pergunta):
            if tf[p]:
                idf = math.log(1 + (n - df[p] + .5)
                               / (df[p] + .5))
                norm = 1 - b + b * len(t) / media
                nota += (idf * tf[p] * (k1 + 1)
                         / (tf[p] + k1 * norm))
        if nota > 0:
            notas.append((doc, nota))
    return sorted(notas, key=lambda x: -x[1])

from busca import palavras
 
# "Embedding de brinquedo": palavras diferentes que
# querem dizer a mesma coisa caem no mesmo conceito.
CONCEITOS = {
    "tempo": {"tempo", "minutos", "demora", "quanto"},
    "forno": {"forno", "asse", "assar", "preaqueca"},
    "calor": {"temperatura", "graus", "quente"},
    "frio": {"geladeira", "refrigerados", "gelado"},
    "multa": {"multa", "penalidade", "atrasar", "atraso"},
}
 
def conceitos(texto):
    ws = set(palavras(texto))
    return {c for c, grupo in CONCEITOS.items()
            if ws & grupo}
 
def busca_por_significado(pergunta, docs):
    q = conceitos(pergunta)
    notas = []
    for doc in docs:
        d = conceitos(doc[1])
        if q and d and q & d:
            nota = len(q & d) / (len(q) * len(d)) ** .5
            notas.append((doc, nota))
    return sorted(notas, key=lambda x: -x[1])

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

from rag import buscar, responder
 
def mostrar(pergunta, perfil):
    print(f"\n{perfil}: {pergunta}")
    evidencias = buscar(pergunta, perfil)
    for e in evidencias:
        print(f"  [{e['id']}] {e['fonte']}")
    if not evidencias:
        print("  (nenhuma evidência)")
 
mostrar("Quanto tempo o bolo de cenoura fica no forno?",
        "atendente")
mostrar("Tem multa se a farinha atrasar?", "atendente")
mostrar("Tem multa se a farinha atrasar?", "gerencia")
mostrar("Quem ganhou a Copa de 2002?", "atendente")
 
def modelo_certo(pergunta, evidencias):
    return "Asse por 40 minutos a 180 graus [E1]."
 
def modelo_inventa(pergunta, evidencias):
    return "Asse por 50 minutos [E7]."
 
p = "Quanto tempo o bolo de cenoura fica no forno?"
print()
for gerar in (modelo_certo, modelo_inventa):
    estado, texto = responder(p, "atendente", gerar)
    print(f"{estado}: {texto}")
estado, texto = responder("Quem ganhou a Copa de 2002?",
                          "atendente", modelo_certo)
print(f"{estado}: {texto}")
