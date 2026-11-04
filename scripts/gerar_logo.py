"""Gera o kit de logo da LHS Quant Lab (touro geométrico na paleta Terminal Âmbar).

Uso: python scripts/gerar_logo.py
Saída: estilo/logo/ (wallpaper, instagram, youtube, site). Renderiza com o Edge headless.
"""
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "estilo" / "logo"
P = json.loads((RAIZ / "estilo" / "paleta.json").read_text(encoding="utf-8"))["escuro"]
FUNDO, BORDA, TXT, SUAVE, AMB, AZUL = (P[k] for k in ["fundo", "borda", "texto", "texto_suave", "primaria", "secundaria"])
BAIXA = "#4A5D7A"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
FONTES_URL = "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=IBM+Plex+Sans:wght@400&family=IBM+Plex+Mono:wght@500&display=block"
SG, PS, PM = "'Space Grotesk'", "'IBM Plex Sans'", "'IBM Plex Mono'"
TAGLINE = "Aprenda a testar e operar com dados"


def touro(cx, topo, escala, brilho=True):
    """Touro geométrico (traçado da logo LHS Capital). Largura = 184*escala, altura = 165*escala."""
    T = lambda pts: " ".join(f"{cx + (x - 1000) * escala:.1f},{topo + (y - 398) * escala:.1f}" for x, y in pts)
    corpo = T([(908, 398), (958, 443), (985, 437), (1000, 446), (1015, 437), (1042, 443), (1092, 398), (1072, 465),
               (1043, 480), (1030, 543), (1000, 563), (970, 543), (957, 480), (928, 465)])
    sw = max(1.2, 3.75 * escala)
    s = ""
    if brilho:
        s += (f'<defs><radialGradient id="brilho"><stop offset="0" stop-color="{AMB}" stop-opacity=".22"/>'
              f'<stop offset="1" stop-color="{AMB}" stop-opacity="0"/></radialGradient></defs>'
              f'<circle cx="{cx}" cy="{topo + 88 * escala:.1f}" r="{137 * escala:.1f}" fill="url(#brilho)"/>')
    s += (f'<polygon points="{corpo}" fill="{AMB}"/>'
          f'<polyline points="{T([(957, 480), (1000, 503), (1043, 480)])}" fill="none" stroke="{FUNDO}" stroke-width="{sw:.1f}" stroke-linejoin="round" opacity=".55"/>'
          f'<line x1="{cx}" y1="{topo + 48 * escala:.1f}" x2="{cx}" y2="{topo + 165 * escala:.1f}" stroke="{FUNDO}" stroke-width="{sw:.1f}" opacity=".55"/>')
    return s


def grafico(w, h, seed=7, veu=None):
    """Grade pontilhada + velas subindo do canto inferior esquerdo ao superior direito (alta vazada, baixa cheia)."""
    rng = np.random.default_rng(seed)
    s = [f'<rect width="{w}" height="{h}" fill="{FUNDO}"/>']
    s += [f'<circle cx="{x}" cy="{y}" r="2.2" fill="{BORDA}"/>' for x in range(40, w, 64) for y in range(40, h, 64)]
    n = max(40, round(w / 17)); passo = w / n
    vol = np.empty(n); vol[0] = 1.0
    for i in range(1, n):  # volatilidade com agrupamento
        vol[i] = np.sqrt(0.15 + 0.80 * vol[i - 1] ** 2 + 0.05 * rng.standard_normal() ** 2)
    w_ = np.cumsum(rng.standard_normal(n) * vol); t = np.linspace(0, 1, n)
    ponte = w_ - t * w_[-1]  # ponte browniana: começa embaixo, termina em cima
    fech = t + 0.11 * ponte / np.abs(ponte).max() + rng.normal(0, 0.009, n) * vol / vol.mean()
    abre = np.r_[fech[0] - 0.004, fech[:-1]] + rng.normal(0, 0.002, n)
    pav = 0.004 + 0.006 * vol / vol.max()
    maxi = np.maximum(abre, fech) + np.abs(rng.normal(0, 1, n)) * pav
    mini = np.minimum(abre, fech) - np.abs(rng.normal(0, 1, n)) * pav
    lo, hi = mini.min(), maxi.max()
    y = lambda v: (h - 40) - (v - lo) / (hi - lo) * (h - 100)
    corpo = max(6, passo * 0.7); sw = 2.5
    for i in range(n):
        x = passo * (i + .5); o, c = y(abre[i]), y(fech[i]); top, base = min(o, c), max(o, c); alt = max(base - top, 3)
        if fech[i] >= abre[i]:
            s.append(f'<g stroke="{AMB}" stroke-width="{sw}" opacity=".55" fill="none">'
                     f'<line x1="{x:.1f}" y1="{y(maxi[i]):.1f}" x2="{x:.1f}" y2="{top:.1f}"/>'
                     f'<line x1="{x:.1f}" y1="{base:.1f}" x2="{x:.1f}" y2="{y(mini[i]):.1f}"/>'
                     f'<rect x="{x - corpo / 2:.1f}" y="{top:.1f}" width="{corpo:.1f}" height="{alt:.1f}"/></g>')
        else:
            s.append(f'<line x1="{x:.1f}" y1="{y(maxi[i]):.1f}" x2="{x:.1f}" y2="{y(mini[i]):.1f}" stroke="{BAIXA}" stroke-width="{sw}"/>'
                     f'<rect x="{x - corpo / 2:.1f}" y="{top:.1f}" width="{corpo:.1f}" height="{alt:.1f}" fill="{BAIXA}"/>')
    if veu:  # véu escuro atrás do texto
        cx, cy, rx, ry = veu
        s.append(f'<defs><radialGradient id="veu"><stop offset="0" stop-color="{FUNDO}" stop-opacity=".92"/>'
                 f'<stop offset=".6" stop-color="{FUNDO}" stop-opacity=".75"/><stop offset="1" stop-color="{FUNDO}" stop-opacity="0"/></radialGradient></defs>'
                 f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#veu)"/>')
    return "".join(s)


def texto(x, y, txt, fam, tam, cor, peso=700, ancora="middle", esp=0):
    return (f'<text x="{x}" y="{y}" text-anchor="{ancora}" font-family="{fam}" font-weight="{peso}" '
            f'font-size="{tam}" fill="{cor}" letter-spacing="{esp}">{txt}</text>')


# ---------- peças ----------
def perfil():
    return 1080, 1080, (f'<rect width="1080" height="1080" fill="{FUNDO}"/>' + touro(540, 190, 2.4)
                        + texto(540, 800, "LHS", SG, 190, TXT, esp=-2) + texto(540, 885, "QUANT LAB", PM, 50, AZUL, 500, esp=16))


def central(w, h):
    """Composição centralizada (wallpaper, story): touro, LHS, QUANT LAB e tagline entre traços."""
    u = min(w, h) / 1440 if w >= h else w / 1000  # retrato (story): logo ocupa ~80% da largura
    cy = h / 2
    s = grafico(w, h, veu=(w / 2, cy, 760 * u * (w / h if w > h else 1), 520 * u))
    s += touro(w / 2, cy - 330 * u, 1.55 * u)
    s += texto(w / 2, cy + 120 * u, "LHS", SG, 150 * u, TXT, esp=-2)
    s += texto(w / 2, cy + 190 * u, "QUANT LAB", PM, 42 * u, AZUL, 500, esp=14 * u)
    tw = 640 * u
    s += texto(w / 2, cy + 268 * u, TAGLINE.upper(), PM, 24 * u, SUAVE, 500, esp=4 * u)
    s += (f'<line x1="{w / 2 - tw / 2 - 90 * u}" y1="{cy + 260 * u}" x2="{w / 2 - tw / 2 - 20 * u}" y2="{cy + 260 * u}" stroke="{BORDA}" stroke-width="{2 * u}"/>'
          f'<line x1="{w / 2 + tw / 2 + 20 * u}" y1="{cy + 260 * u}" x2="{w / 2 + tw / 2 + 90 * u}" y2="{cy + 260 * u}" stroke="{BORDA}" stroke-width="{2 * u}"/>')
    return s


def banner_horizontal(w, h, ox, oy, lado):
    """Banner com o ícone em cartão + nome, tagline e linha de tópicos (YouTube, og-image)."""
    k = lado / 380
    s = grafico(w, h, veu=(w / 2, h / 2, w * 0.41, h * 0.25))
    s += f'<defs><clipPath id="r"><rect x="{ox}" y="{oy}" width="{lado}" height="{lado}" rx="{70 * k}"/></clipPath></defs>'
    s += f'<g clip-path="url(#r)"><svg x="{ox}" y="{oy}" width="{lado}" height="{lado}" viewBox="0 0 1080 1080">{perfil()[2]}</svg></g>'
    s += f'<rect x="{ox}" y="{oy}" width="{lado}" height="{lado}" rx="{70 * k}" fill="none" stroke="{BORDA}" stroke-width="{4 * k}"/>'
    tx = ox + lado + 60 * k
    s += texto(tx, oy + 160 * k, "LHS Quant Lab", SG, 124 * k, TXT, ancora="start", esp=-2)
    s += texto(tx + 4 * k, oy + 250 * k, TAGLINE, PS, 56 * k, SUAVE, 400, "start")
    s += texto(tx + 6 * k, oy + 332 * k, "aulas · backtests · day trading · @lhsquantlab", PM, 36 * k, AZUL, 500, "start", 3 * k)
    return s


def logo_horizontal():
    s = touro(150, 30, 1.45, brilho=False)
    s += texto(330, 150, "LHS Quant Lab", SG, 120, TXT, ancora="start", esp=-2)
    s += texto(334, 210, TAGLINE.upper(), PM, 26, AZUL, 500, "start", 4)
    return 1240, 280, s


def favicon():
    return 512, 512, f'<rect width="512" height="512" rx="96" fill="{FUNDO}"/>' + touro(256, 108, 2.2, brilho=False)


def marca():
    return 512, 512, touro(256, 58, 2.4, brilho=False)


# ---------- renderização ----------
def svg_doc(vw, vh, corpo, w=None, h=None, fontes=True):
    estilo = f'<defs><style>@import url("{FONTES_URL.replace("&", "&amp;")}");</style></defs>' if fontes else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w or vw}" height="{h or vh}" viewBox="0 0 {vw} {vh}">'
            f'{estilo}{corpo}</svg>')


def render(dest, vw, vh, corpo, w=None, h=None, transparente=False, salvar_svg=False, fontes=True):
    w, h = w or vw, h or vh
    dest.parent.mkdir(parents=True, exist_ok=True)
    fundo_css = "transparent" if transparente else FUNDO
    html = (f'<!doctype html><html><head><meta charset="utf-8"><link href="{FONTES_URL}" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{fundo_css}}}svg{{display:block}}</style></head>'
            f'<body>{svg_doc(vw, vh, corpo, w, h, fontes=False)}</body></html>')
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    args = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            f"--window-size={w},{h}", "--virtual-time-budget=10000", f"--screenshot={dest}"]
    if transparente:
        args.append("--default-background-color=00000000")
    subprocess.run(args + [Path(f.name).as_uri()], check=True, capture_output=True)
    Path(f.name).unlink()
    if salvar_svg:
        dest.with_suffix(".svg").write_text(svg_doc(vw, vh, corpo, fontes=fontes), encoding="utf-8")


def main():
    # perfil (Instagram e YouTube usam a mesma imagem)
    w, h, c = perfil()
    render(OUT / "instagram" / "lhs-perfil-1080.png", w, h, c, salvar_svg=True)
    render(OUT / "youtube" / "lhs-perfil-1080.png", w, h, c)
    # Instagram: fundo de story
    render(OUT / "instagram" / "lhs-story-1080x1920.png", 1080, 1920, central(1080, 1920))
    # YouTube: banner (área segura central 1546x423)
    render(OUT / "youtube" / "lhs-banner-2560x1440.png", 2560, 1440, banner_horizontal(2560, 1440, 632, 568, 304), salvar_svg=True)
    # Wallpaper de PC (desenhado em 2560x1440 e escalado)
    wp = central(2560, 1440)
    for W, H in [(1920, 1080), (2560, 1440), (3840, 2160)]:
        render(OUT / "wallpaper" / f"lhs-wallpaper-{W}x{H}.png", 2560, 1440, wp, W, H)
    # Site
    w, h, c = logo_horizontal()
    render(OUT / "site" / "logo-horizontal.png", w, h, c, transparente=True, salvar_svg=True)
    w, h, c = marca()
    render(OUT / "site" / "logo-marca-512.png", w, h, c, transparente=True, salvar_svg=True, fontes=False)
    w, h, c = favicon()
    render(OUT / "site" / "icon-512.png", w, h, c, transparente=True)
    render(OUT / "site" / "apple-touch-icon-180.png", w, h, c, 180, 180, transparente=True)
    render(OUT / "site" / "favicon-32.png", w, h, c, 32, 32, transparente=True)
    (OUT / "site" / "favicon.svg").write_text(svg_doc(w, h, c, fontes=False), encoding="utf-8")
    render(OUT / "site" / "og-image-1200x630.png", 1200, 630, banner_horizontal(1200, 630, 90, 195, 240))
    print("\n".join(str(p.relative_to(OUT)) for p in sorted(OUT.rglob("*.*"))))


if __name__ == "__main__":
    main()
