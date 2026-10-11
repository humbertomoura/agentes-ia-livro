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
