"""Real × Backtest: o setup ao vivo está dentro do que o backtest prometia?

Faixa esperada = bootstrap dos trades out-of-sample do backtest: sorteia N trades (N = trades
reais do setup) muitas vezes e guarda os percentis 5% e 95% da expectativa em R e do win rate.
Seed fixa para o resultado ser sempre o mesmo.
"""
import numpy as np
import pandas as pd

from ..dados import RAIZ
from .metricas import MIN_TRADES

PASTA_BT = RAIZ / "backtests"
SEED = 42
SORTEIOS = 5000


def metricas_backtest(backtest_id: str) -> dict:
    """Primeira coluna de metricas_oos.csv (ou metricas.csv) do backtest."""
    pasta = PASTA_BT / backtest_id
    for nome in ["metricas_oos.csv", "metricas.csv"]:
        arq = pasta / nome
        if arq.exists():
            tab = pd.read_csv(arq, index_col=0)
            col = tab.columns[0]
            return {"variante": col, **pd.to_numeric(tab[col], errors="coerce").dropna().to_dict()}
    return {}


def trades_backtest(backtest_id: str) -> pd.Series:
    """R líquido de cada trade OOS do backtest (vazio se o backtest não guarda R)."""
    pasta = PASTA_BT / backtest_id
    for nome in ["operacoes_oos.csv", "trades.csv"]:
        arq = pasta / nome
        if arq.exists():
            tab = pd.read_csv(arq)
            if "R" in tab:
                return tab["R"].dropna()
    return pd.Series(dtype=float)


def faixa_esperada(r_bt: pd.Series, n: int) -> dict:
    rng = np.random.default_rng(SEED)
    amostras = rng.choice(r_bt.to_numpy(), size=(SORTEIOS, n), replace=True)
    expect, win = amostras.mean(axis=1), (amostras > 0).mean(axis=1) * 100
    return {"expect_p5": np.percentile(expect, 5), "expect_p95": np.percentile(expect, 95),
            "win_p5": np.percentile(win, 5), "win_p95": np.percentile(win, 95)}


def faixa_curva(r_bt: pd.Series, n: int) -> pd.DataFrame:
    """Percentis 5/50/95 do R acumulado após k trades (k = 1..n), sorteando trades do backtest."""
    rng = np.random.default_rng(SEED)
    acum = rng.choice(r_bt.to_numpy(), size=(SORTEIOS, n), replace=True).cumsum(axis=1)
    return pd.DataFrame({"k": np.arange(1, n + 1), "p5": np.percentile(acum, 5, axis=0),
                         "p50": np.percentile(acum, 50, axis=0), "p95": np.percentile(acum, 95, axis=0)})


def comparar(df: pd.DataFrame, setup: str, backtest_id: str) -> dict:
    """Compara os trades reais de um setup com o backtest. Retorna números + veredito."""
    reais = df[df["setup"] == setup]
    r = reais["R"].dropna()
    bt = metricas_backtest(backtest_id)
    r_bt = trades_backtest(backtest_id)
    saida = {"setup": setup, "backtest": backtest_id, "trades": len(reais), "trades_R": len(r),
             "expect_real": r.mean() if len(r) else np.nan,
             "win_real": (reais["liquido"] > 0).mean() * 100 if len(reais) else np.nan,
             "expect_bt": bt.get("Expectativa R", r_bt.mean() if len(r_bt) else np.nan),
             "win_bt": bt.get("Win rate %", (r_bt > 0).mean() * 100 if len(r_bt) else np.nan),
             "dd_bt": bt.get("Máx. drawdown %"), "trades_bt": bt.get("Nº trades", len(r_bt)),
             "r_real": r.reset_index(drop=True), "r_bt": r_bt}
    if len(r) == 0 or len(r_bt) == 0:
        saida["veredito"] = "Em teste"
        saida["explicacao"] = "Sem trades com R" if len(r_bt) else "Backtest sem trades em R"
        return saida
    saida.update(faixa_esperada(r_bt, len(r)))
    if len(r) < MIN_TRADES:
        saida["veredito"] = "Em teste"
        saida["explicacao"] = f"{len(r)} trades com R — mínimo de {MIN_TRADES} para julgar"
    elif saida["expect_real"] < saida["expect_p5"]:
        saida["veredito"] = "Reprovado"
        saida["explicacao"] = "Expectativa real abaixo da faixa esperada (5%) do backtest"
    else:
        saida["veredito"] = "Aprovado"
        saida["explicacao"] = "Expectativa real dentro (ou acima) da faixa esperada do backtest"
    return saida
