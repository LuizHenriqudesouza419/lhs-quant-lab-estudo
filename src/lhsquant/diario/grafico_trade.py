"""Gráfico de um trade: candles da XM com entrada, saída, SL e TP (horário de Brasília).

Candles vêm do MT5 (símbolo exato do trade, ex.: EURUSDm#) e ficam em cache em
dados/diario/candles/. Sem MT5, usa o banco Parquet de dados/xm/.
"""
from datetime import timedelta, timezone

import pandas as pd
import plotly.graph_objects as go

from ..dados import DURACAO, PASTA_DADOS, RAIZ, TIMEFRAMES, _para_dataframe
from ..estilo import aplicar_estilo_plotly
from .horario import servidor_para_brasilia

CACHE = RAIZ / "dados" / "diario" / "candles"
BARRAS_ANTES, BARRAS_DEPOIS = 40, 15


def _br(v, sufixo="", casas=2, sinal=True):
    """Número no padrão brasileiro: +1,80R / −0,10."""
    prefixo = ("+" if v > 0 else "−" if v < 0 else "") if sinal else ""
    return f"{prefixo}{abs(v):.{casas}f}".replace(".", ",") + sufixo


def escolher_tf(duracao: timedelta) -> str:
    if duracao <= timedelta(hours=2):
        return "M5"
    if duracao <= timedelta(hours=12):
        return "M15"
    if duracao <= timedelta(days=3):
        return "H1"
    return "H4"


def _do_mt5(simbolo, tf, ent, fim):
    """BARRAS_ANTES velas até a entrada (por quantidade, pula fim de semana) + todas até o fim."""
    import MetaTrader5 as mt5
    if mt5.terminal_info() is None and not mt5.initialize():
        return pd.DataFrame()
    mt5.symbol_select(simbolo, True)
    # datas sem fuso seriam lidas como horário local do PC; com tz=UTC o MT5 usa o horário do servidor como está
    utc = lambda t: t.to_pydatetime().replace(tzinfo=timezone.utc)  # noqa: E731
    antes = mt5.copy_rates_from(simbolo, TIMEFRAMES[tf], utc(ent), BARRAS_ANTES + 1)
    depois = mt5.copy_rates_range(simbolo, TIMEFRAMES[tf], utc(ent), utc(fim))
    partes = [_para_dataframe(r) for r in (antes, depois) if r is not None and len(r)]
    if not partes:
        return pd.DataFrame()
    df = pd.concat(partes)
    return df[~df.index.duplicated()].sort_index()


def _do_parquet(simbolo, tf, ini, fim):  # ini = entrada
    for nome in [simbolo.replace("#", ""), simbolo.replace("#", "").rstrip("m")]:
        arq = PASTA_DADOS / nome / f"{tf}.parquet"
        if arq.exists():
            df = pd.read_parquet(arq)
            return pd.concat([df.loc[:ini].iloc[-BARRAS_ANTES - 1:], df.loc[ini:fim]]).pipe(
                lambda x: x[~x.index.duplicated()])
    return pd.DataFrame()


def candles(trade: dict, tf: str | None = None) -> tuple[pd.DataFrame, str]:
    """Candles em volta do trade (índice em horário de Brasília) e o timeframe usado."""
    ent, sai = pd.Timestamp(trade["entrada_servidor"]), pd.Timestamp(trade["saida_servidor"])
    tf = tf or escolher_tf(sai - ent)
    fim = sai + DURACAO[tf] * BARRAS_DEPOIS
    arq = CACHE / f"{trade['login']}_{trade['position_id']}_{tf}.parquet"
    if arq.exists():
        df = pd.read_parquet(arq)
    else:
        try:
            df = _do_mt5(trade["simbolo"], tf, ent, fim)
        except Exception:  # MT5 indisponível: tenta o banco local
            df = pd.DataFrame()
        if df.empty:
            df = _do_parquet(trade["simbolo"], tf, ent, fim)
        elif fim < pd.Timestamp.now():  # janela completa: guarda para não pedir de novo
            arq.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(arq)
    if not df.empty:
        df = df.copy()
        df.index = servidor_para_brasilia(pd.Series(df.index)).to_numpy()
    return df, tf


def _lacunas(df: pd.DataFrame, tf: str) -> list:
    """Esconde no eixo X os intervalos sem velas (fim de semana, feriado)."""
    if len(df) < 2:
        return []
    passo = DURACAO[tf]
    idx = df.index
    return [dict(bounds=[str(a + passo), str(b)]) for a, b in zip(idx[:-1], idx[1:]) if b - a > passo * 3]


def figura(trade: dict, tf: str | None = None, modo="escuro") -> go.Figure:
    c = aplicar_estilo_plotly(modo)
    df, tf = candles(trade, tf)
    compra = trade["lado"] == "compra"
    fig = go.Figure()
    if df.empty:
        fig.add_annotation(text="Sem candles para este trade (abra o MT5 para baixar)",
                           showarrow=False, font=dict(color=c["texto_suave"]))
    else:
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["abertura"], high=df["maxima"], low=df["minima"], close=df["fechamento"],
            increasing=dict(line=dict(color=c["positivo"]), fillcolor=c["positivo"]),
            decreasing=dict(line=dict(color=c["negativo"]), fillcolor=c["negativo"]),
            name=f"{trade['simbolo']} {tf}", showlegend=False))
    ent, sai = pd.Timestamp(trade["entrada"]), pd.Timestamp(trade["saida"])
    sl = trade.get("sl_final", trade.get("sl"))
    for preco, nome, cor in [(sl, "SL", c["negativo"]), (trade.get("tp"), "TP", c["positivo"])]:
        if preco and pd.notna(preco):
            fig.add_hline(y=preco, line=dict(color=cor, dash="dash", width=1.2),
                          annotation_text=f"{nome} {preco:.5g}", annotation_position="top left",
                          annotation_font=dict(color=cor, family="IBM Plex Mono"))
    fig.add_trace(go.Scatter(
        x=[ent, sai], y=[trade["preco_entrada"], trade["preco_saida"]], mode="lines",
        line=dict(color=c["texto_suave"], dash="dot", width=1), hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=[ent], y=[trade["preco_entrada"]], mode="markers", name="Entrada",
        marker=dict(symbol="triangle-up" if compra else "triangle-down", size=16, color=c["primaria"],
                    line=dict(color=c["fundo"], width=1.5)),
        hovertemplate=f"Entrada ({trade['lado']})<br>%{{x|%d/%m %H:%M}}<br>%{{y:.5f}}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[sai], y=[trade["preco_saida"]], mode="markers", name="Saída",
        marker=dict(symbol="x", size=13, color=c["secundaria"], line=dict(color=c["fundo"], width=1)),
        hovertemplate=f"Saída ({trade['motivo_saida']})<br>%{{x|%d/%m %H:%M}}<br>%{{y:.5f}}<extra></extra>"))
    r = trade.get("R")
    texto_r = _br(r, "R") if r is not None and pd.notna(r) else "sem R"
    fig.update_layout(
        title=f"{trade['simbolo']} {tf} · {trade['lado']} {_br(trade['lote'], casas=2, sinal=False)} lote · "
              f"{_br(trade['liquido'])} · {texto_r}",
        xaxis=dict(tickformat="%d/%m %H:%M", rangebreaks=_lacunas(df, tf)),
        height=520, xaxis_rangeslider_visible=False, hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom"))
    return fig
