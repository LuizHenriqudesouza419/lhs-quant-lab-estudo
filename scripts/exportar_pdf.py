"""Exporta os notebooks de backtest para PDF, sem as células de código.

Executa cada notebook (para os resultados ficarem atualizados), gera um HTML só com
textos, tabelas e gráficos e usa o Edge em modo headless para imprimir em PDF.

Uso:
    python scripts/exportar_pdf.py                       # todos os notebooks de backtest
    python scripts/exportar_pdf.py 02_primeiro_backtest  # só os indicados
    python scripts/exportar_pdf.py --sem-executar        # usa as saídas já salvas no .ipynb

Os PDFs vão para resultados/relatorios/.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PASTA_NOTEBOOKS = RAIZ / "notebooks"
PASTA_PDF = RAIZ / "resultados" / "relatorios"
NAO_SAO_BACKTEST = {"01_motor_de_dados"}
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")


def exportar(notebook, executar=True):
    PASTA_PDF.mkdir(parents=True, exist_ok=True)
    pdf = PASTA_PDF / f"{notebook.stem}.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", "--no-input",
               "--no-prompt", "--output-dir", tmp, "--output", notebook.stem, str(notebook)]
        if executar:
            cmd.insert(-1, "--execute")
        # cwd = pasta do notebook, porque os caminhos dos dados são relativos a ela
        subprocess.run(cmd, check=True, cwd=notebook.parent, capture_output=True)
        html = Path(tmp) / f"{notebook.stem}.html"
        subprocess.run([str(EDGE), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={pdf}", html.as_uri()],
                       check=True, capture_output=True, timeout=180)
    return pdf


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    executar = "--sem-executar" not in sys.argv
    if args:
        notebooks = [PASTA_NOTEBOOKS / f"{Path(a).stem}.ipynb" for a in args]
    else:
        notebooks = [n for n in sorted(PASTA_NOTEBOOKS.glob("*.ipynb")) if n.stem not in NAO_SAO_BACKTEST]
    for nb in notebooks:
        print(f"{nb.name} ...", end=" ", flush=True)
        pdf = exportar(nb, executar)
        print(f"ok -> {pdf.relative_to(RAIZ)} ({pdf.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
