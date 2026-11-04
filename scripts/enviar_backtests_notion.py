"""Sincroniza os relatórios dos backtests (backtests/*/README.md) com o Notion.

Uma subpágina por backtest dentro de "Relatórios de Backtest".

Uso:
    python scripts/enviar_backtests_notion.py           # todos os backtests do índice
    python scripts/enviar_backtests_notion.py 004.2     # só os IDs indicados

Lê o índice backtests/README.md (ID, setup, status) e usa o README de cada pasta como conteúdo
da página. Rodar de novo substitui a página do mesmo backtest.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant import notion  # noqa: E402

PASTA = RAIZ / "backtests"


def numero(s: str) -> float | None:
    """Primeiro número de uma célula como '−0,17 (H4, K=3)', '1.069' ou '−34,6%'."""
    m = re.search(r"[−-]?\d[\d.]*(?:,\d+)?", s)
    if not m:
        return None
    return float(m.group().replace("−", "-").replace(".", "").replace(",", "."))


def ler_indice() -> list:
    linhas = [l for l in (PASTA / "README.md").read_text(encoding="utf-8").splitlines()
              if l.startswith("| [")]
    itens = []
    for l in linhas:
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        id_, pasta = re.match(r"\[(.+?)\]\((.+?)/?\)", c[0]).groups()
        status = "aprovado" if "✅" in c[7] else "promissor" if "🟡" in c[7] else "reprovado"
        readme = (PASTA / pasta / "README.md").read_text(encoding="utf-8")
        data = re.search(r"\*\*Data\*\* \| (\d\d)/(\d\d)/(\d{4})", readme)
        itens.append({"id": id_, "setup": c[1], "par_tf": c[2], "periodo": c[3],
                      "trades": numero(c[4]), "sharpe": numero(c[5]), "dd": numero(c[6]), "status": status,
                      "data": f"{data[3]}-{data[2]}-{data[1]}" if data else None, "md": readme})
    return itens


def main():
    if not notion.configurado("NOTION_PAGINA_BACKTESTS"):
        print("Notion não configurado: preencha NOTION_TOKEN e NOTION_PAGINA_BACKTESTS no .env")
        return 1
    filtro = set(sys.argv[1:])
    falhas = 0
    for b in ler_indice():
        if filtro and b["id"] not in filtro:
            continue
        try:
            print(f"{b['id']:>6} ✅ {notion.enviar_backtest(b['id'], b['setup'], b['status'], b['md'])}")
        except Exception as e:
            falhas += 1
            print(f"{b['id']:>6} ❌ {e}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
