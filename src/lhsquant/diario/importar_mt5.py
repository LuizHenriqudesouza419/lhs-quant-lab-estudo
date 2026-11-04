"""Importa o histórico de operações da XM (MT5) para o banco do diário.

Só LÊ a conta: usa history_deals_get / history_orders_get. Nenhuma ordem é enviada.
O MT5 importa a conta que estiver logada no terminal — por isso info_conta() vem antes.

Cada posição fechada vira um trade (fechamentos parciais são somados, com preço médio).
"""
import re
from datetime import datetime, timedelta

import MetaTrader5 as mt5
import pandas as pd
import yaml

from ..dados import RAIZ
from . import banco
from .horario import servidor_para_brasilia

ARQ_SETUPS = RAIZ / "setups" / "diario.yaml"
TIPOS_CONTA = {0: "demo", 1: "concurso", 2: "real"}
MOTIVOS = {0: "manual", 1: "manual (celular)", 2: "manual (web)", 3: "EA", 4: "stop",
           5: "alvo", 6: "stop out", 7: "rollover", 8: "margem", 9: "split"}
RE_SL = re.compile(r"\[sl\s+([\d.]+)\]", re.I)
RE_TP = re.compile(r"\[tp\s+([\d.]+)\]", re.I)


def setups() -> dict:
    """{nome: {"magic": int|None, "backtest": str|None}} de setups/diario.yaml."""
    if not ARQ_SETUPS.exists():
        return {}
    dados = yaml.safe_load(ARQ_SETUPS.read_text(encoding="utf-8")) or {}
    return {nome: (cfg or {}) for nome, cfg in (dados.get("setups") or {}).items()}


def conectar():
    if mt5.terminal_info() is None and not mt5.initialize():
        raise RuntimeError(f"Não conectou ao MT5 (o terminal está aberto?): {mt5.last_error()}")


def info_conta() -> dict:
    """Conta logada no terminal agora."""
    conectar()
    c = mt5.account_info()
    if c is None:
        raise RuntimeError("O MT5 está aberto, mas sem conta logada.")
    return {"login": c.login, "servidor": c.server, "tipo": TIPOS_CONTA.get(c.trade_mode, "?"),
            "moeda": c.currency, "nome": c.name, "saldo": c.balance, "patrimonio": c.equity}


def _df(tuplas) -> pd.DataFrame:
    if not tuplas:
        return pd.DataFrame()
    return pd.DataFrame(list(tuplas), columns=tuplas[0]._asdict().keys())


def _media(precos, volumes):
    return float((precos * volumes).sum() / volumes.sum()) if volumes.sum() else float("nan")


def _preco_comentario(regex, comentarios):
    for txt in comentarios:
        m = regex.search(txt or "")
        if m:
            return float(m.group(1))
    return None


def _valor_por_preco(lucro, entrada, saida, direcao, simbolo, lote):
    """Quanto 1,0 de variação de preço vale em dinheiro da conta neste trade."""
    movimento = (saida - entrada) * direcao
    if abs(movimento) > 1e-9 and lucro != 0:
        return lucro / movimento
    info = mt5.symbol_info(simbolo)
    if info is None or not info.trade_tick_size:
        return None
    return info.trade_tick_value / info.trade_tick_size * lote


def montar_trades(negocios: pd.DataFrame, ordens: pd.DataFrame, login: int) -> pd.DataFrame:
    cfg = setups()
    por_magic = {int(v["magic"]): (nome, v.get("backtest")) for nome, v in cfg.items() if v.get("magic")}
    backtest_de = {nome: v.get("backtest") for nome, v in cfg.items()}
    negocios = negocios[negocios["type"].isin([0, 1])]  # tira depósitos, créditos etc.
    linhas = []
    for pos, g in negocios.groupby("position_id"):
        g = g.sort_values("time_msc")
        ent = g[g["entry"].isin([0, 2])]
        sai = g[g["entry"].isin([1, 2, 3])]
        if ent.empty or sai.empty or sai["volume"].sum() + 1e-9 < ent["volume"].sum():
            continue  # posição ainda aberta (ou só parcial)
        direcao = 1 if ent.iloc[0]["type"] == 0 else -1
        simbolo, lote = ent.iloc[0]["symbol"], float(ent["volume"].sum())
        p_ent, p_sai = _media(ent["price"], ent["volume"]), _media(sai["price"], sai["volume"])

        o = ordens[ordens["position_id"] == pos] if not ordens.empty else ordens
        sl_ordem = o.loc[o["sl"] > 0, "sl"].iloc[0] if not o.empty and (o["sl"] > 0).any() else None
        tp_ordem = o.loc[o["tp"] > 0, "tp"].iloc[0] if not o.empty and (o["tp"] > 0).any() else None
        sl_coment = _preco_comentario(RE_SL, sai["comment"])
        sl, origem = (sl_ordem, "ordem") if sl_ordem else (sl_coment, "saída no stop") if sl_coment else (None, None)
        # SL só vale como risco se estiver do lado da perda (stop movido para o lucro não é risco)
        if sl is not None and (p_ent - sl) * direcao <= 0:
            sl, origem = None, None
        tp = tp_ordem or _preco_comentario(RE_TP, sai["comment"])

        magic = int(ent.iloc[0]["magic"])
        comentario = str(ent.iloc[0]["comment"] or "")
        setup_auto, bt = por_magic.get(magic, (None, None))
        if comentario.upper().startswith("LHS:"):
            setup_auto = comentario[4:].strip()
            bt = backtest_de.get(setup_auto)

        lucro, comissao = float(g["profit"].sum()), float(g["commission"].sum())
        swap, taxa = float(g["swap"].sum()), float(g["fee"].sum())
        linhas.append({
            "login": login, "position_id": int(pos), "simbolo": simbolo,
            "lado": "compra" if direcao == 1 else "venda", "lote": lote,
            "entrada_servidor": pd.Timestamp(ent.iloc[0]["time"], unit="s"),
            "saida_servidor": pd.Timestamp(sai.iloc[-1]["time"], unit="s"),
            "preco_entrada": p_ent, "preco_saida": p_sai, "sl": sl, "tp": tp, "sl_origem": origem,
            "lucro": lucro, "comissao": comissao, "swap": swap, "taxa": taxa,
            "liquido": lucro + comissao + swap + taxa,
            "valor_por_preco": _valor_por_preco(lucro, p_ent, p_sai, direcao, simbolo, lote),
            "magic": magic, "comentario": " | ".join(c for c in g["comment"] if c),
            "motivo_saida": MOTIVOS.get(int(sai.iloc[-1]["reason"]), "?"),
            "setup_auto": setup_auto, "backtest_id": bt, "n_negocios": len(g),
        })
    df = pd.DataFrame(linhas)
    if df.empty:
        return df
    df["entrada"] = servidor_para_brasilia(df["entrada_servidor"])
    df["saida"] = servidor_para_brasilia(df["saida_servidor"])
    for col in ["entrada_servidor", "saida_servidor", "entrada", "saida"]:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def importar(desde=datetime(2010, 1, 1)) -> dict:
    """Importa todos os trades fechados da conta logada. Retorna conta + contagens."""
    conta = info_conta()
    ate = datetime.now() + timedelta(days=2)  # servidor está à frente de Brasília
    negocios = _df(mt5.history_deals_get(desde, ate))
    ordens = _df(mt5.history_orders_get(desde, ate))
    trades = montar_trades(negocios, ordens, conta["login"]) if not negocios.empty else pd.DataFrame()
    banco.gravar_conta({k: conta[k] for k in ["login", "servidor", "tipo", "moeda", "nome"]}
                       | {"ultima_importacao": datetime.now().isoformat(timespec="seconds")})
    novos = banco.gravar_trades(trades)
    return {"conta": conta, "trades": len(trades), "novos": novos}

