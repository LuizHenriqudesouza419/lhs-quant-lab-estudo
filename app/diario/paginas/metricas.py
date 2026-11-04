"""Métricas: resumo, curva de capital e cortes por setup, ativo, horário, sessão, emoção e erro."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import comum
from lhsquant.diario import metricas

C = comum.C
st.title("Métricas")
df = comum.dados_filtrados()
if df.empty:
    st.info("Nenhum trade neste filtro. Sincronize a conta primeiro.")
    st.stop()

m = metricas.resumo(df)
if m["Poucos trades"]:
    st.warning(f"Só {m['Nº trades']} trades neste filtro: as métricas ainda não são conclusivas "
               f"(mínimo de {metricas.MIN_TRADES}).")

linha1 = st.columns(4)
linha2 = st.columns(4)
with linha1[0]:
    comum.card("Resultado líquido", comum.num(m["Resultado líquido"]), comum.cor(m["Resultado líquido"]),
               f"bruto {comum.num(m['Resultado bruto'])} · custos {comum.num(m['Custos (comissão+swap+taxa)'])}")
with linha1[1]:
    comum.card("Trades · win rate", f"{m['Nº trades']} · {comum.num(m['Win rate %'], 1, False, '%')}",
               sub=f"{m['Trades com R']} com stop (R)")
with linha1[2]:
    comum.card("Expectativa", comum.num(m["Expectativa R"], sufixo="R"), comum.cor(m["Expectativa R"]),
               f"{comum.num(m['Expectativa $'])} por trade")
with linha1[3]:
    comum.card("Soma de R", comum.num(m["Soma R"], sufixo="R"), comum.cor(m["Soma R"]))
with linha2[0]:
    comum.card("Payoff", comum.num(m["Payoff"], sinal=False), sub="ganho médio / perda média")
with linha2[1]:
    comum.card("Fator de lucro", comum.num(m["Fator de lucro"], sinal=False), sub="ganhos / perdas")
with linha2[2]:
    comum.card("Máx. drawdown", comum.num(m["Máx. drawdown $"]), comum.cor(m["Máx. drawdown $"]),
               comum.num(m["Máx. drawdown R"], sufixo="R"))
with linha2[3]:
    comum.card("Sharpe · Sortino", f"{comum.num(m['Sharpe'], sinal=False)} · {comum.num(m['Sortino'], sinal=False)}",
               sub="anualizados pela frequência de trades")

# ---- curva de capital ----
st.write("")


def _rgba(hex_cor, alfa):
    h = hex_cor.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alfa})"


c1, c2, _ = st.columns([1.2, 1.4, 3])
unidade = c1.segmented_control("Curva em", ["Dinheiro", "R"], default="Dinheiro")
eixo = c2.segmented_control("Eixo", ["Por trade", "Por data"], default="Por trade")
em_r = unidade == "R"
x = df.sort_values("saida").reset_index(drop=True)
if em_r:
    fora = int(x["R"].isna().sum())
    x = x[x["R"].notna()].reset_index(drop=True)
    if fora:
        st.caption(f"{fora} trades sem stop ficam fora da curva em R.")
if x.empty:
    st.info("Sem trades com R neste filtro.")
else:
    valor = x["R"] if em_r else x["liquido"]
    sufixo = "R" if em_r else ""
    acum = valor.cumsum()
    topo = acum.cummax().clip(lower=0)
    dd = acum - topo
    # ponto inicial em zero, antes do primeiro trade
    eixo_x = (pd.concat([pd.Series([0]), pd.Series(range(1, len(x) + 1))]) if eixo != "Por data"
              else pd.concat([pd.Series([x["entrada"].iloc[0]]), x["saida"]]))
    eixo_x = eixo_x.reset_index(drop=True)
    y_curva = pd.concat([pd.Series([0.0]), acum]).reset_index(drop=True)
    y_dd = pd.concat([pd.Series([0.0]), dd]).reset_index(drop=True)
    dica = [[f"{t.saida:%d/%m/%y %H:%M}", t.ativo, t.setup, comum.num(v, sufixo=sufixo), comum.num(a, sufixo=sufixo)]
            for t, v, a in zip(x.itertuples(), valor, acum)]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.72, 0.28], vertical_spacing=0.06)
    fig.add_trace(go.Scatter(x=eixo_x, y=y_curva, mode="lines", name="Líquido" if not em_r else "R acumulado",
                             line=dict(color=C["primaria"], width=2), hoverinfo="skip"), row=1, col=1)
    if not em_r:
        fig.add_trace(go.Scatter(x=eixo_x, y=pd.concat([pd.Series([0.0]), x["lucro"].cumsum()]).reset_index(drop=True),
                                 mode="lines", name="Sem custos", line=dict(color=C["texto_suave"], dash="dash", width=1.4),
                                 hovertemplate="Sem custos: %{y:.2f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=eixo_x.iloc[1:], y=acum, mode="markers", name="Trade", showlegend=False, customdata=dica,
        marker=dict(size=8, color=[C["positivo"] if v > 0 else C["negativo"] for v in valor],
                    line=dict(color=C["fundo"], width=2)),
        hovertemplate=("<b>Trade %{x}</b><br>" if eixo != "Por data" else "<b>%{customdata[0]}</b><br>")
        + "%{customdata[1]} · %{customdata[2]}<br>Resultado: %{customdata[3]}<br>Acumulado: %{customdata[4]}"
        "<extra></extra>"), row=1, col=1)
    fig.add_annotation(x=eixo_x.iloc[-1], y=acum.iloc[-1], text=f"<b>{comum.num(acum.iloc[-1], sufixo=sufixo)}</b>",
                       showarrow=False, xanchor="left", xshift=8, font=dict(color=C["texto"], family="IBM Plex Mono"),
                       row=1, col=1)
    fig.add_hline(y=0, line=dict(color=C["borda"], width=1), row=1, col=1)

    fig.add_trace(go.Scatter(x=eixo_x, y=y_dd, mode="lines", name="Drawdown", showlegend=False,
                             line=dict(color=C["negativo"], width=1.5), fill="tozeroy",
                             fillcolor=_rgba(C["negativo"], 0.18),
                             hovertemplate="Drawdown: %{y:.2f}" + sufixo + "<extra></extra>"), row=2, col=1)
    k = int(dd.idxmin()) if dd.min() < 0 else None
    if k is not None:
        fig.add_annotation(x=eixo_x.iloc[k + 1], y=dd.iloc[k], text=f"máx. {comum.num(dd.iloc[k], sufixo=sufixo)}",
                           showarrow=False, yanchor="top", yshift=-4, font=dict(color=C["negativo"], family="IBM Plex Mono",
                                                                                 size=11), row=2, col=1)
    fig.update_layout(title="Curva de capital" + (" em R" if em_r else ""), height=520, hovermode="closest",
                      legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"),
                      margin=dict(r=70))
    fig.update_yaxes(title_text="acumulado" + (" (R)" if em_r else ""), row=1, col=1)
    fig.update_yaxes(title_text="drawdown", row=2, col=1)
    if eixo == "Por data":
        fig.update_xaxes(tickformat="%d/%m/%y")
    else:
        fig.update_xaxes(title_text="nº do trade", row=2, col=1)
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

COLS = dict(cols_dinheiro=["Líquido $", "Expect. $", "Máx. DD $"], cols_r=["Expect. R", "Soma R"],
            cols_pct=["Win %"], cols_num=["Payoff", "PF"])


def barras(tab, coluna, titulo, valor="Líquido $"):
    if tab.empty:
        return
    vals = tab[valor].fillna(0)
    fig = go.Figure(go.Bar(
        x=tab[coluna].astype(str).str.replace(" (", "<br>(", regex=False), y=vals, marker_color=[C["positivo"] if v >= 0 else C["negativo"] for v in vals],
        text=[comum.num(v, sufixo="R" if valor.endswith("R") else "") for v in vals], textposition="outside",
        customdata=tab["Trades"], hovertemplate="%{x}<br>%{text}<br>%{customdata} trades<extra></extra>"))
    fig.update_layout(title=titulo, height=340, showlegend=False)
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False})


NOMES_ABAS = ["Ativo", "Horário", "Sessão", "Setup", "Emoção", "Disciplina", "Erro", "Trades"]
abas = dict(zip(NOMES_ABAS, st.tabs(NOMES_ABAS)))
with abas["Setup"]:
    tab = metricas.por_grupo(df, "setup")
    barras(tab, "setup", "Resultado líquido por setup")
    comum.tabela(tab.rename(columns={"setup": "Setup"}), **COLS)
with abas["Ativo"]:
    tab = metricas.por_grupo(df, "ativo")
    barras(tab, "ativo", "Resultado líquido por ativo")
    comum.tabela(tab.rename(columns={"ativo": "Ativo"}), **COLS)
with abas["Horário"]:
    valor = st.segmented_control("Mapa em", ["Dinheiro", "R"], default="Dinheiro", key="mapa_unidade")
    mapa, contagem = metricas.mapa_hora_dia(df, "R" if valor == "R" else "liquido")
    if not mapa.empty:
        limite = float(mapa.abs().max().max() or 1)
        texto = [[("" if v != v else comum.num(v, sufixo="R" if valor == "R" else "")) for v in linha]
                 for linha in mapa.to_numpy()]
        fig = go.Figure(go.Heatmap(
            z=mapa.to_numpy(), x=mapa.columns, y=[f"{h:02d}h" for h in mapa.index], text=texto,
            texttemplate="%{text}", customdata=contagem.to_numpy(), zmid=0, zmin=-limite, zmax=limite,
            colorscale=[[0, C["negativo"]], [0.5, C["superficie"]], [1, C["positivo"]]],
            hovertemplate="%{x} %{y}<br>%{text}<br>%{customdata} trades<extra></extra>", xgap=2, ygap=2))
        fig.update_layout(title="Resultado por hora de entrada × dia da semana (Brasília)", height=560,
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
    tab = metricas.por_grupo(df, "hora", ordem=sorted(df["hora"].unique()))
    tab["hora"] = tab["hora"].astype(int).map(lambda h: f"{h:02d}h")
    comum.tabela(tab.rename(columns={"hora": "Hora"}), **COLS)
with abas["Sessão"]:
    tab = metricas.por_sessao(df)
    barras(tab, "sessao", "Resultado líquido por sessão")
    comum.tabela(tab.rename(columns={"sessao": "Sessão"}), **COLS)
    st.caption("Sessão pela hora de entrada, em horário de Brasília.")
with abas["Emoção"]:
    tab = metricas.por_tag(df, "emocoes")
    barras(tab, "emocoes", "Resultado por emoção anotada")
    comum.tabela(tab.rename(columns={"emocoes": "Emoção"}), **COLS)
    st.caption("Um trade com várias emoções conta em cada uma delas.")
with abas["Erro"]:
    tab = metricas.por_tag(df, "erros")
    barras(tab, "erros", "Quanto custa cada erro")
    comum.tabela(tab.rename(columns={"erros": "Erro"}), **COLS)
with abas["Disciplina"]:
    d = df.assign(plano=df["seguiu_plano"].map({1: "Seguiu o plano", 0: "Não seguiu"}).fillna("Sem anotação"),
                  nota_txt=df["nota"].map(lambda n: f"nota {int(n)}" if n == n else "sem nota"))
    tab = metricas.por_grupo(d, "plano")
    barras(tab, "plano", "Seguir o plano compensa?")
    comum.tabela(tab.rename(columns={"plano": "Plano"}), **COLS)
    comum.tabela(metricas.por_grupo(d, "nota_txt", ordem=sorted(d["nota_txt"].unique()))
                 .rename(columns={"nota_txt": "Nota da execução"}), **COLS)
with abas["Trades"]:
    lista = df.sort_values("entrada", ascending=False)
    comum.tabela(lista[["entrada", "saida", "simbolo", "lado", "lote", "setup", "preco_entrada", "preco_saida",
                        "sl_final", "lucro", "comissao", "swap", "liquido", "R", "motivo_saida", "sessao"]]
                 .assign(entrada=lambda x: x["entrada"].dt.strftime("%d/%m/%y %H:%M"),
                         saida=lambda x: x["saida"].dt.strftime("%d/%m/%y %H:%M"))
                 .rename(columns={"entrada": "Entrada", "saida": "Saída", "simbolo": "Ativo", "lado": "Lado",
                                  "lote": "Lote", "setup": "Setup", "preco_entrada": "Preço entrada",
                                  "preco_saida": "Preço saída", "sl_final": "SL", "lucro": "Bruto",
                                  "comissao": "Comissão", "swap": "Swap", "liquido": "Líquido",
                                  "motivo_saida": "Motivo", "sessao": "Sessão"}),
                 cols_dinheiro=["Bruto", "Comissão", "Swap", "Líquido"], cols_r=["R"], cols_num=["Lote"])
    st.download_button("Baixar CSV", lista.drop(columns=["emocoes", "erros"]).to_csv(index=False).encode("utf-8-sig"),
                       "trades_diario.csv", "text/csv", icon=":material/download:")
