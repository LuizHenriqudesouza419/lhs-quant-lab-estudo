"""Motor 1 — Dados.

Baixa candles da XM pelo MetaTrader 5 e guarda em Parquet, um arquivo por
símbolo e timeframe:

    dados/xm/<SIMBOLO>/<TF>.parquet

Só LÊ dados. Nenhuma função deste módulo envia ordens.
Horários são os do servidor da corretora (XM = GMT+2, ou GMT+3 no horário de verão).
"""
from datetime import datetime, timedelta
from pathlib import Path

import MetaTrader5 as mt5
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
PASTA_DADOS = RAIZ / "dados" / "xm"

# nome no projeto -> nome na XM
SIMBOLOS = {
    "EURUSD": "EURUSD",
    "GBPUSD": "GBPUSD",
    "USDJPY": "USDJPY",
    "AUDUSD": "AUDUSD",
    "USDCAD": "USDCAD",
    "BTCUSD": "BTCUSD#",
}

TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}

DURACAO = {"M1": timedelta(minutes=1), "M5": timedelta(minutes=5),
           "M15": timedelta(minutes=15), "H1": timedelta(hours=1),
           "H4": timedelta(hours=4), "D1": timedelta(days=1)}


def conectar():
    """Conecta ao terminal MT5 aberto e mostra qual conta está logada."""
    if not mt5.initialize():
        raise RuntimeError(f"Não conectou ao MT5: {mt5.last_error()}")
    conta = mt5.account_info()
    tipo = {0: "DEMO", 1: "CONCURSO", 2: "REAL"}.get(conta.trade_mode, "?")
    print(f"MT5 conectado: {conta.server} | login {conta.login} | conta {tipo} (só leitura de dados)")
    return conta


def caminho(simbolo, tf):
    return PASTA_DADOS / simbolo / f"{tf}.parquet"


def _para_dataframe(rates):
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return (df.rename(columns={"time": "tempo", "open": "abertura", "high": "maxima",
                               "low": "minima", "close": "fechamento"})
              .set_index("tempo")
              [["abertura", "maxima", "minima", "fechamento", "tick_volume", "spread", "real_volume"]])


def baixar(simbolo, tf, desde=None):
    """Baixa candles de um símbolo/timeframe.

    desde=None baixa tudo o que o terminal tiver (limitado por 'Máx. barras no gráfico').
    O último candle (ainda em formação) é descartado.
    """
    nome_xm = SIMBOLOS[simbolo]
    if mt5.terminal_info() is None:  # conexão caiu: reconecta
        mt5.shutdown()
        if not mt5.initialize():
            raise RuntimeError(f"Reconexão ao MT5 falhou: {mt5.last_error()}")
    mt5.symbol_select(nome_xm, True)
    if desde is None:
        # o terminal recusa pedir exatamente 'maxbars'; reduz até ser aceito
        qtd = mt5.terminal_info().maxbars - 1
        rates = mt5.copy_rates_from_pos(nome_xm, TIMEFRAMES[tf], 0, qtd)
        while rates is None and qtd > 1000:
            qtd //= 2
            rates = mt5.copy_rates_from_pos(nome_xm, TIMEFRAMES[tf], 0, qtd)
    else:
        rates = mt5.copy_rates_range(nome_xm, TIMEFRAMES[tf], desde, datetime.now() + timedelta(days=2))
    if rates is None or len(rates) == 0:
        return pd.DataFrame()
    return _para_dataframe(rates).iloc[:-1]


def atualizar(simbolo, tf):
    """Acrescenta ao Parquet só os candles novos. Retorna quantos foram adicionados."""
    arq = caminho(simbolo, tf)
    if arq.exists():
        antigo = pd.read_parquet(arq)
        novo = baixar(simbolo, tf, desde=antigo.index[-1].to_pydatetime())
        df = pd.concat([antigo, novo])
        df = df[~df.index.duplicated(keep="last")].sort_index()
        adicionados = len(df) - len(antigo)
    else:
        df = baixar(simbolo, tf)
        adicionados = len(df)
    if len(df):
        arq.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(arq)
    return adicionados


def salvar_info_simbolos():
    """Guarda um retrato diário do valor do tick/pip, spread, swap etc. de cada símbolo."""
    linhas = []
    hoje = pd.Timestamp.now().normalize()
    for simbolo, nome_xm in SIMBOLOS.items():
        mt5.symbol_select(nome_xm, True)
        i = mt5.symbol_info(nome_xm)
        if i is None:
            continue
        linhas.append({
            "data": hoje, "simbolo": simbolo, "nome_xm": nome_xm, "digitos": i.digits,
            "ponto": i.point, "tick_tamanho": i.trade_tick_size, "tick_valor": i.trade_tick_value,
            "contrato": i.trade_contract_size, "spread_pontos": i.spread,
            "swap_compra": i.swap_long, "swap_venda": i.swap_short,
            "lote_min": i.volume_min, "lote_passo": i.volume_step, "moeda_lucro": i.currency_profit,
        })
    novo = pd.DataFrame(linhas)
    arq = PASTA_DADOS / "info_simbolos.parquet"
    if arq.exists():
        antigo = pd.read_parquet(arq)
        novo = pd.concat([antigo[antigo["data"] != hoje], novo], ignore_index=True)
    arq.parent.mkdir(parents=True, exist_ok=True)
    novo.to_parquet(arq, index=False)
    return novo


def atualizar_tudo():
    """Atualiza todos os símbolos e timeframes. Retorna um resumo."""
    conectar()
    try:
        resumo = []
        for simbolo in SIMBOLOS:
            for tf in TIMEFRAMES:
                try:
                    n, erro = atualizar(simbolo, tf), ""
                except Exception as e:  # um par com problema não para os outros
                    n, erro = 0, repr(e)
                df = pd.read_parquet(caminho(simbolo, tf)) if caminho(simbolo, tf).exists() else None
                resumo.append({"simbolo": simbolo, "tf": tf, "novos": n, "erro": erro,
                               "total": 0 if df is None else len(df),
                               "inicio": None if df is None else df.index[0],
                               "fim": None if df is None else df.index[-1]})
        salvar_info_simbolos()
        return pd.DataFrame(resumo)
    finally:
        mt5.shutdown()
