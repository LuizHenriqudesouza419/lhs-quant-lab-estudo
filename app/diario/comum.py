"""Peças comuns das páginas do Diário: estilo Terminal Âmbar, filtros, formatação."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from lhsquant.diario import banco, metricas  # noqa: E402
from lhsquant.estilo import PALETA, aplicar_estilo_plotly  # noqa: E402

C = PALETA["escuro"]
aplicar_estilo_plotly()

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap');
h1, h2, h3, h4 {{ font-family: 'Space Grotesk', sans-serif !important; letter-spacing: -0.01em; }}
.lhs-card {{ background:{C['superficie']}; border:1px solid {C['borda']}; border-radius:10px;
            padding:12px 16px; height:100%; }}
.lhs-card .rot {{ color:{C['texto_suave']}; font-size:0.78rem; text-transform:uppercase; letter-spacing:0.06em; }}
.lhs-card .val {{ font-family:'IBM Plex Mono', monospace; font-size:1.45rem; font-weight:600; margin-top:2px; }}
.lhs-card .sub {{ color:{C['texto_suave']}; font-size:0.78rem; font-family:'IBM Plex Mono', monospace; }}
.lhs-selo {{ font-family:'IBM Plex Mono', monospace; font-weight:600; font-size:0.85rem;
            padding:3px 12px; border-radius:999px; display:inline-block; }}
.lhs-mono {{ font-family:'IBM Plex Mono', monospace; }}
</style>
"""

SELOS = {"Aprovado": (C["positivo"], C["positivo_fundo"]),
         "Reprovado": (C["negativo"], C["negativo_fundo"]),
         "Em teste": (C["secundaria_texto"], C["info_fundo"])}


def estilo():
    st.markdown(CSS, unsafe_allow_html=True)


def num(v, casas=2, sinal=True, sufixo=""):
    """Número no padrão brasileiro com sinal: +1,80R / −42,10."""
    if v is None or pd.isna(v):
        return "—"
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    prefixo = ("+" if v > 0 else "−" if v < 0 else "") if sinal else ("−" if v < 0 else "")
    return f"{prefixo}{s}{sufixo}"


def cor(v):
    if v is None or pd.isna(v) or v == 0:
        return C["texto"]
    return C["positivo"] if v > 0 else C["negativo"]


def card(rotulo, valor, cor_valor=None, sub=""):
    st.markdown(f"<div class='lhs-card'><div class='rot'>{rotulo}</div>"
                f"<div class='val' style='color:{cor_valor or C['texto']}'>{valor}</div>"
                f"<div class='sub'>{sub}</div></div>", unsafe_allow_html=True)


def selo(veredito):
    texto, fundo = SELOS.get(veredito, SELOS["Em teste"])
    return f"<span class='lhs-selo' style='color:{texto};background:{fundo}'>{veredito}</span>"


@st.cache_data(show_spinner=False)
def _carregar(versao):  # versao muda após importar/salvar e invalida o cache
    df = banco.carregar()
    return metricas.preparar(df) if not df.empty else df


def recarregar():
    st.session_state["versao_dados"] = st.session_state.get("versao_dados", 0) + 1


def dados_filtrados() -> pd.DataFrame:
    """Trades da conta/período escolhidos na barra lateral."""
    df = _carregar(st.session_state.get("versao_dados", 0))
    if df.empty:
        return df
    f = st.session_state.get("filtro", {})
    if f.get("login"):
        df = df[df["login"] == f["login"]]
    if f.get("periodo"):
        ini, fim = f["periodo"]
        df = df[(df["entrada"].dt.date >= ini) & (df["entrada"].dt.date <= fim)]
    if f.get("ativos"):
        df = df[df["ativo"].isin(f["ativos"])]
    return df.reset_index(drop=True)


def todos() -> pd.DataFrame:
    return _carregar(st.session_state.get("versao_dados", 0))


def tabela(tab: pd.DataFrame, cols_dinheiro=(), cols_r=(), cols_pct=(), cols_num=()):
    """Mostra uma tabela de métricas com números em pt-BR e ganho/perda coloridos."""
    if tab.empty:
        st.info("Sem trades neste corte.")
        return
    tab = tab.copy()
    if "Poucos trades" in tab:
        tab["Amostra"] = tab.pop("Poucos trades").map({True: "poucos trades", False: "ok"})
    fmt = {c: (lambda v: num(v)) for c in cols_dinheiro}
    fmt |= {c: (lambda v: num(v, sufixo="R")) for c in cols_r}
    fmt |= {c: (lambda v: num(v, 1, sinal=False, sufixo="%")) for c in cols_pct}
    fmt |= {c: (lambda v: num(v, 2, sinal=False)) for c in cols_num}
    # formata como texto (o Streamlit mostra "None" em vazios formatados pelo Styler) e colore pelo valor original
    cores = pd.DataFrame("", index=tab.index, columns=tab.columns)
    for c in [*cols_dinheiro, *cols_r]:
        if c in tab:
            cores[c] = tab[c].map(lambda v: f"color:{cor(v)}")
    texto = tab.copy()
    for c, f in fmt.items():
        if c in texto:
            texto[c] = texto[c].map(f)
    texto = texto.astype(object).where(texto.notna(), "—")
    st.dataframe(texto.style.apply(lambda _: cores, axis=None), hide_index=True, width="stretch")
