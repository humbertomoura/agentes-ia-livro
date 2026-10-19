import re
import sqlite3

db = sqlite3.connect(":memory:")
db.row_factory = sqlite3.Row
db.execute("""create table caderno (
    id integer primary key, cliente text, assunto text,
    texto text, fonte text, ate text,
    ativa integer default 1, substitui integer)""")

SEGREDO = re.compile(
    r"(?i)(senha|cvv|\d{4}[ .-]?\d{4}[ .-]?\d{4})")
PARECE_REGRA = re.compile(
    r"(?i)(ignor|autoriz|sem aprova|desconto)")


def anotar(cliente, assunto, texto, fonte, ate=None):
    """Portão de escrita: decide o que entra."""
    if SEGREDO.search(texto):
        return "BLOQUEADO (segredo)"
    if PARECE_REGRA.search(texto):
        return "BLOQUEADO (parece regra, não fato)"
    atual = db.execute(
        "select * from caderno where cliente=? and "
        "assunto=? and ativa=1", (cliente, assunto)
    ).fetchone()
    igual = (texto, fonte, ate)
    if atual and tuple(atual[k] for k in (
            "texto", "fonte", "ate")) == igual:
        return "NADA A FAZER"       # nada mudou
    antiga = None
    if atual:                   # não apaga: substitui
        antiga = atual["id"]
        db.execute(
            "update caderno set ativa=0 where id=?",
            (antiga,))
    db.execute(
        "insert into caderno (cliente, assunto, texto, "
        "fonte, ate, substitui) values (?,?,?,?,?,?)",
        (cliente, assunto, texto, fonte, ate, antiga))
    return "ATUALIZADA" if antiga else "NOVA"
