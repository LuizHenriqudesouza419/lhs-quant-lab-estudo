"""Relatório pré-mercado diário do EURUSD — pronto às 04:30 (Brasília), dias úteis.

Rodar manualmente:  python scripts/relatorio_premercado.py
Agendado pelo Windows (tarefa "LHS Quant Lab - Pre-mercado EURUSD").

Saídas:
- dados/premercado/AAAA-MM-DD.md, .html e .pdf (relatório completo)
- nota no Obsidian: 01-LHS Quant Lab/Pre-Mercado/AAAA-MM-DD.md
- subpágina em "Relatórios de Mercado" no Notion (se configurado)
- resumo + PDF no Telegram (se configurado)
- dados/premercado/placar.csv (viés previsto × fechamento do dia)

Só lê dados do MT5. Não envia ordens.
"""
import subprocess
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import markdown  # noqa: E402

from lhsquant import dados, notion, premercado as pm  # noqa: E402
from lhsquant.avisos import tarefa  # noqa: E402
from lhsquant.estilo import PALETA  # noqa: E402

LOG = RAIZ / "logs" / "premercado.log"
OBSIDIAN = Path.home() / "OneDrive" / "Documents" / "Obsidian Vault" / "01-LHS Quant Lab" / "Pre-Mercado"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SETA = {1: "▲ alta", -1: "▼ baixa", 0: "◆ misto"}
ICONE_VIES = {"ALTA": "🟢", "BAIXA": "🔴", "NEUTRO": "🟡"}
IMPACTO = {"High": "🔴 alto", "Medium": "🟠 médio", "Holiday": "⚪ feriado"}


def pips(a, b):
    return (a - b) / pm.PIP


def cenarios(a, eventos):
    """Plano condicional em texto, a partir das regras objetivas (não é sinal de entrada)."""
    t, n = a["tfs"], a["niveis"]
    pdh, pdl = n["Máxima de ontem (PDH)"], n["Mínima de ontem (PDL)"]
    linhas = []
    if a["vies"] == "ALTA":
        linhas.append(f"Viés comprador: priorizar compras em recuo até a EMA20/50 do H1 "
                      f"({t['H1']['ema20']:.5f} / {t['H1']['ema50']:.5f}). Perder a PDL ({pdl:.5f}) invalida o viés.")
    elif a["vies"] == "BAIXA":
        linhas.append(f"Viés vendedor: priorizar vendas em repique até a EMA20/50 do H1 "
                      f"({t['H1']['ema20']:.5f} / {t['H1']['ema50']:.5f}). Superar a PDH ({pdh:.5f}) invalida o viés.")
    else:
        linhas.append(f"Sem alinhamento entre H4, H1 e M15: não operar a favor de tendência. Operar só reações claras "
                      f"nos extremos de ontem ({pdl:.5f} – {pdh:.5f}) ou ficar de fora.")
    if a["regime"] == "lateral":
        linhas.append(f"ADX do H1 em {t['H1']['adx']:.0f}: mercado lateral, rompimentos falham mais; preferir alvos curtos.")
    elif a["regime"] == "tendência":
        linhas.append(f"ADX do H1 em {t['H1']['adx']:.0f}: tendência ativa, evitar operar contra ela.")
    if a["asia"] is not None:
        razao = a["asia"]["range"] / a["asia"]["mediana"]
        if razao < 0.7:
            linhas.append(f"Ásia comprimida ({a['asia']['range']:.0f} pips, {razao:.0%} da mediana): atenção a rompimento "
                          f"em Londres de {a['asia']['maxima']:.5f} ou {a['asia']['minima']:.5f}.")
        elif razao > 1.3:
            linhas.append(f"Ásia já esticada ({a['asia']['range']:.0f} pips, {razao:.0%} da mediana): "
                          f"rompimento em Londres tende a ter menos espaço.")
    if a["andado"] > 0.8 * a["atr_d1"]:
        linhas.append(f"O dia já andou {a['andado']:.0f} pips ({a['andado'] / a['atr_d1']:.0%} do ATR D1): pouco espaço restante.")
    if a["spread_atual"] > 2 * a["spread_normal"]:
        linhas.append(f"Spread alargado agora ({a['spread_atual']:.1f} pips contra {a['spread_normal']:.1f} normal): esperar normalizar.")
    altos = [e for e in eventos if e["impacto"] == "High"]
    if altos:
        janelas = ", ".join(f"{(e['hora'] - timedelta(minutes=15)):%H:%M}–{(e['hora'] + timedelta(minutes=15)):%H:%M}"
                            for e in altos)
        linhas.append(f"Não operar nas janelas de notícia de alto impacto: {janelas}.")
    return linhas


def montar_markdown(a, eventos, manchetes, placar, avisos):
    t, preco = a["tfs"], a["preco"]
    md = [f"# Pré-mercado EURUSD — {a['gerado']:%d/%m/%Y}",
          f"*Gerado às {a['gerado']:%H:%M} (Brasília) · preço {preco:.5f} · LHS Quant Lab*", "",
          "## Resumo", "",
          f"- **Viés do dia:** {ICONE_VIES[a['vies']]} **{a['vies']}** (nota {a['soma']:+d} de 3: H4 + H1 + M15, exige 3/3) · regime {a['regime']}"]
    altos = [e for e in eventos if e["impacto"] == "High"]
    md.append(f"- **Evento principal:** {altos[0]['hora']:%H:%M} {altos[0]['moeda']} {altos[0]['evento']}" if altos
              else "- **Evento principal:** nenhum de alto impacto para USD/EUR hoje")
    acima = {k: v for k, v in a["niveis"].items() if v > preco}
    abaixo = {k: v for k, v in a["niveis"].items() if v <= preco}
    if acima:
        k = min(acima, key=acima.get)
        md.append(f"- **Resistência mais próxima:** {k} {acima[k]:.5f} (+{pips(acima[k], preco):.0f} pips)")
    if abaixo:
        k = max(abaixo, key=abaixo.get)
        md.append(f"- **Suporte mais próximo:** {k} {abaixo[k]:.5f} ({pips(abaixo[k], preco):.0f} pips)")

    md += ["", "## Tendência por timeframe", "",
           "| TF | Leitura | Preço × EMA50 | EMA200 | ADX | Estrutura (20 barras) |", "|---|---|---|---|---|---|"]
    for tf, x in t.items():
        md.append(f"| {tf} | {SETA[x['nota']]} | {pips(x['preco'], x['ema50']):+.0f} pips | "
                  f"{'acima' if x['acima_ema200'] else 'abaixo'} | {x['adx']:.0f} | {x['estrutura']} |")
    md += ["", "*Leitura: ▲ = preço e EMA20 acima da EMA50 com EMA50 subindo; ▼ = o contrário. "
               "O viés exige H4, H1 e M15 alinhados (3/3); D1 fica só como contexto.*"]

    md += ["", "## Níveis do dia", "", "| Nível | Preço | Distância |", "|---|---|---|"]
    for k, v in acima.items():  # níveis já vêm do maior para o menor
        md.append(f"| {k} | {v:.5f} | {pips(v, preco):+.0f} pips |")
    md.append(f"| **→ preço atual** | **{preco:.5f}** | |")
    for k, v in abaixo.items():
        md.append(f"| {k} | {v:.5f} | {pips(v, preco):+.0f} pips |")

    md += ["", "## Volatilidade e custo", ""]
    if a["asia"] is not None:
        md.append(f"- **Faixa asiática** (21h–04h Brasília): {a['asia']['minima']:.5f} – {a['asia']['maxima']:.5f} = "
                  f"**{a['asia']['range']:.0f} pips** (mediana de 20 dias: {a['asia']['mediana']:.0f})")
    md += [f"- **ATR D1:** {a['atr_d1']:.0f} pips · **ATR H1:** {a['atr_h1']:.1f} pips · "
           f"já andou hoje: {a['andado']:.0f} pips ({a['andado'] / a['atr_d1']:.0%} do ATR D1)",
           f"- **Spread agora:** {a['spread_atual']:.1f} pips (normal: {a['spread_normal']:.1f})"]

    md += ["", "## Calendário econômico (USD e EUR, horário de Brasília)", ""]
    if eventos:
        md += ["| Hora | Moeda | Impacto | Evento | Previsão | Anterior |", "|---|---|---|---|---|---|"]
        md += [f"| {e['hora']:%H:%M} | {e['moeda']} | {IMPACTO[e['impacto']]} | {e['evento']} | "
               f"{e['previsao'] or '—'} | {e['anterior'] or '—'} |" for e in eventos]
    else:
        md.append("Nenhum evento de impacto alto ou médio para USD/EUR hoje.")

    md += ["", "## Plano condicional", ""] + [f"- {l}" for l in cenarios(a, eventos)]
    md += ["", "*Contexto, não sinal: nenhum setup do LHS Quant Lab está aprovado em backtest ainda.*"]

    md += ["", "## Manchetes (FXStreet, últimas 14 h)", ""]
    md += [f"- {n['hora']:%H:%M} — [{n['titulo']}]({n['link']})" for n in manchetes] or ["- Sem manchetes relevantes."]

    md += ["", "## Placar do viés", "",
           f"Dias avaliados: {placar['dias']} · acertos: {placar['acertos']}"
           + (f" ({placar['acertos'] / placar['dias']:.0%})" if placar["dias"] else "")
           + " · acerto = direção do fechamento do D1 a favor do viés (dias neutros não contam)."]
    if avisos:
        md += ["", "## Avisos da geração", ""] + [f"- {x}" for x in avisos]
    return "\n".join(md) + "\n"


def montar_html(md, titulo):
    c = PALETA["escuro"]
    corpo = markdown.markdown(md, extensions=["tables"])
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{titulo}</title>
<style>
body{{background:{c['fundo']};color:{c['texto']};font-family:"IBM Plex Sans","Segoe UI",sans-serif;
max-width:900px;margin:0 auto;padding:24px 16px;line-height:1.5}}
h1,h2{{font-family:"Space Grotesk","Segoe UI",sans-serif}} h1{{color:{c['primaria']}}}
h2{{border-bottom:1px solid {c['borda']};padding-bottom:4px;margin-top:28px}}
table{{border-collapse:collapse;width:100%;font-family:"IBM Plex Mono",Consolas,monospace;font-size:13px}}
th,td{{border:1px solid {c['borda']};padding:5px 8px;text-align:left}} th{{background:{c['superficie']}}}
a{{color:{c['secundaria_texto']}}} em{{color:{c['texto_suave']}}}
@media print{{body{{max-width:none}}}}
</style></head><body>{corpo}</body></html>"""


def resumo_telegram(a, eventos):
    linhas = [f"<b>Pré-mercado EURUSD — {a['gerado']:%d/%m}</b>",
              f"{ICONE_VIES[a['vies']]} Viés: <b>{a['vies']}</b> ({a['soma']:+d}/3) · regime {a['regime']}",
              f"Preço {a['preco']:.5f} · ATR D1 {a['atr_d1']:.0f} pips"]
    if a["asia"] is not None:
        linhas.append(f"Ásia: {a['asia']['minima']:.5f} – {a['asia']['maxima']:.5f} ({a['asia']['range']:.0f} pips)")
    n = a["niveis"]
    linhas.append(f"PDH {n['Máxima de ontem (PDH)']:.5f} · PDL {n['Mínima de ontem (PDL)']:.5f}")
    altos = [e for e in eventos if e["impacto"] == "High"]
    linhas.append("Alto impacto: " + ("; ".join(f"{e['hora']:%H:%M} {e['moeda']} {e['evento']}" for e in altos)
                                       if altos else "nenhum"))
    return "\n".join(linhas)


def main():
    LOG.parent.mkdir(exist_ok=True)
    inicio = datetime.now()
    avisos = []
    try:
        with tarefa("Pré-mercado EURUSD") as t:  # avisa início, fim (resumo + PDF) e erro no Telegram
            dados.conectar()
            for tf in ("M15", "H1", "H4", "D1"):
                dados.atualizar(pm.SIMBOLO, tf)
            a = pm.analisar()
            eventos, manchetes = [], []
            try:
                eventos = pm.calendario(a["gerado"].date())
            except Exception as e:  # fonte externa fora do ar não impede o relatório
                avisos.append(f"Calendário indisponível: {e!r}")
            try:
                manchetes = pm.noticias()
            except Exception as e:
                avisos.append(f"Manchetes indisponíveis: {e!r}")
            placar = pm.registrar_placar(a)
            dados.mt5.shutdown()

            nome = f"{a['gerado']:%Y-%m-%d}"
            md = montar_markdown(a, eventos, manchetes, placar, avisos)
            (pm.PASTA / f"{nome}.md").write_text(md, encoding="utf-8")
            html = pm.PASTA / f"{nome}.html"
            html.write_text(montar_html(md, f"Pré-mercado EURUSD {nome}"), encoding="utf-8")
            pdf = pm.PASTA / f"{nome}.pdf"
            subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={pdf}", html.as_uri()], check=True, capture_output=True, timeout=180)
            OBSIDIAN.mkdir(parents=True, exist_ok=True)
            (OBSIDIAN / f"{nome}.md").write_text(md, encoding="utf-8")
            if notion.configurado() and not notion.enviar_premercado(a, md):
                avisos.append("Notion: envio falhou")

            t.concluir(resumo_telegram(a, eventos), html=True, arquivo=pdf)
        status, texto = "OK", f"viés {a['vies']} ({a['soma']:+d}) · {len(eventos)} eventos · {len(manchetes)} manchetes"
        if avisos:
            texto += " · avisos: " + " | ".join(avisos)
    except Exception:
        status, texto = "ERRO", traceback.format_exc()
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n=== {inicio:%Y-%m-%d %H:%M} | {status} | {datetime.now() - inicio} ===\n{texto}\n")
    print(texto)
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
