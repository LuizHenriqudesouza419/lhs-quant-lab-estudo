"""Real × Backtest: cada setup ao vivo contra a faixa esperada pelo seu backtest."""
import plotly.graph_objects as go
import streamlit as st

import comum
from lhsquant.diario import comparar_bt, importar_mt5

C = comum.C
st.title("Real × Backtest")
st.caption("Faixa esperada = sorteio (bootstrap, seed fixa) dos trades out-of-sample do backtest, com o mesmo número "
           "de trades que você já fez no setup. Abaixo do percentil 5% da expectativa = Reprovado.")

df = comum.dados_filtrados()
if df.empty:
    st.info("Nenhum trade neste filtro. Sincronize a conta primeiro.")
    st.stop()

cfg = importar_mt5.setups()
ligados = {s: (cfg.get(s) or {}).get("backtest") for s in df["setup"].unique()}
ligados = {s: bt for s, bt in ligados.items() if bt and (comparar_bt.PASTA_BT / bt).exists()}
sem_bt = sorted(set(df["setup"]) - set(ligados))
if sem_bt:
    st.caption("Sem backtest ligado: " + ", ".join(sem_bt) + " — ligue em setups/diario.yaml.")
if not ligados:
    st.info("Nenhum setup destes trades tem backtest ligado em setups/diario.yaml.")
    st.stop()

for setup, bt in ligados.items():
    r = comparar_bt.comparar(df, setup, bt)
    st.divider()
    st.markdown(f"### {setup} &nbsp; {comum.selo(r['veredito'])}", unsafe_allow_html=True)
    st.caption(f"Backtest {bt} ({r['trades_bt']:.0f} trades OOS) · {r['explicacao']}")
    cols = st.columns(4)
    with cols[0]:
        comum.card("Trades reais", f"{r['trades']}", sub=f"{r['trades_R']} com stop (R)")
    with cols[1]:
        faixa = (f"faixa {comum.num(r['expect_p5'], sufixo='R')} a {comum.num(r['expect_p95'], sufixo='R')}"
                 if "expect_p5" in r else "")
        comum.card("Expectativa real", comum.num(r["expect_real"], sufixo="R"), comum.cor(r["expect_real"]), faixa)
    with cols[2]:
        comum.card("Expectativa backtest", comum.num(r["expect_bt"], sufixo="R"), comum.cor(r["expect_bt"]),
                   "líquida de custos")
    with cols[3]:
        faixa_win = (f"faixa {comum.num(r['win_p5'], 0, False, '%')} a {comum.num(r['win_p95'], 0, False, '%')}"
                     if "win_p5" in r else "")
        comum.card("Win rate real × BT", f"{comum.num(r['win_real'], 1, False, '%')} × {comum.num(r['win_bt'], 1, False, '%')}",
                   sub=faixa_win)
    if len(r["r_real"]) and len(r["r_bt"]):
        curva = comparar_bt.faixa_curva(r["r_bt"], len(r["r_real"]))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=curva["k"], y=curva["p95"], mode="lines", line=dict(width=0), showlegend=False,
                                 hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=curva["k"], y=curva["p5"], mode="lines", line=dict(width=0), fill="tonexty",
                                 fillcolor="rgba(127,179,230,0.15)", name="Faixa esperada (5%–95%)"))
        fig.add_trace(go.Scatter(x=curva["k"], y=curva["p50"], mode="lines", name="Backtest (mediana)",
                                 line=dict(color=C["texto_suave"], dash="dash")))
        fig.add_trace(go.Scatter(x=curva["k"], y=r["r_real"].cumsum(), mode="lines+markers", name="Real",
                                 line=dict(color=C["primaria"], width=2.2), marker=dict(size=5)))
        fig.update_layout(title="R acumulado: real × esperado pelo backtest", height=360, hovermode="x unified",
                          xaxis_title="nº do trade", yaxis_title="R acumulado",
                          legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
