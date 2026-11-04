"""Diário de Trading — LHS Quant Lab.

Rodar:  python -m streamlit run app/diario/app.py   (ou pelo atalho da Área de Trabalho)
Só lê a conta da XM: nenhuma ordem é enviada.
"""
import os
import threading
from datetime import date, timedelta

import streamlit as st

import comum

LOGO = comum.RAIZ / "estilo" / "logo" / "site"

st.set_page_config(page_title="Diário de Trading · LHS Quant Lab", page_icon=str(LOGO / "favicon-32.png"),
                   layout="wide")
comum.estilo()
st.logo(str(LOGO / "logo-horizontal.png"), size="large", icon_image=str(LOGO / "icon-512.png"))

paginas = st.navigation([
    st.Page("paginas/metricas.py", title="Métricas", icon=":material/monitoring:", default=True),
    st.Page("paginas/diario.py", title="Diário", icon=":material/edit_note:"),
    st.Page("paginas/sincronizar.py", title="Sincronizar", icon=":material/sync:"),
    st.Page("paginas/real_bt.py", title="Real × Backtest", icon=":material/compare_arrows:"),
])

# ---- filtros (valem para todas as páginas) ----
with st.sidebar:
    contas = comum.banco.contas()
    if not contas.empty:
        rotulos = {int(r.login): f"{r.tipo.upper()} · {r.login} · {r.servidor}" for r in contas.itertuples()}
        login = st.selectbox("Conta", list(rotulos), format_func=rotulos.get, key="conta_sel",
                             help="Real e demo nunca se misturam nas métricas.")
        df_conta = comum.todos()
        df_conta = df_conta[df_conta["login"] == login] if not df_conta.empty else df_conta
        if not df_conta.empty:
            primeiro, hoje = df_conta["entrada"].min().date(), date.today()
            # atalhos em português (o calendário do Streamlit só existe em inglês)
            atalhos = {"Tudo": primeiro, "Hoje": hoje, "Últimos 7 dias": hoje - timedelta(days=6),
                       "Últimos 30 dias": hoje - timedelta(days=29), "Este mês": hoje.replace(day=1),
                       "Últimos 90 dias": hoje - timedelta(days=89), "Este ano": hoje.replace(month=1, day=1),
                       "Personalizado": None}
            escolha = st.selectbox("Período", list(atalhos), key="periodo_atalho")
            if escolha == "Personalizado":
                dias = [primeiro + timedelta(days=i) for i in range((hoje - primeiro).days + 1)]
                periodo = st.select_slider("De / até", dias, value=(dias[0], dias[-1]),
                                           format_func=lambda d: f"{d:%d/%m/%Y}", key="periodo_datas")
            else:
                periodo = (atalhos[escolha], hoje)
                st.caption(f"{periodo[0]:%d/%m/%Y} a {periodo[1]:%d/%m/%Y}")
            ativos = st.multiselect("Ativos", sorted(df_conta["ativo"].unique()), placeholder="Todos")
        else:
            periodo, ativos = None, []
        st.session_state["filtro"] = {"login": login,
                                      "periodo": periodo if periodo and len(periodo) == 2 else None,
                                      "ativos": ativos}
    st.caption("Só leitura da conta · nenhuma ordem é enviada")
    if st.button("Fechar programa", icon=":material/power_settings_new:", width="stretch"):
        st.info("Programa encerrado. Pode fechar esta aba.")
        threading.Timer(1.0, lambda: os._exit(0)).start()
        st.stop()

paginas.run()
