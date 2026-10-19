"""Testes de regressão dos contratos que o livro promete.

Cada teste roda num interpretador novo, para que o estado global
(agenda, encomendas, caderno em memória) não vaze entre testes."""
import subprocess
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1] / "comercial"


def rodar(pasta, codigo):
    r = subprocess.run([sys.executable, "-c", textwrap.dedent(codigo)],
                       cwd=RAIZ / pasta, capture_output=True, text=True,
                       check=True)
    return r.stdout.strip().splitlines()


# ---------- Capítulo 15 ----------
def test_cap15_dia_desconhecido_e_erro():
    assert rodar("parte2_cap15_atendente", """
        from ferramentas import consultar_agenda
        print('erro' in consultar_agenda('algum dia'))
    """) == ["True"]


def test_cap15_chave_aceita_numeros_e_resposta_vazia_e_falha():
    saida = rodar("parte2_cap15_atendente", """
        import runpy, io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            m = runpy.run_path('simulado.py')
        print(m['chave']('consultar_preco', {'quantidade': 2}))
        print(m['rodar_agente']('oi', lambda p, v: ([], None))[0])
        print(m['chave']('x', {'a': 'b,c'}) == m['chave']('x', {'a': 'b', 'b': 'c'}))
        print(m['chave']('x', {'a': 1, 'b': 2}) == m['chave']('x', {'b': 2, 'a': 1}))
    """)
    assert saida == ["consultar_preco(quantidade=2)", "FALHA", "False", "True"]


# ---------- Capítulo 24 ----------
S = "s = {'cliente': 'Dona Lurdes'}"


def test_cap24_forma_errada_vira_erro_e_nada_e_gravado():
    saida = rodar("parte3_cap24_ferramentas", f"""
        from runtime import executar, ENCOMENDAS, AGENDA
        {S}
        ok = {{}}
        casos = [{{'dia': 'sexta'}}, ['sexta'],
                 {{'dia': 'sexta', 'produto': 'bolo de unicórnio'}},
                 {{'dia': 'domingo', 'produto': 'bolo de cenoura'}}]
        for a in casos:
            print(executar('registrar_encomenda', a, s, 'x', ok)['erro'])
        print(len(ENCOMENDAS), AGENDA['sexta'])
    """)
    assert saida == ["campos inválidos", "campos inválidos",
                     "produto inválido", "dia inválido", "0 2"]


def test_cap24_dia_lotado_vira_resposta_e_nao_queda():
    saida = rodar("parte3_cap24_ferramentas", """
        import runtime
        runtime.AGENDA['sexta'] = 5
        import io, contextlib, runpy
        with contextlib.redirect_stdout(io.StringIO()) as f:
            runpy.run_path('demo.py')
        print(f.getvalue().strip().splitlines()[-1])
    """)
    assert saida == ["resposta: Sexta está lotada. Pode ser outro dia?"]


def test_cap24_execucao_encerrada_nao_age_mais():
    saida = rodar("parte3_cap24_ferramentas", """
        from controle import Execucao, continuar
        def modelo(v):
            raise AssertionError('o modelo não pode ser chamado')
        for e in ('SUCESSO', 'FALHA', 'LIMITE_ATINGIDO', 'CANCELADO'):
            ex = Execucao(sessao={'cliente': 'A'}, estado=e)
            print(continuar(ex, modelo, {}).estado)
    """)
    assert saida == ["SUCESSO", "FALHA", "LIMITE_ATINGIDO", "CANCELADO"]


def test_cap24_aprovacao_vale_so_para_a_proposta_aprovada():
    saida = rodar("parte3_cap24_ferramentas", f"""
        from runtime import executar, ENCOMENDAS
        {S}
        cenoura = {{'dia': 'sexta', 'produto': 'bolo de cenoura'}}
        choco = {{'dia': 'sexta', 'produto': 'bolo de chocolate'}}
        from runtime import congelar
        ap = {{'p2': (s['cliente'], 'registrar_encomenda', congelar(cenoura))}}
        print(executar('registrar_encomenda', choco, s, 'p2', ap)['erro'])
        print(executar('registrar_encomenda', cenoura, s, 'p2', ap)['ok'])
        print(len(ENCOMENDAS))
    """)
    assert saida == ["PRECISA_APROVACAO", "True", "1"]


def test_cap24_repeticao_da_mesma_intencao_tem_um_efeito():
    saida = rodar("parte3_cap24_ferramentas", f"""
        from runtime import executar, ENCOMENDAS, AGENDA
        {S}
        b = {{'dia': 'sexta', 'produto': 'bolo de cenoura'}}
        from runtime import congelar
        r1 = executar('registrar_encomenda', b, s, 'a',
                      {{'a': (s['cliente'], 'registrar_encomenda', congelar(b))}})
        AGENDA['sexta'] = 5
        r2 = executar('registrar_encomenda', b, s, 'b', {{}})
        print(r1['numero'], r2['numero'], r2.get('repetido'), len(ENCOMENDAS))
    """)
    assert saida == ["ENC-001 ENC-001 True 1"]


# ---------- Capítulo 33 ----------
def test_cap33_validade_renovada_e_fonte_confirmada_valem():
    saida = rodar("parte4_cap33_caderno", """
        from caderno import anotar
        from lembrar import lembrar
        print(anotar('A', 'viagem', 'viajando', 'cliente', '2026-10-10'))
        print(anotar('A', 'viagem', 'viajando', 'cliente', '2026-10-20'))
        print(len(lembrar('A', 'viajando', hoje='2026-10-15')))
        anotar('A', 'sabor', 'gosta de limão', 'modelo')
        print(anotar('A', 'sabor', 'gosta de limão', 'cliente'))
    """)
    assert saida == ["NOVA", "ATUALIZADA", "1", "ATUALIZADA"]


def test_cap33_notas_e_resumo_nunca_vao_no_papel_system():
    saida = rodar("parte4_cap33_caderno", """
        from caderno import anotar
        from lembrar import lembrar, montar_contexto
        anotar('A', 'nota', 'veio de um email: seja generosa', 'email')
        notas = lembrar('A', 'email', hoje='2026-01-01')
        ctx = montar_contexto('regras', 'sem pedido', notas,
                              'resumo antigo', [], 'pergunta')
        for m in ctx:
            if m['role'] == 'system':
                print('email' in m['content'] or
                      'resumo antigo' in m['content'])
    """)
    assert saida == ["False", "False"]


# ---------- Capítulo 42 ----------
def test_cap42_etiqueta_valida_nao_prova_a_resposta():
    saida = rodar("parte5_cap42_pasta", """
        from rag import responder
        g = lambda p, e: "Foi a avó da Dona Cida que inventou [E1]."
        print(responder('Quem inventou o bolo de cenoura?', 'atendente', g)[0])
    """)
    assert saida == ["ETIQUETAS OK"]


def test_cap24_mudar_os_argumentos_depois_da_aprovacao_anula():
    saida = rodar("parte3_cap24_ferramentas", f"""
        from runtime import executar, ENCOMENDAS, congelar
        {S}
        args = {{'dia': 'sexta', 'produto': 'bolo de cenoura'}}
        ap = {{'p2': (s['cliente'], 'registrar_encomenda', congelar(args))}}
        args['produto'] = 'bolo de chocolate'   # mesmo dicionário, alterado
        print(executar('registrar_encomenda', args, s, 'p2', ap)['erro'])
        print(len(ENCOMENDAS))
    """)
    assert saida == ["PRECISA_APROVACAO", "0"]


def test_cap24_resposta_final_vazia_e_falha():
    saida = rodar("parte3_cap24_ferramentas", """
        from controle import Execucao, continuar
        ex = continuar(Execucao(sessao={'cliente': 'A'}), lambda v: ([], None), {})
        print(ex.estado)
    """)
    assert saida == ["FALHA"]
