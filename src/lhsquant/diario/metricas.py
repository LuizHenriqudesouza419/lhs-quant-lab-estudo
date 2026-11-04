"""Métricas do diário: resumo geral e cortes por setup, ativo, horário, sessão, emoção e erro.

Tudo em dinheiro líquido (lucro + comissão + swap + taxa) e em R (líquido / risco do SL).
Trades sem SL entram nas métricas em dinheiro, mas ficam fora das métricas em R.
"""
import numpy as np
import pandas as pd

from .horario import DIAS, ORDEM_SESSOES, sessao

MIN_TRADES = 30  # abaixo disso a métrica é marcada como "poucos trades"


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hora"] = df["entrada"].dt.hour
    df["dia_semana"] = df["entrada"].dt.dayofweek.map(dict(enumerate(DIAS)))
    df["sessao"] = df["hora"].apply(sessao)
    df["duracao_min"] = (df["saida"] - df["entrada"]).dt.total_seconds() / 60
    df["ativo"] = df["simbolo"].str.replace("#", "", regex=False)
    return df


def max_drawdown(resultados: pd.Series) -> float:
    curva = resultados.cumsum()
    return float((curva - curva.cummax().clip(lower=0)).min()) if len(curva) else 0.0


def resumo(df: pd.DataFrame) -> dict:
    """Métricas principais de um conjunto de trades."""
    n = len(df)
    if n == 0:
        return {"Nº trades": 0}
    df = df.sort_values("saida")  # o resultado entra na conta na saída (drawdown na ordem certa)
    liq = df["liquido"]
    ganhos, perdas = liq[liq > 0], liq[liq < 0]
    r = df["R"].dropna()
    dias = max((df["saida"].max() - df["entrada"].min()).days, 1)
    trades_ano = n / dias * 365
    desvio = liq.std(ddof=1) if n > 1 else np.nan
    desvio_neg = liq[liq < 0].std(ddof=1) if (liq < 0).sum() > 1 else np.nan
    return {
        "Nº trades": n,
        "Win rate %": 100 * (liq > 0).mean(),
        "Payoff": ganhos.mean() / -perdas.mean() if len(ganhos) and len(perdas) else np.nan,
        "Fator de lucro": ganhos.sum() / -perdas.sum() if len(perdas) else np.nan,
        "Resultado líquido": liq.sum(),
        "Resultado bruto": df["lucro"].sum(),
        "Custos (comissão+swap+taxa)": (df["comissao"] + df["swap"] + df["taxa"]).sum(),
        "Expectativa $": liq.mean(),
        "Expectativa R": r.mean() if len(r) else np.nan,
        "Soma R": r.sum() if len(r) else np.nan,
        "Trades com R": len(r),
        "Máx. drawdown $": max_drawdown(liq),
        "Máx. drawdown R": max_drawdown(r) if len(r) else np.nan,
        # Sharpe/Sortino por trade, anualizados pela frequência real de trades
        "Sharpe": liq.mean() / desvio * np.sqrt(trades_ano) if desvio and desvio > 0 else np.nan,
        "Sortino": liq.mean() / desvio_neg * np.sqrt(trades_ano) if desvio_neg and desvio_neg > 0 else np.nan,
        "Duração média (min)": df["duracao_min"].mean() if "duracao_min" in df else np.nan,
        "Poucos trades": n < MIN_TRADES,
    }


def por_grupo(df: pd.DataFrame, coluna: str, ordem=None) -> pd.DataFrame:
    """Tabela de métricas por valor de uma coluna (setup, ativo, sessao...)."""
    linhas = []
    for valor, g in df.groupby(coluna, sort=False):
        m = resumo(g)
        linhas.append({coluna: valor, "Trades": m["Nº trades"], "Win %": m["Win rate %"],
                       "Payoff": m["Payoff"], "PF": m["Fator de lucro"],
                       "Líquido $": m["Resultado líquido"], "Expect. $": m["Expectativa $"],
                       "Expect. R": m["Expectativa R"], "Soma R": m["Soma R"],
                       "Máx. DD $": m["Máx. drawdown $"], "Poucos trades": m["Poucos trades"]})
    tab = pd.DataFrame(linhas)
    if tab.empty:
        return tab
    if ordem:
        tab[coluna] = pd.Categorical(tab[coluna], [o for o in ordem if o in set(tab[coluna])], ordered=True)
        return tab.sort_values(coluna).reset_index(drop=True)
    return tab.sort_values("Líquido $", ascending=False).reset_index(drop=True)


def por_tag(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Emoções / erros: cada tag do trade conta; 'sem anotação' = trades sem nenhuma tag."""
    x = df.copy()
    x[coluna] = x[coluna].apply(lambda v: v if v else ["sem anotação"])
    return por_grupo(x.explode(coluna), coluna)


def mapa_hora_dia(df: pd.DataFrame, valor="liquido") -> pd.DataFrame:
    """Matriz hora (linhas) × dia da semana (colunas) com a soma do resultado."""
    tab = df.pivot_table(index="hora", columns="dia_semana", values=valor, aggfunc="sum")
    contagem = df.pivot_table(index="hora", columns="dia_semana", values="liquido", aggfunc="count")
    colunas = [d for d in DIAS if d in tab.columns]
    return tab.reindex(columns=colunas), contagem.reindex(columns=colunas)


def por_sessao(df):
    return por_grupo(df, "sessao", ORDEM_SESSOES)
