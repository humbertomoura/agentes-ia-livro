import pytest
from casamento import (Armazem, Forno, Pix, Workflow,
                       versao)


def novo():
    ctx = {"forno": Forno(), "pix": Pix()}
    return Workflow(Armazem(), ctx), ctx


def pedido(valor=1400, **extra):
    p = {"id": "E1", "salgados": 200, "andares": 3,
         "dia": "14/11", "valor": valor}
    p.update(extra)
    return p


def test_pedido_pequeno_segue_sem_aprovacao():
    wf, ctx = novo()
    e = wf.iniciar(pedido(valor=800))
    assert e["status"] == "Sucesso"
    assert e["aprovado_por"] == "regra"


def test_pedido_grande_espera_aprovacao():
    wf, _ = novo()
    e = wf.iniciar(pedido())
    assert e["status"] == "Bloqueado"
    assert e["trilha"] == ["conferir", "calcular"]


def test_aprovacao_de_versao_antiga_nao_vale():
    wf, _ = novo()
    wf.iniciar(pedido())
    vista = wf.versao_atual("E1")
    wf.alterar("E1", salgados=300, valor=1900)
    e = wf.aprovar("E1", "dona_cida", vista)
    assert e["status"] == "Bloqueado"
    assert "mudou" in e["motivo"]


def test_quem_nao_tem_autoridade_nao_aprova():
    wf, _ = novo()
    wf.iniciar(pedido())
    with pytest.raises(PermissionError):
        wf.aprovar("E1", "julia", wf.versao_atual("E1"))


def test_retomada_nao_duplica_efeitos():
    wf, ctx = novo()
    wf.iniciar(pedido())
    ctx["cair_em"] = "cobrar"
    with pytest.raises(RuntimeError):
        wf.aprovar("E1", "dona_cida", wf.versao_atual("E1"))
    e = Workflow(wf.armazem, ctx).rodar("E1")
    assert e["status"] == "Sucesso"
    assert len(ctx["pix"].cobrancas) == 1
    assert len(ctx["forno"].reservas) == 1


def test_rodar_de_novo_apos_sucesso_nao_faz_nada():
    wf, ctx = novo()
    wf.iniciar(pedido(valor=500))
    e = wf.rodar("E1")
    assert e["status"] == "Sucesso"
    assert len(ctx["pix"].cobrancas) == 1


def test_quantidade_invalida_falha_sem_efeito():
    wf, ctx = novo()
    e = wf.iniciar(pedido(salgados=0, valor=500))
    assert e["status"] == "Falha"
    assert ctx["forno"].reservas == {}


def test_cancelar_compensa_efeitos():
    wf, ctx = novo()
    e = wf.iniciar(pedido(valor=500))
    e = wf.cancelar("E1")
    assert e["status"] == "Cancelado"
    assert ctx["forno"].liberadas == {e["reserva"]}
    assert ctx["pix"].estornos == {e["cobranca"]}


def test_alterar_so_com_pedido_pausado():
    wf, _ = novo()
    wf.iniciar(pedido(valor=500))
    with pytest.raises(ValueError):
        wf.alterar("E1", salgados=10)


def test_versao_muda_com_qualquer_campo():
    assert versao(pedido()) != versao(pedido(dia="15/11"))


def test_saida_do_livro():
    import subprocess, sys, pathlib
    aqui = pathlib.Path(__file__).parent
    r = subprocess.run([sys.executable, "demo.py"], cwd=aqui,
                       capture_output=True, text=True)
    assert r.stdout == (aqui / "saida.txt").read_text()
