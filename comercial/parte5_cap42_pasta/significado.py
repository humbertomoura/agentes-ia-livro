from busca import palavras

# "Embedding de brinquedo": palavras relacionadas
# caem no mesmo conceito.
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
