"""Relatório pré-mercado diário do EURUSD (contexto para day trade).

Tudo é calculado em Python, a partir dos candles fechados (sem o candle em formação):
tendência por timeframe, viés do dia, níveis, faixa asiática, volatilidade, spread,
calendário econômico (Forex Factory) e manchetes (FXStreet).

Só LÊ dados. Nenhuma função deste módulo envia ordens.
Horários do relatório em Brasília (UTC-3). Candles do Parquet estão no horário do
servidor da XM; a diferença para UTC é medida no próprio MT5 (offset_servidor).
"""
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import numpy as np
import pandas as pd
import requests

from lhsquant import dados

SIMBOLO = "EURUSD"
PIP = 0.0001
BRT = timezone(timedelta(hours=-3))
PASTA = dados.RAIZ / "dados" / "premercado"
PLACAR = PASTA / "placar.csv"
URL_CALENDARIO = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
URL_NOTICIAS = "https://www.fxstreet.com/rss/news"
# palavra inteira: "US Dollar" sozinho pegaria notícias de CAD, MXN etc.
PALAVRAS_NOTICIAS = re.compile(
    r"\b(EUR|EUR/USD|euro|eurozone|ECB|European Central Bank|Lagarde|Fed|Federal Reserve|FOMC|Powell|DXY|US Dollar Index|"
    r"Treasury|Treasuries|Nonfarm|NFP|US CPI|US PCE|US GDP|German|Germany|ZEW|Ifo)\b", re.IGNORECASE)
ASIA_UTC = (0, 7)  # faixa asiática: 00:00–07:00 UTC (= 21:00–04:00 em Brasília)


# ---------------------------------------------------------------- indicadores
def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def atr(df, n=14):
    c_ant = df["fechamento"].shift(1)
    tr = pd.concat([df["maxima"] - df["minima"], (df["maxima"] - c_ant).abs(),
                    (df["minima"] - c_ant).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def adx(df, n=14):
    alta = df["maxima"].diff()
    baixa = -df["minima"].diff()
    dm_mais = np.where((alta > baixa) & (alta > 0), alta, 0.0)
    dm_menos = np.where((baixa > alta) & (baixa > 0), baixa, 0.0)
    a = atr(df, n)
    di_mais = 100 * pd.Series(dm_mais, df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    di_menos = 100 * pd.Series(dm_menos, df.index).ewm(alpha=1 / n, adjust=False).mean() / a
    dx = 100 * (di_mais - di_menos).abs() / (di_mais + di_menos)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def tendencia(df):
    """Leitura de tendência de um timeframe. nota: +1 alta, −1 baixa, 0 misto."""
    c = df["fechamento"]
    e20, e50, e200 = ema(c, 20), ema(c, 50), ema(c, 200)
    inclinacao = e50.iloc[-1] - e50.iloc[-6]  # EMA50 contra 5 barras atrás
    preco = c.iloc[-1]
    if preco > e50.iloc[-1] and e20.iloc[-1] > e50.iloc[-1] and inclinacao > 0:
        nota = 1
    elif preco < e50.iloc[-1] and e20.iloc[-1] < e50.iloc[-1] and inclinacao < 0:
        nota = -1
    else:
        nota = 0
    # estrutura: máxima/mínima das últimas 20 barras contra as 20 anteriores
    mx, mn = df["maxima"], df["minima"]
    topo = mx.iloc[-20:].max() > mx.iloc[-40:-20].max()
    fundo = mn.iloc[-20:].min() > mn.iloc[-40:-20].min()
    estrutura = ("topos e fundos ascendentes" if topo and fundo else
                 "topos e fundos descendentes" if not topo and not fundo else "estrutura mista")
    return {"nota": nota, "preco": preco, "ema20": e20.iloc[-1], "ema50": e50.iloc[-1],
            "ema200": e200.iloc[-1], "acima_ema200": bool(preco > e200.iloc[-1]),
            "adx": float(adx(df).iloc[-1]), "estrutura": estrutura}


# ---------------------------------------------------------------- dados
def offset_servidor():
    """Horas entre o horário do servidor da XM e UTC (2 no inverno, 3 no verão europeu)."""
    tick = dados.mt5.symbol_info_tick(dados.SIMBOLOS[SIMBOLO])
    return round((tick.time - datetime.now(timezone.utc).timestamp()) / 3600), tick


def carregar(tf, offset):
    """Candles do Parquet com o índice convertido para UTC."""
    df = pd.read_parquet(dados.caminho(SIMBOLO, tf))
    df.index = df.index - pd.Timedelta(hours=offset)
    return df


def _baixar_com_cache(url, nome, horas):
    """Baixa um arquivo e guarda; reaproveita o salvo se tiver menos de `horas`.
    O Forex Factory bloqueia pedidos repetidos, por isso o cache."""
    PASTA.mkdir(parents=True, exist_ok=True)
    arq = PASTA / nome
    if arq.exists() and datetime.now().timestamp() - arq.stat().st_mtime < horas * 3600:
        return arq.read_text(encoding="utf-8")
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (LHS Quant Lab)"})
        r.raise_for_status()
    except requests.RequestException:
        if arq.exists():  # bloqueado ou fora do ar: usa a última cópia salva
            return arq.read_text(encoding="utf-8")
        raise
    arq.write_text(r.text, encoding="utf-8")
    return r.text


def calendario(dia_brt):
    """Eventos de USD e EUR (impacto alto/médio e feriados) do dia, em horário de Brasília."""
    eventos = json.loads(_baixar_com_cache(URL_CALENDARIO, "calendario_semana.json", horas=6))
    saida = []
    for e in eventos:
        if e["country"] not in ("USD", "EUR") or e["impact"] not in ("High", "Medium", "Holiday"):
            continue
        hora = datetime.fromisoformat(e["date"]).astimezone(BRT)
        if hora.date() != dia_brt:
            continue
        saida.append({"hora": hora, "moeda": e["country"], "impacto": e["impact"],
                      "evento": e["title"], "previsao": e.get("forecast", ""),
                      "anterior": e.get("previous", "")})
    return sorted(saida, key=lambda x: x["hora"])


def noticias(horas=14, maximo=8):
    """Manchetes recentes do FXStreet ligadas a euro, dólar, BCE e Fed."""
    raiz = ET.fromstring(_baixar_com_cache(URL_NOTICIAS, "noticias.xml", horas=0.5))
    limite = datetime.now(timezone.utc) - timedelta(hours=horas)
    saida = []
    for item in raiz.iter("item"):
        titulo = (item.findtext("title") or "").strip()
        quando = parsedate_to_datetime(item.findtext("pubDate"))
        if quando < limite or not PALAVRAS_NOTICIAS.search(titulo):
            continue
        saida.append({"hora": quando.astimezone(BRT), "titulo": titulo, "link": item.findtext("link")})
    return saida[:maximo]


# ---------------------------------------------------------------- análise
def analisar(agora_utc=None):
    """Calcula tudo o que entra no relatório. Precisa do MT5 conectado (dados.conectar())."""
    offset, tick = offset_servidor()
    agora_utc = agora_utc or datetime.now(timezone.utc)
    hoje_utc = pd.Timestamp(agora_utc.date())
    d1, h4, h1, m15 = (carregar(tf, offset) for tf in ("D1", "H4", "H1", "M15"))

    tfs = {"D1": tendencia(d1), "H4": tendencia(h4), "H1": tendencia(h1), "M15": tendencia(m15)}
    # day trade: viés só com H4, H1 e M15 todos alinhados; D1 fica só como contexto
    soma = tfs["H4"]["nota"] + tfs["H1"]["nota"] + tfs["M15"]["nota"]
    vies = "ALTA" if soma == 3 else "BAIXA" if soma == -3 else "NEUTRO"
    adx_h1 = tfs["H1"]["adx"]
    regime = "tendência" if adx_h1 >= 25 else "lateral" if adx_h1 < 20 else "indefinido"

    # D1 da XM fecha às 17h de Nova York; em UTC o índice cai na véspera, à noite
    d1_fechados = d1[d1.index < pd.Timestamp(agora_utc.replace(tzinfo=None)) - pd.Timedelta(days=1)]
    ontem = d1_fechados.iloc[-1]
    semanas = d1_fechados.resample("W-FRI", label="right", closed="right").agg(
        {"maxima": "max", "minima": "min"})
    semana_ant = semanas[semanas.index < hoje_utc].iloc[-1]
    pivo = (ontem["maxima"] + ontem["minima"] + ontem["fechamento"]) / 3

    preco = (tick.bid + tick.ask) / 2
    redondo_baixo = np.floor(preco / 0.005) * 0.005
    niveis = {
        "Máxima da semana anterior": semana_ant["maxima"],
        "Máxima de ontem (PDH)": ontem["maxima"],
        "Fechamento de ontem (PDC)": ontem["fechamento"],
        "Mínima de ontem (PDL)": ontem["minima"],
        "Mínima da semana anterior": semana_ant["minima"],
        "Pivô clássico": pivo,
        "R1": 2 * pivo - ontem["minima"],
        "S1": 2 * pivo - ontem["maxima"],
        "Número redondo acima": redondo_baixo + 0.005,
        "Número redondo abaixo": redondo_baixo,
    }

    # faixa asiática de hoje e das 20 sessões anteriores
    asia = m15[(m15.index.hour >= ASIA_UTC[0]) & (m15.index.hour < ASIA_UTC[1])]
    por_dia = asia.groupby(asia.index.normalize()).agg({"maxima": "max", "minima": "min"})
    por_dia["range"] = (por_dia["maxima"] - por_dia["minima"]) / PIP
    asia_hoje = por_dia.loc[hoje_utc] if hoje_utc in por_dia.index else None
    asia_mediana = por_dia["range"][por_dia.index < hoje_utc].iloc[-20:].median()

    atr_d1 = atr(d1_fechados).iloc[-1] / PIP
    hoje_m15 = m15[m15.index >= hoje_utc]
    andado = (hoje_m15["maxima"].max() - hoje_m15["minima"].min()) / PIP if len(hoje_m15) else 0.0
    spread_atual = (tick.ask - tick.bid) / PIP
    spread_normal = m15["spread"].iloc[-20 * 96:].median() / 10  # pontos de 5 dígitos -> pips

    return {
        "gerado": agora_utc.astimezone(BRT), "preco": preco, "offset": offset,
        "tfs": tfs, "soma": soma, "vies": vies, "regime": regime,
        "niveis": dict(sorted(niveis.items(), key=lambda kv: -kv[1])),
        "asia": None if asia_hoje is None else {
            "maxima": asia_hoje["maxima"], "minima": asia_hoje["minima"],
            "range": asia_hoje["range"], "mediana": asia_mediana},
        "atr_d1": atr_d1, "atr_h1": atr(h1).iloc[-1] / PIP, "andado": andado,
        "spread_atual": spread_atual, "spread_normal": spread_normal,
    }


# ---------------------------------------------------------------- placar
def registrar_placar(a):
    """Grava o viés de hoje e confere os dias anteriores contra o fechamento do D1."""
    PASTA.mkdir(parents=True, exist_ok=True)
    placar = pd.read_csv(PLACAR, parse_dates=["data"]) if PLACAR.exists() else pd.DataFrame(
        columns=["data", "vies", "soma", "preco_ref", "fechamento", "resultado_pips", "acertou"])
    hoje = pd.Timestamp(a["gerado"].date())
    placar = placar[placar["data"] != hoje]
    # só NEUTRO até aqui -> o CSV lê "acertou" vazia como float e recusa True/False
    placar["acertou"] = placar["acertou"].astype(object)
    placar = pd.concat([placar, pd.DataFrame([{"data": hoje, "vies": a["vies"], "soma": a["soma"],
                                               "preco_ref": round(a["preco"], 5)}])], ignore_index=True)

    # fechamento do dia de cada relatório = D1 da XM daquela data (fecha 17h NY = 18h Brasília)
    d1 = pd.read_parquet(dados.caminho(SIMBOLO, "D1"))
    for i, linha in placar[placar["fechamento"].isna()].iterrows():
        if linha["data"] in d1.index and linha["data"] < hoje:
            fech = d1.loc[linha["data"], "fechamento"]
            mov = (fech - linha["preco_ref"]) / PIP
            placar.loc[i, ["fechamento", "resultado_pips"]] = [fech, round(mov, 1)]
            if linha["vies"] != "NEUTRO":
                placar.loc[i, "acertou"] = (mov > 0) == (linha["vies"] == "ALTA")
    placar.sort_values("data").to_csv(PLACAR, index=False)
    avaliados = placar.dropna(subset=["acertou"])
    return {"dias": len(avaliados), "acertos": int(avaliados["acertou"].astype(bool).sum())}
