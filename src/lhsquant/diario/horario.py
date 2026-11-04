"""Horários do diário: servidor da XM -> Brasília, e sessões do forex.

O MT5 entrega o horário do servidor da XM, que é GMT+2 no inverno e GMT+3 no verão
(muda junto com o horário de verão de Nova York). Brasília é GMT-3 o ano todo.
"""
import pandas as pd

BRASILIA = "America/Sao_Paulo"

# Sessões pela hora de ENTRADA em Brasília (mesma faixa asiática do pré-mercado: 00–07 UTC)
SESSOES = [  # (nome, hora inicial, hora final) — final exclusiva
    ("Ásia", 21, 4),
    ("Londres", 4, 9),
    ("Londres + NY", 9, 13),
    ("Nova York", 13, 18),
    ("Fora de sessão", 18, 21),
]


def rotulo_sessao(nome, ini, fim) -> str:
    """"Ásia (21:00 às 04:00)" — horário de Brasília."""
    return f"{nome} ({ini:02d}:00 às {fim:02d}:00)"


ORDEM_SESSOES = [rotulo_sessao(*s) for s in SESSOES]
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def servidor_para_utc(tempo: pd.Series) -> pd.Series:
    """Horário do servidor XM (sem fuso) -> UTC (sem fuso)."""
    tempo = pd.to_datetime(tempo)
    verao_ny = (tempo.dt.tz_localize("UTC").dt.tz_convert("America/New_York")
                .apply(lambda t: t.dst().total_seconds() > 0))
    return tempo - pd.to_timedelta(2 + verao_ny.astype(int), unit="h")


def servidor_para_brasilia(tempo: pd.Series) -> pd.Series:
    """Horário do servidor XM (sem fuso) -> Brasília (sem fuso)."""
    utc = servidor_para_utc(tempo)
    return utc.dt.tz_localize("UTC").dt.tz_convert(BRASILIA).dt.tz_localize(None)


def sessao(hora: int) -> str:
    for nome, ini, fim in SESSOES:
        if (ini <= hora < fim) if ini < fim else (hora >= ini or hora < fim):
            return rotulo_sessao(nome, ini, fim)
    return ORDEM_SESSOES[-1]
