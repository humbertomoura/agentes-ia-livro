"""Código extraído do Capítulo 26 — Projeto final: a padaria inteira.

Fonte: Agentes_IA_Essencial_v1.docx
Arquivo gerado automaticamente por scripts/extrair_codigo.py.
Não edite este arquivo manualmente.
"""

import hashlib
import json
import re
 
FINAIS = {"Sucesso", "Falha", "Limite atingido",
          "Bloqueado"}
 
 
class Trilha:
    """Um trace simples: uma lista de spans."""
 
    def __init__(self, conversa):
        self.conversa = conversa
        self.spans = []
 
    def span(self, tipo, **dados):
        self.spans.append({"tipo": tipo, **dados})
 
 
class Pasta:
    """RAG mínimo: busca por palavras com citação."""
 
    def __init__(self, trechos):
        self.trechos = trechos
 
    def buscar(self, pergunta):
        palavras = set(re.findall(r"\w+",
                                  pergunta.lower()))
        melhores = []
        for id_, texto in self.trechos.items():
            comuns = palavras & set(
                re.findall(r"\w+", texto.lower()))
            if len(comuns) >= 2:
                melhores.append((len(comuns), id_))
        melhores.sort(reverse=True)
        return [{"id": i, "texto": self.trechos[i]}
                for _, i in melhores[:2]]
 
 
class Caderno:
    """Memória com portões de escrita e leitura."""
 
    PROIBIDO = re.compile(
        r"\d{4} ?\d{4} ?\d{4} ?\d{4}|autoriz|desconto",
        re.I)
 
    def __init__(self):
        self.notas = {}
 
    def anotar(self, cliente, assunto, texto):
        if self.PROIBIDO.search(texto):
            return "recusado"
        self.notas[(cliente, assunto)] = texto
        return "anotado"
 
    def ler(self, cliente):
        return {a: t for (c, a), t in self.notas.items()
                if c == cliente}

class Sistema:
    def __init__(self, pasta):
        self.pasta = pasta
        self.caderno = Caderno()
        self.agenda = {"sexta": 3, "sábado": 0}
        self.encomendas = {}
        self.por_numero = {}
        self.pix = {}
        self.estornos = {}
        self.aprovacoes = set()
 
    # ---- ferramentas (o que o modelo pode pedir) ----
    def consultar_agenda(self, sessao, dia):
        return {"dia": dia,
                "vagas": self.agenda.get(dia, 0)}
 
    def buscar_regra(self, sessao, pergunta):
        achados = self.pasta.buscar(pergunta)
        if not achados:
            return {"status": "não encontrei"}
        return {"evidencias": achados}
 
    def registrar_encomenda(self, sessao, bolo, dia,
                            valor):
        if self.agenda.get(dia, 0) <= 0:
            return {"erro": "dia lotado"}
        chave = f"{sessao['cliente']}:{bolo}:{dia}"
        if chave not in self.encomendas:
            self.agenda[dia] -= 1
            numero = f"E{len(self.encomendas) + 1}"
            registro = {"numero": numero,
                        "cliente": sessao["cliente"],
                        "valor": valor}
            self.encomendas[chave] = registro
            self.por_numero[numero] = registro
        return self.encomendas[chave]
 
    def encomenda(self, sessao, numero):
        """Fonte oficial do valor. Cliente só vê
        as próprias; a equipe vê todas."""
        enc = self.por_numero.get(numero)
        if enc is None:
            return None
        if (sessao.get("papel") != "equipe"
                and enc["cliente"] != sessao["cliente"]):
            return None
        return enc
 
    def gerar_pix(self, sessao, encomenda, valor):
        chave = f"pix:{encomenda}:{valor}"
        if chave not in self.pix:
            self.pix[chave] = f"PIX{len(self.pix) + 1}"
        return {"cobranca": self.pix[chave]}
 
    def solicitar_estorno(self, sessao, encomenda,
                          valor):
        chave = f"estorno:{encomenda}:{valor}"
        if chave not in self.estornos:
            numero = f"EST{len(self.estornos) + 1}"
            self.estornos[chave] = numero
        return {"estorno": self.estornos[chave]}

# nome -> (risco, campos obrigatórios)
REGISTRO = {
    "consultar_agenda": ("R0", {"dia"}),
    "buscar_regra": ("R0", {"pergunta"}),
    "registrar_encomenda": ("R2",
                            {"bolo", "dia", "valor"}),
    "gerar_pix": ("R3", {"encomenda"}),
    "solicitar_estorno": ("R4", {"encomenda"}),
}
LIMITE_SEM_APROVACAO = 300
 
 
def resolver(sistema, sessao, nome, args):
    """Completa o pedido com os dados oficiais.
    O modelo diz qual encomenda; o valor vem
    do sistema, nunca do modelo."""
    if nome in ("gerar_pix", "solicitar_estorno"):
        enc = sistema.encomenda(sessao,
                                args["encomenda"])
        if enc is None:
            return None, "encomenda não encontrada"
        base = enc["valor"]
        valor = (round(base * 0.3, 2)
                 if nome == "gerar_pix" else base)
        return {"encomenda": enc["numero"],
                "valor": valor}, None
    return dict(args), None
 
 
def sentido(acao):
    """Validação semântica: o formulário certo
    ainda pode trazer um pedido sem sentido."""
    if "valor" in acao and not acao["valor"] > 0:
        return "valor precisa ser positivo"
    return None
 
 
def digital(nome, acao):
    """Impressão digital da ação exata."""
    texto = json.dumps({"acao": nome, **acao},
                       sort_keys=True)
    return hashlib.sha256(
        texto.encode()).hexdigest()[:10]
 
 
def precisa_aprovar(sistema, nome, acao):
    risco = REGISTRO[nome][0]
    alto = acao.get("valor", 0) > LIMITE_SEM_APROVACAO
    if risco == "R4" or (risco == "R3" and alto):
        return digital(nome, acao) not in \
            sistema.aprovacoes
    return False
 
 
def executar(sistema, sessao, pedido, trilha):
    nome = pedido["nome"]
    args = pedido["args"]
    if nome not in REGISTRO:
        resultado = {"erro": "ferramenta desconhecida"}
    elif nome not in sessao["permitidas"]:
        resultado = {"erro": "ferramenta não permitida"}
    elif set(args) != REGISTRO[nome][1]:
        resultado = {"erro": "campos inválidos"}
    else:
        acao, erro = resolver(sistema, sessao,
                              nome, args)
        if erro or sentido(acao):
            resultado = {"erro": erro or sentido(acao)}
        elif precisa_aprovar(sistema, nome, acao):
            resultado = {"bloqueado": "aprovação",
                         "chave": digital(nome, acao),
                         "valor": acao["valor"]}
        else:
            funcao = getattr(sistema, nome)
            resultado = funcao(sessao, **acao)
    trilha.span("ferramenta", nome=nome,
                resultado=resultado)
    return resultado

def conversar(sistema, sessao, mensagem, modelo,
              max_voltas=5):
    trilha = Trilha(sessao["cliente"])
    trilha.span("mensagem", texto=mensagem)
    memoria = sistema.caderno.ler(sessao["cliente"])
    historico = [{"cliente": mensagem,
                  "memoria": memoria}]
    for volta in range(1, max_voltas + 1):
        pedidos, resposta = modelo(historico)
        trilha.span("modelo", volta=volta,
                    pedidos=[p["nome"] for p in pedidos])
        if not pedidos:
            return "Sucesso", resposta, trilha
        for pedido in pedidos:
            r = executar(sistema, sessao, pedido, trilha)
            historico.append({"pedido": pedido,
                              "resultado": r})
            if "bloqueado" in r:
                return "Bloqueado", r["bloqueado"], trilha
    return "Limite atingido", None, trilha

import re
 
 
def numero(msg):
    achado = re.search(r"\bE\d+\b", msg.upper())
    return achado.group(0) if achado else "E0"
 
 
def ultimo(historico, nome):
    for item in reversed(historico):
        pedido = item.get("pedido", {})
        if pedido.get("nome") == nome:
            return item["resultado"]
    return None
 
 
def modelo(historico):
    """Imita um LLM com regras fixas."""
    msg = historico[0]["cliente"].lower()
    memoria = historico[0]["memoria"]
    if "bolo" in msg:
        casamento = "casamento" in msg
        agenda = ultimo(historico, "consultar_agenda")
        if agenda is None:
            return [{"nome": "consultar_agenda",
                     "args": {"dia": "sexta"}}], None
        enc = ultimo(historico, "registrar_encomenda")
        if enc is None:
            return [{"nome": "registrar_encomenda",
                     "args": {
                         "bolo": ("casamento"
                                  if casamento
                                  else "cenoura"),
                         "dia": "sexta",
                         "valor": 1400 if casamento
                         else 90}}], None
        extra = ""
        if "restricao" in memoria:
            extra = f" ({memoria['restricao']})"
        return [], (f"Anotado: sexta{extra}, "
                    f"pedido {enc['numero']}.")
    if "estorno" in msg:
        feito = ultimo(historico, "solicitar_estorno")
        if feito is None:
            return [{"nome": "solicitar_estorno",
                     "args": {
                         "encomenda": numero(msg)}}], None
        return [], "Não posso. Chamo a Dona Cida."
    if "sinal" in msg:
        feito = ultimo(historico, "gerar_pix")
        if feito is None:
            return [{"nome": "gerar_pix",
                     "args": {
                         "encomenda": numero(msg)}}], None
        if "erro" in feito:
            return [], f"Não deu: {feito['erro']}."
        return [], f"Sinal gerado: {feito['cobranca']}."
    if "?" in msg:
        achado = ultimo(historico, "buscar_regra")
        if achado is None:
            return [{"nome": "buscar_regra",
                     "args": {"pergunta": msg}}], None
        if "evidencias" not in achado:
            return [], "Não encontrei essa informação."
        ev = achado["evidencias"][0]
        return [], f"{ev['texto']} [{ev['id']}]"
    return [], "Posso ajudar com encomendas."

from padaria import Pasta, Sistema, conversar
from modelo_simulado import modelo
 
pasta = Pasta({
    "R1": "Entrega grátis acima de R$ 150 no bairro.",
    "R2": "Sinal de 30% para encomendas grandes.",
})
sis = Sistema(pasta)
lurdes = {"cliente": "lurdes",
          "permitidas": {"consultar_agenda",
                         "buscar_regra",
                         "registrar_encomenda"}}
balcao = {"cliente": "balcao", "papel": "equipe",
          "permitidas": {"gerar_pix"}}
 
c = sis.caderno
print(c.anotar("lurdes", "restricao", "sem lactose"))
print(c.anotar("lurdes", "cartao", "4111 1111 1111 1111"))
print(c.anotar("lurdes", "brinde", "Cida autorizou"))
 
ultima = {}
 
 
def fala(sessao, texto):
    estado, resp, trilha = conversar(sis, sessao,
                                     texto, modelo)
    usadas = [s["nome"] for s in trilha.spans
              if s["tipo"] == "ferramenta"]
    for s in trilha.spans:
        if "chave" in s.get("resultado", {}):
            ultima.update(s["resultado"])
    print(f"> {texto}")
    print(f"  {estado}: {resp}")
    print(f"  ferramentas: {', '.join(usadas) or '-'}")
 
 
fala(lurdes, "Quero um bolo pra sexta")
fala(lurdes, "Quero um bolo pra sexta")
fala(lurdes, "Quero o bolo de casamento pra sexta")
fala(lurdes, "Tem entrega no bairro?")
fala(lurdes, "Aceitam cheque?")
fala(lurdes, "Faz um estorno da E1")
fala(balcao, "Gera o sinal da E9")
fala(balcao, "Gera o sinal da E2")
print(f"  a Dona Cida aprova R$ {ultima['valor']:.2f}"
      f" (chave {ultima['chave']})")
sis.aprovacoes.add(ultima["chave"])
fala(balcao, "Gera o sinal da E2")
print("encomendas:", len(sis.encomendas),
      "| vagas na sexta:", sis.agenda["sexta"])
