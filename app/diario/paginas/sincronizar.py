"""Sincronizar: mostra a conta logada no MT5, importa os trades e marca setups pendentes."""
import streamlit as st

import comum
from lhsquant.diario import banco, importar_mt5

st.title("Sincronizar com a XM")
st.caption("Lê o histórico da conta que está logada no terminal MT5. Só leitura: nenhuma ordem é enviada.")

try:
    conta = importar_mt5.info_conta()
except Exception as e:  # terminal fechado ou sem login
    conta = None
    st.warning(f"MT5 indisponível: {e}. Abra o terminal da XM e recarregue a página.")

if conta:
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        comum.card("Conta logada", conta["tipo"].upper(),
                   comum.C["negativo"] if conta["tipo"] == "real" else comum.C["secundaria"], conta["servidor"])
    with c2:
        comum.card("Login", str(conta["login"]), sub=conta["nome"])
    with c3:
        comum.card("Saldo", comum.num(conta["saldo"], sinal=False), sub=conta["moeda"])
    with c4:
        comum.card("Patrimônio", comum.num(conta["patrimonio"], sinal=False), sub=conta["moeda"])
    st.write("")
    if st.button(f"Sincronizar conta {conta['tipo']} {conta['login']}", type="primary", icon=":material/sync:"):
        with st.spinner("Lendo histórico do MT5..."):
            r = importar_mt5.importar()
        comum.recarregar()
        st.success(f"{r['trades']} trades fechados lidos · {r['novos']} novos no diário.")

contas = banco.contas()
if not contas.empty:
    st.subheader("Contas no diário")
    st.dataframe(contas.rename(columns={"login": "Login", "servidor": "Servidor", "tipo": "Tipo", "moeda": "Moeda",
                                        "nome": "Nome", "ultima_importacao": "Última importação"}),
                 hide_index=True, width="stretch")

# ---- trades sem setup ----
df = comum.dados_filtrados()
if df.empty:
    st.info("Nenhum trade no diário ainda. Clique em Sincronizar.")
    st.stop()

nomes_setups = list(importar_mt5.setups())
pendentes = df[df["setup"] == "sem setup"].sort_values("entrada", ascending=False)
st.subheader(f"Trades sem setup ({len(pendentes)})")
if pendentes.empty:
    st.success("Todos os trades deste filtro já têm setup.")
else:
    st.caption("Escolha o setup de cada trade e clique em Salvar. Os nomes vêm de setups/diario.yaml.")
    editor = pendentes[["position_id", "login", "entrada", "simbolo", "lado", "lote", "liquido", "motivo_saida"]].copy()
    editor.insert(0, "setup", None)
    editado = st.data_editor(
        editor, hide_index=True, width="stretch", disabled=list(editor.columns[1:]),
        column_config={
            "setup": st.column_config.SelectboxColumn("Setup", options=nomes_setups, width="medium"),
            "position_id": st.column_config.NumberColumn("Posição", format="%d"),
            "login": None,
            "entrada": st.column_config.DatetimeColumn("Entrada (Brasília)", format="DD/MM/YY HH:mm"),
            "simbolo": "Ativo", "lado": "Lado", "lote": "Lote",
            "liquido": st.column_config.NumberColumn("Líquido", format="%.2f"),
            "motivo_saida": "Saída",
        })
    if st.button("Salvar setups", icon=":material/save:"):
        marcados = editado.dropna(subset=["setup"])
        for linha in marcados.itertuples():
            banco.salvar_anotacao(linha.login, linha.position_id, setup=linha.setup)
        comum.recarregar()
        st.success(f"{len(marcados)} trades marcados.")
        st.rerun()

st.subheader("Últimos trades")
ultimos = df.sort_values("entrada", ascending=False).head(15)
comum.tabela(ultimos[["entrada", "simbolo", "lado", "lote", "setup", "liquido", "R", "motivo_saida", "sessao"]]
             .assign(entrada=lambda x: x["entrada"].dt.strftime("%d/%m/%y %H:%M"))
             .rename(columns={"entrada": "Entrada", "simbolo": "Ativo", "lado": "Lado", "lote": "Lote",
                              "setup": "Setup", "liquido": "Líquido", "motivo_saida": "Saída", "sessao": "Sessão"}),
             cols_dinheiro=["Líquido"], cols_r=["R"], cols_num=["Lote"])
