"""Diário: um trade por vez, com o gráfico gerado dos candles da XM e o formulário de anotação."""
import pandas as pd
import streamlit as st

import comum
from lhsquant.diario import banco, grafico_trade, importar_mt5

st.title("Diário de trading")
df = comum.dados_filtrados()
if df.empty:
    st.info("Nenhum trade neste filtro. Sincronize a conta primeiro.")
    st.stop()

df = df.sort_values("entrada", ascending=False).reset_index(drop=True)
so_pendentes = st.toggle("Mostrar só trades sem anotação", value=False)
lista = df[df["motivo"].isna() & df["nota"].isna()] if so_pendentes else df
if lista.empty:
    st.success("Todos os trades deste filtro já estão anotados.")
    st.stop()


def rotulo(i):
    t = lista.loc[i]
    return (f"{t['entrada']:%d/%m/%y %H:%M} · {t['simbolo']} {t['lado']} · {comum.num(t['liquido'])}"
            f" · {t['setup']}")


ids = list(lista.index)
pos = st.session_state.get("pos_diario", 0)
pos = min(pos, len(ids) - 1)
c_ant, c_sel, c_prox = st.columns([1, 8, 1])
if c_ant.button("◀", help="Trade mais recente", width="stretch", disabled=pos == 0):
    pos -= 1
if c_prox.button("▶", help="Trade mais antigo", width="stretch", disabled=pos >= len(ids) - 1):
    pos += 1
escolhido = c_sel.selectbox("Trade", ids, index=pos, format_func=rotulo, label_visibility="collapsed")
st.session_state["pos_diario"] = ids.index(escolhido)
t = lista.loc[escolhido].to_dict()

# ---- números do trade ----
cols = st.columns(6)
duracao = t["saida"] - t["entrada"]
horas, minutos = divmod(int(duracao.total_seconds() // 60), 60)
with cols[0]:
    comum.card("Resultado líquido", comum.num(t["liquido"]), comum.cor(t["liquido"]),
               f"bruto {comum.num(t['lucro'])} · custos {comum.num(t['comissao'] + t['swap'] + t['taxa'])}")
with cols[1]:
    comum.card("Múltiplo de R", comum.num(t["R"], sufixo="R"), comum.cor(t["R"]),
               "sem stop: informe o SL abaixo" if pd.isna(t["R"]) else f"risco {comum.num(t['risco'], sinal=False)}")
with cols[2]:
    comum.card("Entrada → saída", f"{t['preco_entrada']:.5g} → {t['preco_saida']:.5g}", sub=f"{t['lado']} {t['lote']:g} lote")
with cols[3]:
    comum.card("Duração", f"{horas}h{minutos:02d}", sub=f"{t['entrada']:%d/%m %H:%M} (Brasília)")
with cols[4]:
    sl_txt = "—" if pd.isna(t["sl_final"]) else f"{t['sl_final']:.5g}"
    comum.card("Saída", t["motivo_saida"], sub=f"SL {sl_txt}")
with cols[5]:
    comum.card("Sessão", t["sessao"], sub=f"{t['dia_semana']} · {t['hora']}h")

# ---- gráfico ----
tf = st.segmented_control("Timeframe do gráfico", ["Auto", "M5", "M15", "H1", "H4"], default="Auto")
with st.spinner("Montando gráfico com os candles da XM..."):
    fig = grafico_trade.figura(t, None if tf in (None, "Auto") else tf)
st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

# ---- anotação ----
nota_atual = banco.anotacao(t["login"], t["position_id"])
nomes_setups = list(importar_mt5.setups())
setup_atual = nota_atual.get("setup") or t.get("setup_auto")
opcoes_setup = nomes_setups + ([setup_atual] if setup_atual and setup_atual not in nomes_setups else [])

st.subheader("Anotação do trade")
with st.form(f"anotacao_{t['login']}_{t['position_id']}"):
    a1, a2 = st.columns(2)
    setup = a1.selectbox("Setup", opcoes_setup, index=opcoes_setup.index(setup_atual) if setup_atual else None,
                         placeholder="Escolha o setup", accept_new_options=True)
    sl_corrigido = a2.number_input(
        "SL inicial (corrigir se o importado estiver errado ou vazio)", value=nota_atual.get("sl_corrigido"),
        format="%.5f", step=0.0001, placeholder=f"importado: {'nenhum' if pd.isna(t['sl']) else t['sl']}")
    motivo = st.text_area("Motivo da entrada", value=nota_atual.get("motivo") or "",
                          placeholder="O que o setup mostrou? Qual era o plano de saída?")
    b1, b2 = st.columns(2)
    plano_atual = nota_atual.get("seguiu_plano")
    seguiu = b1.radio("Seguiu o plano?", ["Sim", "Não"], horizontal=True,
                      index=None if plano_atual is None else (0 if plano_atual else 1))
    nota = b2.slider("Nota da execução", 1, 5, value=nota_atual.get("nota") or 3,
                     help="1 = execução ruim · 5 = execução perfeita (independe do resultado)")
    emocoes = st.multiselect("Emoções / estado mental", sorted(set(banco.EMOCOES) | set(nota_atual.get("emocoes", []))),
                             default=nota_atual.get("emocoes", []), accept_new_options=True)
    erros = st.multiselect("Erros", sorted(set(banco.ERROS) | set(nota_atual.get("erros", []))),
                           default=nota_atual.get("erros", []), accept_new_options=True)
    licao = st.text_area("Lição", value=nota_atual.get("licao") or "")
    if st.form_submit_button("Salvar anotação", type="primary", icon=":material/save:"):
        banco.salvar_anotacao(t["login"], t["position_id"], setup=setup, sl_corrigido=sl_corrigido,
                              motivo=motivo or None, seguiu_plano=None if seguiu is None else int(seguiu == "Sim"),
                              nota=nota, emocoes=emocoes, erros=erros, licao=licao or None)
        comum.recarregar()
        st.success("Anotação salva.")
        st.rerun()

# ---- resumo do dia ----
dia = t["entrada"].date()
st.subheader(f"Resumo do dia {dia:%d/%m/%Y}")
do_dia = df[df["entrada"].dt.date == dia]
st.caption(f"{len(do_dia)} trades · líquido {comum.num(do_dia['liquido'].sum())} · "
           f"{comum.num(do_dia['R'].sum(), sufixo='R')}")
texto = st.text_area("Como foi o dia", value=banco.resumo_do_dia(t["login"], dia), key=f"resumo_{t['login']}_{dia}",
                     label_visibility="collapsed", placeholder="Contexto do mercado, disciplina, o que repetir e o que evitar...")
if st.button("Salvar resumo do dia", icon=":material/save:"):
    banco.salvar_resumo_dia(t["login"], dia, texto)
    st.success("Resumo do dia salvo.")
