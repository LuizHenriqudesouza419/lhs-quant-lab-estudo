"""Identidade visual da LHS Quant Lab (paleta Terminal Âmbar) para gráficos.

Fonte única das cores: estilo/paleta.json. Uso nos notebooks:

    from lhsquant.estilo import aplicar_estilo, CORES
    aplicar_estilo()            # tema escuro (padrão da marca)
    aplicar_estilo("claro")     # para PDFs e impressão
    plt.plot(x, y, color=CORES["primaria"])
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PALETA = json.loads((RAIZ / "estilo" / "paleta.json").read_text(encoding="utf-8"))

# Cores do modo ativo; aplicar_estilo() atualiza este dicionário
CORES = dict(PALETA["escuro"])


def aplicar_estilo(modo="escuro"):
    """Aplica a paleta no matplotlib. modo: "escuro" ou "claro". Retorna as cores do modo."""
    import matplotlib as mpl
    from cycler import cycler

    c = PALETA[modo]
    CORES.clear()
    CORES.update(c)
    mpl.rcParams.update({
        "figure.facecolor": c["fundo"],
        "axes.facecolor": c["fundo"],
        "savefig.facecolor": c["fundo"],
        "axes.edgecolor": c["borda"],
        "axes.labelcolor": c["texto"],
        "axes.titlecolor": c["texto"],
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.grid": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": cycler(color=[c["primaria"], c["secundaria"], c["positivo"],
                                         c["negativo"], c["texto_suave"]]),
        "grid.color": c["borda"],
        "grid.alpha": 0.6,
        "xtick.color": c["texto_suave"],
        "ytick.color": c["texto_suave"],
        "text.color": c["texto"],
        "legend.facecolor": c["superficie"],
        "legend.edgecolor": c["borda"],
        "legend.frameon": True,
        "font.family": "sans-serif",
        "font.sans-serif": ["IBM Plex Sans", "Segoe UI", "DejaVu Sans"],
        "figure.figsize": (12, 4.5),
    })
    return CORES


def aplicar_estilo_plotly(modo="escuro"):
    """Registra e ativa o template "lhs" no plotly (mesma paleta). Retorna as cores do modo.

    Uso: aplicar_estilo_plotly(); fig = go.Figure(...)   # já sai com as cores da marca
    """
    import plotly.graph_objects as go
    import plotly.io as pio

    c = PALETA[modo]
    eixo = dict(gridcolor=c["borda"], linecolor=c["borda"], zerolinecolor=c["borda"],
                tickfont=dict(color=c["texto_suave"], family="IBM Plex Mono"),
                title=dict(font=dict(color=c["texto_suave"])))
    pio.templates["lhs"] = go.layout.Template(layout=dict(
        paper_bgcolor=c["fundo"], plot_bgcolor=c["fundo"],
        font=dict(family="IBM Plex Sans, Segoe UI, sans-serif", color=c["texto"], size=13),
        title=dict(font=dict(family="Space Grotesk, IBM Plex Sans, sans-serif", size=16, color=c["texto"])),
        colorway=[c["primaria"], c["secundaria"], c["positivo"], c["negativo"], c["texto_suave"]],
        xaxis=eixo, yaxis=eixo,
        legend=dict(bgcolor=c["superficie"], bordercolor=c["borda"], borderwidth=1),
        hoverlabel=dict(bgcolor=c["superficie"], bordercolor=c["borda"],
                        font=dict(color=c["texto"], family="IBM Plex Mono")),
        margin=dict(l=50, r=20, t=50, b=40),
    ))
    pio.templates.default = "lhs"
    return dict(c)
