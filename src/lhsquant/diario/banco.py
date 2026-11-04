"""Banco do diário de trading (SQLite em dados/diario.db, fora do git).

Tabelas:
    contas      — contas da XM já importadas (real/demo)
    trades      — um registro por posição fechada (vem do MT5, reimportar não apaga anotações)
    diario      — anotações do Luiz sobre cada trade (setup manual, SL corrigido, emoções...)
    resumo_dia  — texto livre por dia e conta
"""
import json
import sqlite3
from contextlib import contextmanager

import pandas as pd

from ..dados import RAIZ

ARQUIVO = RAIZ / "dados" / "diario.db"

# Listas sugeridas no formulário (dá para digitar outras)
EMOCOES = ["disciplinado", "calmo", "confiante", "ansioso", "FOMO", "medo", "ganância",
           "vingança", "tédio", "cansado", "eufórico"]
ERROS = ["entrou cedo", "entrou tarde", "fora do setup", "sem stop", "moveu o stop",
         "saiu cedo", "segurou o prejuízo", "lote acima do plano", "operou notícia",
         "overtrading", "fora do horário"]

ESQUEMA = """
CREATE TABLE IF NOT EXISTS contas (
    login INTEGER PRIMARY KEY, servidor TEXT, tipo TEXT, moeda TEXT, nome TEXT,
    ultima_importacao TEXT
);
CREATE TABLE IF NOT EXISTS trades (
    login INTEGER, position_id INTEGER, simbolo TEXT, lado TEXT, lote REAL,
    entrada_servidor TEXT, saida_servidor TEXT, entrada TEXT, saida TEXT,
    preco_entrada REAL, preco_saida REAL, sl REAL, tp REAL, sl_origem TEXT,
    lucro REAL, comissao REAL, swap REAL, taxa REAL, liquido REAL,
    valor_por_preco REAL, magic INTEGER, comentario TEXT, motivo_saida TEXT,
    setup_auto TEXT, backtest_id TEXT, n_negocios INTEGER,
    PRIMARY KEY (login, position_id)
);
CREATE TABLE IF NOT EXISTS diario (
    login INTEGER, position_id INTEGER, setup TEXT, sl_corrigido REAL,
    motivo TEXT, seguiu_plano INTEGER, nota INTEGER, emocoes TEXT, erros TEXT,
    licao TEXT, atualizado TEXT,
    PRIMARY KEY (login, position_id)
);
CREATE TABLE IF NOT EXISTS resumo_dia (
    login INTEGER, data TEXT, texto TEXT, PRIMARY KEY (login, data)
);
"""


@contextmanager
def conexao():
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ARQUIVO)
    try:
        con.executescript(ESQUEMA)
        yield con
        con.commit()
    finally:
        con.close()


def gravar_conta(conta: dict):
    with conexao() as con:
        con.execute("INSERT OR REPLACE INTO contas VALUES (:login, :servidor, :tipo, :moeda, :nome, :ultima_importacao)",
                    conta)


def gravar_trades(df: pd.DataFrame) -> int:
    """Insere ou atualiza trades (chave login + position_id). Retorna quantos eram novos."""
    if df.empty:
        return 0
    colunas = list(df.columns)
    with conexao() as con:
        antes = con.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        con.executemany(
            f"INSERT OR REPLACE INTO trades ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))})",
            df.astype(object).where(df.notna(), None).itertuples(index=False, name=None))
        return con.execute("SELECT COUNT(*) FROM trades").fetchone()[0] - antes


def contas() -> pd.DataFrame:
    with conexao() as con:
        return pd.read_sql("SELECT * FROM contas ORDER BY tipo DESC", con)


def carregar(login=None) -> pd.DataFrame:
    """Trades + anotações, com setup, SL e R finais já resolvidos."""
    sql = """SELECT t.*, c.tipo AS tipo_conta, d.setup AS setup_manual, d.sl_corrigido, d.motivo,
                    d.seguiu_plano, d.nota, d.emocoes, d.erros, d.licao
             FROM trades t
             LEFT JOIN contas c ON c.login = t.login
             LEFT JOIN diario d ON d.login = t.login AND d.position_id = t.position_id"""
    with conexao() as con:
        df = pd.read_sql(sql, con)
    if login is not None:
        df = df[df["login"] == login]
    if df.empty:
        return df
    for col in ["entrada", "saida", "entrada_servidor", "saida_servidor"]:
        df[col] = pd.to_datetime(df[col])
    for col in ["nota", "seguiu_plano", "sl_corrigido", "sl", "tp"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["setup"] = df["setup_manual"].fillna(df["setup_auto"]).fillna("sem setup")
    df["sl_final"] = df["sl_corrigido"].fillna(df["sl"])
    distancia = (df["preco_entrada"] - df["sl_final"]).abs()
    risco = distancia * df["valor_por_preco"]
    df["risco"] = risco.where((risco > 0) & df["sl_final"].notna())
    df["R"] = df["liquido"] / df["risco"]
    df["R_bruto"] = df["lucro"] / df["risco"]
    for col in ["emocoes", "erros"]:
        df[col] = df[col].apply(lambda s: json.loads(s) if isinstance(s, str) and s else [])
    return df.sort_values("entrada").reset_index(drop=True)


def anotacao(login, position_id) -> dict:
    with conexao() as con:
        con.row_factory = sqlite3.Row
        linha = con.execute("SELECT * FROM diario WHERE login=? AND position_id=?",
                            (int(login), int(position_id))).fetchone()
    if linha is None:
        return {}
    d = dict(linha)
    for col in ["emocoes", "erros"]:
        d[col] = json.loads(d[col]) if d[col] else []
    return d


def salvar_anotacao(login, position_id, **campos):
    campos = {k: (json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v) for k, v in campos.items()}
    campos.update(login=int(login), position_id=int(position_id),
                  atualizado=pd.Timestamp.now().isoformat(timespec="seconds"))
    nomes = list(campos)
    with conexao() as con:
        con.execute(
            f"INSERT INTO diario ({', '.join(nomes)}) VALUES ({', '.join(':' + n for n in nomes)}) "
            f"ON CONFLICT(login, position_id) DO UPDATE SET "
            + ", ".join(f"{n}=excluded.{n}" for n in nomes if n not in ("login", "position_id")),
            campos)


def resumo_do_dia(login, data) -> str:
    with conexao() as con:
        linha = con.execute("SELECT texto FROM resumo_dia WHERE login=? AND data=?",
                            (int(login), str(data))).fetchone()
    return linha[0] if linha else ""


def salvar_resumo_dia(login, data, texto):
    with conexao() as con:
        con.execute("INSERT OR REPLACE INTO resumo_dia VALUES (?, ?, ?)", (int(login), str(data), texto))

