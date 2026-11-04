"""Rotina diária: acrescenta os candles novos de todos os pares e timeframes.

Rodar manualmente:  python scripts/atualizar_dados.py
Agendado pelo Windows (tarefa "LHS Quant Lab - Atualizar dados").
"""
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant.avisos import tarefa  # noqa: E402
from lhsquant.dados import atualizar_tudo  # noqa: E402

LOG = RAIZ / "logs" / "atualizar_dados.log"


def main():
    LOG.parent.mkdir(exist_ok=True)
    inicio = datetime.now()
    try:
        with tarefa("Atualizar dados") as t:  # avisa início, fim e erro no Telegram
            resumo = atualizar_tudo()
            texto = resumo.to_string(index=False)
            t.concluir(texto)
        status = "OK"
    except Exception as e:  # registra o erro no log para ver depois
        texto = repr(e)
        status = "ERRO"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n=== {inicio:%Y-%m-%d %H:%M} | {status} | {datetime.now() - inicio} ===\n{texto}\n")
    print(texto)
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
