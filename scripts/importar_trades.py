"""Rotina diária do Diário de Trading: importa os trades fechados da conta logada no MT5
e manda o resumo do dia no Telegram (só se houve trade). Só leitura: nenhuma ordem é enviada.

Rodar manualmente:  python scripts/importar_trades.py
Agendado pelo Windows (tarefa "LHS Quant Lab - Importar trades", seg–sex 19:00).
"""
import sys
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant import notificar  # noqa: E402
from lhsquant.diario import banco, comparar_bt, importar_mt5, metricas  # noqa: E402

LOG = RAIZ / "logs" / "importar_trades.log"


def num(v, sufixo=""):
    return "—" if v != v else f"{'+' if v > 0 else '−' if v < 0 else ''}{abs(v):.2f}".replace(".", ",") + sufixo


def resumo_telegram(conta, df):
    hoje = df[df["saida"].dt.date == date.today()]
    if hoje.empty:
        return None
    linhas = [f"<b>Diário de trading · {date.today():%d/%m}</b>",
              f"Conta {conta['tipo'].upper()} {conta['login']}",
              f"{len(hoje)} trades · líquido {num(hoje['liquido'].sum())} {conta['moeda']} · {num(hoje['R'].sum(), 'R')}"]
    for t in hoje.itertuples():
        linhas.append(f"• {t.simbolo} {t.lado} · {t.setup} · {num(t.liquido)} · {num(t.R, 'R')} ({t.motivo_saida})")
    cfg = importar_mt5.setups()
    for setup in hoje["setup"].unique():
        bt = (cfg.get(setup) or {}).get("backtest")
        if bt and (comparar_bt.PASTA_BT / bt).exists():
            r = comparar_bt.comparar(df, setup, bt)
            if r["veredito"] == "Reprovado":
                linhas.append(f"⚠️ <b>{setup}</b> abaixo da faixa do backtest: "
                              f"{num(r['expect_real'], 'R')} × esperado ≥ {num(r['expect_p5'], 'R')}")
    linhas.append("Anote os trades no Diário antes de esquecer.")
    return "\n".join(linhas)


def main():
    LOG.parent.mkdir(exist_ok=True)
    inicio = datetime.now()
    try:
        r = importar_mt5.importar()
        texto = f"conta {r['conta']['tipo']} {r['conta']['login']} · {r['trades']} trades · {r['novos']} novos"
        df = metricas.preparar(banco.carregar(r["conta"]["login"]))
        msg = resumo_telegram(r["conta"], df) if not df.empty else None
        if msg:
            notificar.enviar_texto(msg, html=True)
        status = "OK"
    except Exception as e:  # registra o erro no log para ver depois
        texto, status = repr(e), "ERRO"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n=== {inicio:%Y-%m-%d %H:%M} | {status} | {datetime.now() - inicio} ===\n{texto}\n")
    print(texto)
    return 0 if status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
