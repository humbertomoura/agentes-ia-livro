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
