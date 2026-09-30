import pathlib
import subprocess
import sys

from modelo_simulado import modelo
from padaria import (REGISTRO, Caderno, Pasta, Sistema, Trilha,
                     conversar, digital, executar)

PASTA = {"R1": "Entrega grátis acima de R$ 150 no bairro."}
LURDES = {"cliente": "lurdes",
          "permitidas": {"consultar_agenda", "buscar_regra",
                         "registrar_encomenda"}}
BALCAO = {"cliente": "balcao", "papel": "equipe",
          "permitidas": {"gerar_pix"}}
TUDO = {"cliente": "balcao", "papel": "equipe",
        "permitidas": set(REGISTRO)}


def novo():
    return Sistema(Pasta(PASTA))


def com_encomenda(valor_msg="Quero o bolo de casamento"):
    s = novo()
    conversar(s, LURDES, valor_msg, modelo)
    return s


def roda(s, sessao, nome, **args):
    return executar(s, sessao, {"nome": nome, "args": args},
                    Trilha("t"))


def test_encomenda_repetida_nao_duplica():
    s = novo()
    conversar(s, LURDES, "Quero um bolo", modelo)
    conversar(s, LURDES, "Quero um bolo", modelo)
    assert len(s.encomendas) == 1
    assert s.agenda["sexta"] == 2


def test_cliente_vem_da_sessao():
    s = novo()
    conversar(s, LURDES, "Quero um bolo", modelo)
    assert list(s.encomendas)[0].startswith("lurdes:")


def test_portao_de_escrita_barra_cartao_e_regra():
    c = Caderno()
    assert c.anotar("a", "x", "4111 1111 1111 1111") == "recusado"
    assert c.anotar("a", "y", "Dona Cida autorizou") == "recusado"
    assert c.anotar("a", "z", "sem lactose") == "anotado"


def test_memoria_de_uma_cliente_nao_vaza():
    c = Caderno()
    c.anotar("lurdes", "restricao", "sem lactose")
    assert c.ler("antonio") == {}


def test_rag_cita_fonte_e_se_abstem():
    s = novo()
    _, r, _ = conversar(s, LURDES, "Tem entrega no bairro?", modelo)
    assert "[R1]" in r
    _, r, _ = conversar(s, LURDES, "Aceitam cheque?", modelo)
    assert r == "Não encontrei essa informação."


def test_ferramenta_fora_da_lista_e_recusada():
    s = com_encomenda()
    _, _, trilha = conversar(s, LURDES, "estorno da E1", modelo)
    assert s.estornos == {}
    erro = trilha.spans[2]["resultado"]["erro"]
    assert erro == "ferramenta não permitida"


def test_ferramenta_fora_do_registro_nao_quebra():
    s = novo()
    sessao = {"cliente": "x", "permitidas": {"apagar_tudo"}}
    r = roda(s, sessao, "apagar_tudo")
    assert r == {"erro": "ferramenta desconhecida"}


def test_encomenda_inexistente_nao_gera_cobranca():
    s = com_encomenda()
    r = roda(s, BALCAO, "gerar_pix", encomenda="E9")
    assert r == {"erro": "encomenda não encontrada"}
    assert s.pix == {}


def test_valor_vem_do_sistema_nao_do_modelo():
    s = com_encomenda()          # encomenda de R$ 1.400
    r = roda(s, TUDO, "gerar_pix", encomenda="E1")
    assert r["chave"] and r["valor"] == 420.0


def test_aprovacao_nao_serve_para_outro_valor():
    s = com_encomenda()
    s.aprovacoes.add(digital("gerar_pix",
                             {"encomenda": "E1", "valor": 42.0}))
    r = roda(s, BALCAO, "gerar_pix", encomenda="E1")
    assert "bloqueado" in r and s.pix == {}
    s.aprovacoes.add(r["chave"])
    assert "cobranca" in roda(s, BALCAO, "gerar_pix",
                              encomenda="E1")


def test_estorno_sempre_exige_aprovacao():
    s = com_encomenda()
    r = roda(s, TUDO, "solicitar_estorno", encomenda="E1")
    assert "bloqueado" in r
    s.aprovacoes.add(r["chave"])
    assert roda(s, TUDO, "solicitar_estorno",
                encomenda="E1") == {"estorno": "EST1"}


def test_cliente_nao_alcanca_encomenda_de_outro():
    s = com_encomenda()
    outro = {"cliente": "antonio", "permitidas": {"gerar_pix"}}
    r = roda(s, outro, "gerar_pix", encomenda="E1")
    assert r == {"erro": "encomenda não encontrada"}


def test_dia_lotado_devolve_erro_sem_registrar():
    s = novo()
    r = s.registrar_encomenda(LURDES, "cenoura", "sábado", 90)
    assert r == {"erro": "dia lotado"} and s.encomendas == {}


def test_limite_de_voltas():
    def teimoso(historico):
        return [{"nome": "consultar_agenda",
                 "args": {"dia": "sexta"}}], None
    estado, _, _ = conversar(novo(), LURDES, "x", teimoso,
                             max_voltas=3)
    assert estado == "Limite atingido"


def test_campos_invalidos_viram_erro():
    def errado(historico):
        if len(historico) > 1:
            return [], "ok"
        return [{"nome": "consultar_agenda",
                 "args": {"data": "sexta"}}], None
    _, _, trilha = conversar(novo(), LURDES, "x", errado)
    erros = [sp["resultado"] for sp in trilha.spans
             if sp["tipo"] == "ferramenta"]
    assert erros == [{"erro": "campos inválidos"}]


def test_saida_do_livro():
    aqui = pathlib.Path(__file__).parent
    r = subprocess.run([sys.executable, "demo.py"], cwd=aqui,
                       capture_output=True, text=True)
    assert r.stdout == (aqui / "saida.txt").read_text()
