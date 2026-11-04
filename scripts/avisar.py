"""Manda um aviso avulso para o Telegram (chat privado do @lhsquantlab_bot).

    python scripts/avisar.py "Backtest 002 pronto: PF 1,12 líquido · 214 trades"
    python scripts/avisar.py "Curva de capital do 002" --imagem resultados/002/equity.png
    python scripts/avisar.py "Relatório do 002" --arquivo resultados/002/relatorio.pdf
    python scripts/avisar.py "Rodando H1..." --silencioso

Para tarefas longas dentro de um script, prefira `lhsquant.avisos.tarefa`
(manda início com previsão, fim e erro sozinho).
"""
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant import notificar  # noqa: E402


def main():
    p = argparse.ArgumentParser(description="Aviso avulso no Telegram")
    p.add_argument("texto")
    p.add_argument("--imagem", help="PNG/JPG; o texto vira legenda")
    p.add_argument("--arquivo", help="PDF/CSV/HTML...; o texto vira legenda")
    p.add_argument("--silencioso", action="store_true", help="chega sem som")
    a = p.parse_args()
    if a.imagem:
        ok = notificar.enviar_imagem(a.imagem, a.texto, silencioso=a.silencioso)
    elif a.arquivo:
        ok = notificar.enviar_arquivo(a.arquivo, a.texto, silencioso=a.silencioso)
    else:
        ok = notificar.enviar_texto(a.texto, silencioso=a.silencioso)
    print("enviado" if ok else "falhou")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
