"""Gera carrosséis do Instagram (1080x1350) na identidade LHS Quant Lab.

Uso: python scripts/gerar_carrossel.py 001 [3 5 ...]  (números opcionais = regerar só esses slides)
Cada carrossel é um dicionário em CARROSSEIS; a saída vai para conteudo/instagram/<id>/.
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_logo import AMB, AZUL, BORDA, EDGE, FUNDO, SUAVE, TXT, grafico, touro  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
W, H = 1080, 1350
SUP = "#16233A"
POS, POS_F, NEG, NEG_F = "#5FCF9B", "#173B33", "#F08A6C", "#3D2420"
FONTES = ("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700"
          "&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=block")

CSS = f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{FUNDO};color:{TXT};font-family:'IBM Plex Sans',Arial,sans-serif;position:relative;
  background-image:radial-gradient({BORDA} 2px,transparent 2.4px);background-size:48px 48px;background-position:24px 24px}}
.bg{{position:absolute;inset:0}}
.topo{{position:absolute;top:56px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center}}
.marca{{display:flex;align-items:center;gap:16px;font-family:'IBM Plex Mono',monospace;font-size:24px;letter-spacing:4px;color:{SUAVE}}}
.pag{{font-family:'IBM Plex Mono',monospace;font-size:24px;color:{SUAVE}}}
.rodape{{position:absolute;bottom:56px;left:80px;right:80px;display:flex;justify-content:space-between;
  font-family:'IBM Plex Mono',monospace;font-size:26px;color:{AZUL}}}
.rodape .seta{{color:{AMB}}}
.corpo{{position:absolute;top:190px;bottom:150px;left:80px;right:80px;display:flex;flex-direction:column;justify-content:center;gap:40px}}
.eyebrow{{font-family:'IBM Plex Mono',monospace;font-size:28px;letter-spacing:6px;color:{AMB};text-transform:uppercase}}
h1{{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:84px;line-height:1.05;letter-spacing:-1px}}
h2{{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:64px;line-height:1.1;letter-spacing:-1px}}
p{{font-size:38px;line-height:1.45;color:{SUAVE}}}
.amb{{color:{AMB}}}
ul{{list-style:none;display:flex;flex-direction:column;gap:22px}}
li{{display:flex;gap:24px;align-items:flex-start;font-size:36px;line-height:1.35;background:{SUP};border:2px solid {BORDA};border-radius:20px;padding:26px 30px}}
li .n{{font-family:'IBM Plex Mono',monospace;color:{AMB};font-size:30px;padding-top:4px;min-width:46px}}
li.nao .n{{color:{NEG}}}
li.sim .n{{color:{POS}}}
.duas{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}
.duas li{{font-size:30px;padding:22px 22px;gap:16px}}
.duas li .n{{min-width:28px}}
.col{{font-family:'IBM Plex Mono',monospace;font-size:26px;letter-spacing:4px;text-transform:uppercase;margin-bottom:18px}}
.col.sim{{color:{POS}}}
.col.nao{{color:{NEG}}}
.card{{background:{SUP};border:2px solid {BORDA};border-radius:24px;padding:44px;display:flex;flex-direction:column;gap:28px}}
.card .tit{{font-family:'IBM Plex Mono',monospace;font-size:26px;color:{AZUL};letter-spacing:2px}}
.card .setup{{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:48px;line-height:1.1}}
.metr{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.metr div{{display:flex;flex-direction:column;gap:6px}}
.metr b{{font-family:'IBM Plex Mono',monospace;font-size:44px;font-weight:500;color:{TXT}}}
.metr span{{font-size:24px;color:{SUAVE}}}
.selo{{align-self:flex-start;font-family:'IBM Plex Mono',monospace;font-size:30px;letter-spacing:4px;padding:12px 24px;border-radius:12px}}
.selo.neg{{color:{NEG};background:{NEG_F}}}
.centro{{align-items:center;text-align:center}}
.tile{{background:#FFFDF8;border-radius:24%;display:flex;align-items:center;justify-content:center;flex:none;box-shadow:0 0 0 3px {BORDA}}}
.tile img,.tile svg{{width:70%;height:70%;object-fit:contain}}
.logos{{display:flex;gap:24px;flex-wrap:wrap;align-items:center}}
.centro .logos{{justify-content:center}}
.grade{{display:grid;grid-template-columns:repeat(4,auto);gap:28px;justify-content:center}}
.linha{{display:flex;align-items:center;gap:26px;background:{SUP};border:2px solid {BORDA};border-radius:20px;padding:20px 26px}}
.linha .n{{font-family:'IBM Plex Mono',monospace;color:{AMB};font-size:28px;min-width:40px}}
.linha .lg{{display:flex;gap:12px}}
.linha .tx b{{font-family:'Space Grotesk',Arial,sans-serif;font-size:34px;display:block}}
.linha .tx span{{font-size:28px;line-height:1.3;color:{SUAVE}}}
.linhas{{display:flex;flex-direction:column;gap:20px}}
.regra{{border-left:6px solid {AMB};background:{SUP};border-radius:0 20px 20px 0;padding:28px 34px;font-size:34px;line-height:1.4}}
.regra b{{color:{AMB}}}
.justo{{gap:28px}}
.sub{{font-family:'IBM Plex Mono',monospace;font-size:24px;letter-spacing:4px;color:{AZUL};text-transform:uppercase}}
.duelo{{display:flex;align-items:center;justify-content:center;gap:28px}}
.duelo figure{{display:flex;flex-direction:column;align-items:center;gap:14px}}
.duelo img{{width:330px;height:360px;object-fit:cover;border-radius:24px;border:3px solid {BORDA};filter:grayscale(1) contrast(1.05)}}
.duelo figcaption{{font-family:'IBM Plex Mono',monospace;font-size:24px;letter-spacing:3px;color:{SUAVE};text-transform:uppercase}}
.duelo .x{{font-family:'Space Grotesk',Arial,sans-serif;font-weight:700;font-size:64px;color:{AMB};padding-bottom:40px}}
.credito{{font-size:18px;color:{SUAVE};opacity:.75}}
.compacta ul{{gap:14px}}
.compacta li{{font-size:31px;padding:17px 26px}}
.compacta li .n{{font-size:28px;padding-top:2px}}
.hora{{display:grid;grid-template-columns:1fr auto;gap:14px 30px;font-size:36px;align-items:center}}
.hora b{{font-family:'IBM Plex Mono',monospace;font-weight:500;color:{TXT}}}
.hora .top{{color:{AMB}}}
"""


def svg(w, h, corpo, vw=None, vh=None):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {vw or w} {vh or h}">{corpo}</svg>'


def mini_touro(lado=44):
    return svg(lado, lado, touro(92, 0, 1.0, brilho=False), 184, 184)


def montar(slide, i, n):
    fundo = ""
    if slide.get("grafico"):
        fundo = f'<div class="bg">{svg(W, H, grafico(W, H, seed=slide.get("seed", 7), veu=(W / 2, H / 2, 620, 520)))}</div>'
    topo = (f'<div class="topo"><div class="marca">{mini_touro()}LHS QUANT LAB</div>'
            f'<div class="pag">{i:02d} / {n:02d}</div></div>')
    seta = '<span class="seta">arraste →</span>' if i < n else '<span class="seta">salve ★</span>'
    rodape = f'<div class="rodape"><span>@lhsquantlab</span>{seta}</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><link href="{FONTES}" rel="stylesheet">'
            f'<style>{CSS}</style></head><body>{fundo}{topo}<div class="corpo{slide.get("classe", "")}">'
            f'{slide["html"]}</div>{rodape}</body></html>')


def lista(itens, marca=None, cls=""):
    """Lista em cartões; sem `marca` numera 01, 02...; `cls` = sim/nao muda a cor da marca."""
    c = f' class="{cls}"' if cls else ""
    return "<ul>" + "".join(f'<li{c}><span class="n">{marca or f"{k:02d}"}</span><span>{t}</span></li>'
                            for k, t in enumerate(itens, 1)) + "</ul>"


# Logos oficiais das ferramentas (estilo/logos-ferramentas/). Os do Simple Icons vêm em preto:
# a cor da marca é aplicada aqui.
PASTA_LOGOS = RAIZ / "estilo" / "logos-ferramentas"
COR_MARCA = {"anaconda": "#44A833", "numba": "#00A3E0", "numpy": "#013243",
             "obsidian": "#7C3AED", "pandas": "#150458", "scikitlearn": "#F7931E"}
BANCO = svg(100, 100, f'<ellipse cx="50" cy="22" rx="34" ry="12" fill="{AMB}"/>'
                      f'<path d="M16 22v56c0 7 15 12 34 12s34-5 34-12V22c0 7-15 12-34 12S16 29 16 22z" fill="{FUNDO}"/>'
                      f'<path d="M16 50c0 7 15 12 34 12s34-5 34-12" stroke="{AMB}" stroke-width="4" fill="none"/>')


def logo(nome, lado=120):
    """Logo oficial num cartão claro (legível no fundo escuro). nome = arquivo sem extensão; "banco" = ícone de dados."""
    if nome == "banco":
        conteudo = BANCO
    else:
        arq = next(PASTA_LOGOS.glob(f"{nome}.*"))
        if arq.suffix == ".svg":
            texto = arq.read_text(encoding="utf-8")
            if nome in COR_MARCA:
                texto = texto.replace("<svg ", f'<svg fill="{COR_MARCA[nome]}" ', 1)
            conteudo_b, mime = texto.encode("utf-8"), "image/svg+xml"
        else:
            conteudo_b, mime = arq.read_bytes(), "image/png"
        conteudo = f'<img src="data:{mime};base64,{base64.b64encode(conteudo_b).decode()}">'
    return f'<div class="tile" style="width:{lado}px;height:{lado}px">{conteudo}</div>'


def logos(nomes, lado=120, cls="logos"):
    return f'<div class="{cls}">' + "".join(logo(n, lado) for n in nomes) + "</div>"


def foto(caminho, legenda, foco="50% 20%"):
    """Foto local embutida (P&B, mesmo tamanho para todas) — caminho relativo a conteudo/instagram/."""
    b64 = base64.b64encode((RAIZ / "conteudo" / "instagram" / caminho).read_bytes()).decode()
    return (f'<figure><img src="data:image/jpeg;base64,{b64}" style="object-position:{foco}">'
            f'<figcaption>{legenda}</figcaption></figure>')


def linhas(itens, lado=76):
    """Linhas em cartão com logos à esquerda: itens = [(marca, [logos], título, texto)]."""
    return '<div class="linhas">' + "".join(
        f'<div class="linha">{f"<span class=n>{m}</span>" if m else ""}'
        f'<div class="lg">{"".join(logo(n, lado) for n in lg)}</div>'
        f'<div class="tx"><b>{t}</b><span>{x}</span></div></div>' for m, lg, t, x in itens) + "</div>"


CARROSSEIS = {
    "001": {
        "pasta": "001-apresentacao",
        "slides": [
            {"grafico": True, "classe": " centro", "html": f"""
                {svg(300, 270, touro(150, 0, 1.6, brilho=False), 300, 270)}
                <h1>Day trading<br>com <span class="amb">dados</span>,<br>não com achismo.</h1>
                <p>Conheça a LHS Quant Lab e o que vamos construir aqui.</p>"""},
            {"html": """
                <div class="eyebrow">O problema</div>
                <h2>Você já operou um setup sem saber se ele funciona?</h2>
                <p>Print de lucro, vídeo bonito, “acerta 90% das vezes”.</p>
                <p>Nada disso prova que um método tem vantagem <span class="amb">depois dos custos</span> e ao longo de anos de mercado.</p>"""},
            {"html": """
                <div class="eyebrow">Nossa missão</div>
                <h1>Ensinar a <span class="amb">testar</span><br>e <span class="amb">operar</span><br>com dados.</h1>
                <p>A LHS Quant Lab é um laboratório de day trading baseado em dados: você aprende o método e decide com evidência, não com achismo.</p>"""},
            {"html": f"""
                <div class="eyebrow">Objetivo 1</div>
                <h2>Ensinar você a testar os seus próprios setups</h2>
                {lista(["Backtest do zero, passo a passo",
                        "Custos reais: spread, comissão e slippage",
                        "Separar teste e validação para não se enganar",
                        "Comparar o resultado com o acaso"])}"""},
            {"html": f"""
                <div class="eyebrow">Objetivo 2</div>
                <h2>Construir a base do day trading</h2>
                {lista(["Sessões do mercado: Ásia, Londres e Nova York",
                        "Gestão de risco e tamanho de posição",
                        "Os números do trader: payoff, expectativa e drawdown",
                        "Rotina e diário de operações com dados"])}"""},
            {"html": f"""
                <div class="eyebrow">Objetivo 3</div>
                <h2>Analisar os setups mais populares com dados</h2>
                {lista(["Anos de histórico, não um print de um dia bom",
                        "Relatório completo: acertos, payoff, drawdown e custos",
                        "Análise por sessão e por tempo gráfico",
                        "Você pede o setup, a gente testa"])}"""},
            {"html": f"""
                <div class="eyebrow">Como trabalhamos</div>
                <h2>O que fazemos e o que não fazemos</h2>
                <div class="duas">
                  <div><div class="col sim">Fazemos</div>
                  {lista(["Análises quantitativas", "Backtests com custos reais", "Educação passo a passo"], marca="✓", cls="sim")}</div>
                  <div><div class="col nao">Não fazemos</div>
                  {lista(["Sinais de compra e venda", "Promessa de lucro", "Recomendação de ativos"], marca="✕", cls="nao")}</div>
                </div>
                <p>Aqui é <span class="amb">educação e pesquisa de método</span>. A decisão de operar é sempre sua.</p>"""},
            {"grafico": True, "seed": 11, "classe": " centro", "html": f"""
                {svg(240, 216, touro(120, 0, 1.28, brilho=False), 240, 216)}
                <h1>Siga <span class="amb">@lhsquantlab</span></h1>
                <p>Comente qual setup você quer ver testado.<br>O mais pedido vira o próximo backtest.</p>
                <p>Salve este post para acompanhar a série.</p>"""},
        ],
        "legenda": """Day trading com dados, não com achismo. 📊

Este é o primeiro post da LHS Quant Lab, um laboratório de day trading baseado em evidência. Nossos objetivos:

1️⃣ Ensinar você a testar os seus próprios setups, com custos reais e validação honesta.
2️⃣ Construir a base do day trading: sessões, gestão de risco e os números que todo trader precisa conhecer.
3️⃣ Analisar os setups mais populares com dados: anos de histórico, custos e relatório completo.

Fazemos análises quantitativas, backtests e educação. Não vendemos sinais, não prometemos lucro e não recomendamos ativos.

👇 Comente qual setup você quer ver testado. O mais pedido vira o próximo backtest.

#daytrading #trading #backtest #forex #tradingquantitativo #educacaofinanceira #analisetecnica #mercadofinanceiro""",
    },
    "002": {
        "pasta": "002-ferramentas",
        "slides": [
            {"grafico": True, "seed": 5, "classe": " centro", "html": f"""
                <div class="eyebrow">Bastidores</div>
                <h1>As ferramentas da<br><span class="amb">LHS Quant Lab</span></h1>
                {logos(["mt5", "python", "anaconda", "jupyter", "mql5", "claude", "github", "obsidian"], 150, "grade")}
                <p>O que usamos para testar setups<br>com dados, não com achismo.</p>"""},
            {"html": f"""
                <div class="eyebrow">O fluxo</div>
                <h2>Do dado bruto à decisão</h2>
                {linhas([("01", ["mt5"], "Dados", "Candles e spread real da corretora"),
                         ("02", ["python", "jupyter"], "Análise", "Backtests em notebooks reprodutíveis"),
                         ("03", ["pandas", "scikitlearn"], "Validação", "Custos, fora da amostra e teste contra o acaso"),
                         ("04", ["mql5"], "Automação", "Só o setup aprovado vira robô"),
                         ("05", ["github", "obsidian"], "Registro", "Cada teste documentado, inclusive os reprovados")])}"""},
            {"html": f"""
                {logo("mt5", 180)}
                <div class="eyebrow">Dados e operação</div>
                <h2>MetaTrader 5</h2>
                {lista(["Candles da própria corretora, com o <span class='amb'>spread real</span> de cada barra",
                        "Até 16 anos de histórico no H1, atualizado todo dia",
                        "Conta demo para testar antes de arriscar um centavo"])}"""},
            {"html": f"""
                {logos(["anaconda", "python", "jupyter", "vscode"], 110)}
                <div class="eyebrow">O motor da análise</div>
                <h2>Anaconda, Python e Jupyter</h2>
                {lista(["<b>Anaconda:</b> ambiente isolado, o mesmo resultado em qualquer máquina",
                        "<b>Python:</b> anos de candles processados em segundos",
                        "<b>Jupyter:</b> código, gráfico e conclusão no mesmo caderno"])}
                <div class="sub">Bibliotecas: pandas · NumPy · Numba · scikit-learn</div>
                {logos(["pandas", "numpy", "numba", "scikitlearn"], 80)}""", "classe": " justo"},
            {"html": f"""
                {logos(["mql5", "mt5"], 160)}
                <div class="eyebrow">Automação</div>
                <h2>MQL5: do teste para o robô</h2>
                {lista(["Só o setup aprovado nos critérios vira EA ou indicador",
                        "Validado de novo no Strategy Tester do MT5",
                        "Execução sem emoção: a regra é a mesma do backtest"])}
                <p>Primeiro a <span class="amb">evidência</span>, depois a automação.</p>"""},
            {"html": f"""
                {logo("claude", 160)}
                <div class="eyebrow">Inteligência artificial</div>
                <h2>Claude: o assistente de pesquisa</h2>
                {lista(["Escreve e revisa o código dos backtests",
                        "Caça erros como o look-ahead (usar dado do futuro)",
                        "Gera o relatório pré-mercado todo dia às 4:30"])}
                <div class="regra"><b>Regra da casa:</b> a IA acelera, os dados decidem. Ela nunca envia ordem em conta real.</div>"""},
            {"html": f"""
                <div class="eyebrow">Os bastidores</div>
                <h2>O que ninguém vê</h2>
                {linhas([(None, ["banco"], "Parquet", "Milhões de candles guardados no próprio PC"),
                         (None, ["git", "github"], "Git e GitHub", "Histórico de cada teste, sem esconder os reprovados"),
                         (None, ["obsidian"], "Obsidian", "O diário da pesquisa"),
                         (None, ["telegram"], "Telegram", "Alertas e relatórios no celular")])}
                <div class="regra">Nenhuma ferramenta cria vantagem. O que separa evidência de sorte é o <b>método</b>:
                custos reais, teste fora da amostra e comparação com o acaso.</div>"""},
            {"grafico": True, "seed": 13, "classe": " centro", "html": f"""
                {svg(240, 216, touro(120, 0, 1.28, brilho=False), 240, 216)}
                <h1>Siga <span class="amb">@lhsquantlab</span></h1>
                <p>Comente qual ferramenta você quer<br>ver em detalhe.</p>
                <p>Próximo teste: rompimento da Ásia<br>na abertura de Londres.</p>"""},
        ],
        "legenda": """Não existe day trading baseado em evidência sem as ferramentas certas. 🛠️

Estas são as ferramentas do nosso laboratório:

📈 MetaTrader 5: os dados da corretora, com o spread real
🐍 Anaconda, Python e Jupyter: o motor dos backtests
🤖 MQL5: o setup aprovado vira robô
🧠 Claude (IA): o assistente de pesquisa e programação
🗂️ GitHub, Obsidian e Telegram: registro, diário e alertas

Quase tudo é gratuito. O diferencial não está na ferramenta, e sim no método: custos reais, teste fora da amostra e comparação com o acaso.

👇 Qual delas você quer ver em detalhe? Comente aqui.

#daytrading #python #mql5 #metatrader5 #backtest #tradingquantitativo #forex #inteligenciaartificial #jupyter #anaconda""",
    },
    "003": {
        "pasta": "003-eleicoes-preco-desconta-tudo",
        "slides": [
            {"grafico": True, "seed": 17, "classe": " centro justo", "html": f"""
                <div class="eyebrow">Eleições 2026</div>
                <div class="duelo">
                  {foto("003-eleicoes-preco-desconta-tudo/fotos/lula.jpg", "Lula", "50% 18%")}
                  <span class="x">×</span>
                  {foto("003-eleicoes-preco-desconta-tudo/fotos/flavio.jpg", "Flávio Bolsonaro", "62% 22%")}
                </div>
                <h2>Quem ganhou importa <span class="amb">menos</span> do que você pensa.</h2>
                <p>O que importa é estar preparado para a mudança.</p>
                <div class="credito">Fotos: Ricardo Stuckert/PR (CC BY 2.0) · Agência Senado — via Wikimedia Commons</div>"""},
            {"html": """
                <div class="eyebrow">Todo ciclo é igual</div>
                <h2>Semanas de previsões, certezas e “agora vai”</h2>
                <p>“O dólar vai disparar.” “A bolsa vai derreter.” “Se fulano ganhar, compra isso.”</p>
                <p>Ninguém sabe como o mercado vai reagir. E quem acerta uma vez quase sempre teve <span class="amb">sorte</span>, não método.</p>"""},
            {"html": """
                <div class="eyebrow">Teoria de Dow · princípio 1</div>
                <h1>O preço<br><span class="amb">desconta tudo.</span></h1>
                <p>Pesquisas, expectativas, medo e esperança já estavam sendo negociados muito antes da apuração.</p>
                <div class="regra">O mercado negocia <b>expectativa</b>, não o fato. Quando a notícia sai, boa parte dela já está no gráfico.</div>"""},
            {"html": f"""
                <div class="eyebrow">Notícia não é sinal</div>
                <h2>Notícia é um ponto de atenção</h2>
                {lista(["Volatilidade acima do normal: o stop de sempre pode ser curto demais",
                        "Spread alargado e slippage maior: o custo do trade sobe",
                        "Gaps na abertura e movimentos sem direção clara"], marca="!", cls="nao")}
                <p>A manchete diz <span class="amb">onde prestar atenção</span>. Quem diz o que fazer é o preço.</p>"""},
            {"html": f"""
                <div class="eyebrow">Foco no que depende de você</div>
                <h2>Controle o que dá para controlar</h2>
                <div class="duas">
                  <div><div class="col nao">Não controlamos</div>
                  {lista(["Quem ganhou", "A próxima manchete", "A reação do mercado"], marca="✕", cls="nao")}</div>
                  <div><div class="col sim">Controlamos</div>
                  {lista(["Risco por trade", "Stop e alvo definidos", "Setup testado com custos"], marca="✓", cls="sim")}</div>
                </div>"""},
            {"html": f"""
                <div class="eyebrow">Estar preparado</div>
                <h2>Checklist do day trader em semana de evento</h2>
                {lista(["Calendário econômico conferido antes de abrir o gráfico",
                        "Risco por trade definido antes da entrada, não durante",
                        "Setup com backtest que já passou por dias de alta volatilidade",
                        "Plano para spread alargado: reduzir a mão ou ficar de fora"])}"""},
            {"html": """
                <div class="eyebrow">Por que o quant</div>
                <h2>Opinião muda a cada manchete. O processo, não.</h2>
                <p>Um setup validado com anos de dados já atravessou eleições, crises e pandemia, com custos reais e fora da amostra.</p>
                <div class="regra">Governos mudam. <b>Preço, risco e estatística</b> continuam sendo o que decide o resultado do trade.</div>"""},
            {"grafico": True, "seed": 19, "classe": " centro", "html": f"""
                {svg(240, 216, touro(120, 0, 1.28, brilho=False), 240, 216)}
                <h1>Siga <span class="amb">@lhsquantlab</span></h1>
                <p>Você muda a sua operação<br>em semana de notícia? Conta aqui.</p>
                <p>Day trading com dados,<br>não com achismo.</p>"""},
        ],
        "legenda": """A eleição acabou. E o mercado? 🗳️📊

Não importa quem ganhou. Para quem opera, o que importa é estar preparado para a mudança.

Seguimos o primeiro princípio da Teoria de Dow: o preço desconta tudo. Pesquisas, expectativas, medo e esperança já estavam sendo negociados muito antes da apuração. O mercado negocia expectativa, não o fato.

Por isso, para nós, notícia é ponto de atenção, não sinal:
⚠️ volatilidade acima do normal
⚠️ spread alargado e slippage maior
⚠️ gaps e movimentos sem direção

O que decide o trade é o que dá para controlar: risco por trade, stop definido e um setup testado com dados e custos reais.

Opinião muda a cada manchete. O processo é o mesmo em qualquer governo.

👇 Você muda a sua operação em semana de notícia? Conta aqui.

Conteúdo educacional. Não é recomendação de investimento.
📷 Fotos oficiais: Ricardo Stuckert/PR (CC BY 2.0) e Agência Senado, via Wikimedia Commons.

#daytrading #eleicoes2026 #teoriadedow #trading #mercadofinanceiro #tradingquantitativo #gestaoderisco #backtest #forex #educacaofinanceira""",
    },
    "004": {
        "pasta": "004-antes-de-operar",
        "slides": [
            {"grafico": True, "seed": 23, "classe": " centro", "html": """
                <div class="eyebrow">Rotina pré-mercado</div>
                <h1>Antes de operar,<br>responda estas<br><span class="amb">7 perguntas.</span></h1>
                <p>O que day traders profissionais olham<br>antes de abrir a primeira ordem.</p>"""},
            {"html": """
                <div class="eyebrow">O erro mais comum</div>
                <h2>Abrir o gráfico e sair clicando</h2>
                <p>Sem saber o tipo de dia, os níveis, a notícia das 10h30 ou quanto pode perder hoje.</p>
                <div class="regra">O pré-mercado não é <b>sinal de entrada</b>. É preparação: entender o cenário antes de o preço andar.</div>
                <p>Al Brooks, a BabyPips e os relatórios matinais de forex fazem as mesmas perguntas. Vamos a elas.</p>"""},
            {"html": f"""
                <div class="eyebrow">Pergunta 1</div>
                <h2>Hoje é dia de <span class="amb">tendência</span> ou de <span class="amb">lateral</span>?</h2>
                {lista(["Na tendência: operar a favor e deixar o lucro correr",
                        "Na lateral: comprar embaixo, vender em cima, alvos curtos",
                        "O mercado passa a maior parte do tempo lateral",
                        "Por isso, a maioria dos rompimentos falha"])}
                <p>É a primeira pergunta do price action de Al Brooks.</p>"""},
            {"html": f"""
                <div class="eyebrow">Pergunta 2</div>
                <h2>Onde estão os níveis que importam?</h2>
                {lista(["Máxima, mínima e fechamento de ontem",
                        "Faixa da madrugada (sessão asiática)",
                        "Máxima e mínima da semana anterior",
                        "Números redondos: 1.1200, 1.1250…"])}
                <p>Funcionam como <span class="amb">alvo, barreira ou ímã</span>: o preço costuma voltar a testá-los.</p>"""},
            {"html": f"""
                <div class="eyebrow">Pergunta 3</div>
                <h2>Que notícia pode mexer no preço hoje?</h2>
                {lista(["Payroll e inflação (CPI) dos EUA",
                        "Decisões de juros do Fed e do BCE",
                        "Discursos de presidentes de banco central"], marca="!", cls="nao")}
                <div class="regra">Confira o <b>calendário econômico</b> antes de abrir o gráfico e defina uma janela sem operar antes e depois do dado.</div>"""},
            {"html": """
                <div class="eyebrow">Pergunta 4</div>
                <h2>Em que horário o mercado anda?</h2>
                <div class="card">
                  <div class="tit">SESSÕES · HORÁRIO DE BRASÍLIA · NOV A MAR</div>
                  <div class="hora">
                    <span>Ásia (Tóquio)</span><b>21h – 06h</b>
                    <span>Londres</span><b>05h – 14h</b>
                    <span>Nova York</span><b>10h – 19h</b>
                    <span class="top">Londres + Nova York</span><b class="top">10h – 14h</b>
                  </div>
                </div>
                <p>A sobreposição de Londres com Nova York é o período de <span class="amb">mais liquidez</span>. A Ásia costuma ser mais calma no EURUSD.</p>"""},
            {"html": f"""
                <div class="eyebrow">Perguntas 5 e 6</div>
                <h2>Qual é o plano? E quanto posso perder hoje?</h2>
                {lista(["Viés com condição: “vendedor enquanto abaixo de X”",
                        "O preço que <span class='amb'>invalida</span> a ideia, escrito antes",
                        "Risco por trade e perda máxima do dia definidos",
                        "Bateu a perda máxima? Plataforma fechada."])}"""},
            {"html": f"""
                <div class="eyebrow">Pergunta 7</div>
                <h2>Quanto custa operar agora?</h2>
                {lista(["Spread de agora × spread normal do ativo",
                        "Virada do dia e notícia: spread alargado",
                        "Custo alto come o lucro de alvos curtos"], marca="$")}
                <div class="regra">Bônus: <b>revise os trades de ontem</b>. O que deu certo, o que foi erro de execução e o que foi só o mercado.</div>"""},
            {"classe": " compacta", "html": f"""
                <div class="eyebrow">Salve e use todo dia</div>
                <h2>Checklist pré-mercado</h2>
                {lista(["Tendência ou lateral?",
                        "Níveis de ontem, da Ásia e da semana marcados",
                        "Calendário: notícias de alto impacto e horários",
                        "Sessão do dia e horário de sobreposição",
                        "Plano com nível de invalidação",
                        "Risco por trade e perda máxima do dia",
                        "Spread de agora × normal",
                        "Revisão dos trades de ontem"], marca="☐")}"""},
            {"grafico": True, "seed": 29, "classe": " centro", "html": f"""
                {svg(240, 216, touro(120, 0, 1.28, brilho=False), 240, 216)}
                <h1>Siga <span class="amb">@lhsquantlab</span></h1>
                <p>Qual dessas perguntas você<br>ainda pula? Conta aqui.</p>
                <p>Preparação não garante lucro.<br>Mas evita os erros bobos.</p>"""},
        ],
        "legenda": """Antes de operar, responda estas 7 perguntas. ✅

Pesquisamos o que os day traders olham antes da primeira ordem: o price action de Al Brooks, a rotina da BabyPips e os relatórios matinais de forex. As perguntas são sempre as mesmas:

1️⃣ Hoje é dia de tendência ou de lateral?
2️⃣ Onde estão os níveis que importam (ontem, Ásia, semana, números redondos)?
3️⃣ Que notícia pode mexer no preço hoje?
4️⃣ Em que horário o mercado anda? (Londres + Nova York: 10h às 14h de Brasília, de novembro a março)
5️⃣ Qual é o plano e o que invalida a ideia?
6️⃣ Quanto posso perder hoje?
7️⃣ Quanto custa operar agora (spread)?

O pré-mercado não é sinal de entrada. É preparação. A entrada vem do setup, e o setup só vale se tiver sido testado com dados e custos reais.

💾 Salve o checklist e use antes de cada sessão.
👇 Qual dessas você ainda pula? Conta aqui.

Conteúdo educacional. Não é recomendação de investimento.

#daytrading #forex #premercado #priceaction #trading #gestaoderisco #tradingquantitativo #eurusd #mercadofinanceiro #educacaofinanceira""",
    },
}


def render(html, destino):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={W},{H}", "--virtual-time-budget=10000", f"--screenshot={destino}",
                    Path(f.name).as_uri()], check=True, capture_output=True)
    Path(f.name).unlink()


def main(cid, so=None):
    """`so` = números dos slides a regerar (ex.: [3]); sem ele, gera todos."""
    c = CARROSSEIS[cid]
    out = RAIZ / "conteudo" / "instagram" / c["pasta"]
    out.mkdir(parents=True, exist_ok=True)
    n = len(c["slides"])
    for i, s in enumerate(c["slides"], 1):
        if so and i not in so:
            continue
        render(montar(s, i, n), out / f"{i:02d}.png")
    (out / "legenda.txt").write_text(c["legenda"], encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "001", [int(a) for a in sys.argv[2:]] or None)
