# Backtest 004 — Rompimento da faixa asiática na abertura de Londres · EURUSD M15 e H1 (filtro H4)

| | |
|---|---|
| **Data** | 20/10/2026 |
| **Status** | ❌ Reprovado por pouco (5/6 critérios no H1; fator de lucro 1,07 < 1,2). Primeiro setup com vantagem bruta consistente |
| **Dados** | XM (MT5), EURUSD. H1 desde 2010; M15 desde out/2022; H4 como filtro de tendência |
| **Notebook de origem** | [`notebooks/09_backtest_004_rompimento_asia.ipynb`](../../notebooks/09_backtest_004_rompimento_asia.ipynb) |

## 1. O que foi testado
**Hipótese:** a madrugada asiática forma uma faixa estreita; na abertura de Londres o preço rompe um lado e segue.

| Item | Regra |
|---|---|
| Faixa | máxima/mínima das 00h (ou 03h) às 10h do servidor |
| Abertura de Londres | 10h do servidor = 8h em Londres, o ano todo |
| Entrada | ordem stop 1 pip além da faixa (clássico) ou fechamento fora da faixa; das 10h às 15h; 1 operação por dia |
| Stop / alvo | lado oposto ou meio da faixa · 1 R, 1,5 R, 2 R ou sem alvo (fim do dia) |
| Filtros | faixa estreita (abaixo da mediana de 20 dias) · a favor da tendência do H4 |
| Day trade | zera às 23h; spread real ×1,5 na virada; slippage 2 pts/lado |

128 combinações por tempo gráfico, escolhidas só no treino. Fora da amostra: H1 2021–2026, M15 2025–2026. Teste do
acaso: mesmos dias e horários, **direção sorteada**.

## 2. Resultados e conclusão
### Regra clássica (sem otimização)
| Métrica | M15 treino | M15 fora | H1 treino | H1 fora |
|---|---:|---:|---:|---:|
| Nº de operações | 532 | 396 | 2.364 | 1.332 |
| Win rate | 41% | 42% | 42% | 43% |
| Expectativa sem custos | +0,05 R | −0,01 R | +0,04 R | **+0,08 R** |
| Expectativa líquida | −0,04 R | −0,09 R | −0,01 R | **0,00 R** |
| p vs aleatório (fora) | | 0,54 | | **0,007** |

### Melhor do treino, fora da amostra
| | M15 | H1 |
|---|---:|---:|
| Configuração | faixa 03h, fechamento, faixa estreita, a favor do H4 | faixa 03h, ordem stop, stop lado oposto, sem alvo, a favor do H4 |
| Operações | 108 | 608 |
| Expectativa líquida | −0,061 R | **+0,037 R** |
| Fator de lucro | 0,88 | 1,07 |
| Máx. drawdown | −19% | −24% |
| Com comissão US$ 7 | −0,089 R | +0,009 R |

### Critérios (H1)
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 608 | ✅ |
| Expectativa > 0 R | +0,037 | ✅ |
| Fator de lucro > 1,2 | 1,07 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,017 | ✅ |
| Nenhum ano com DD > 20% | pior −13,6% | ✅ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 2,0/sem · p90 5 | ✅ |

1. **No H1, a direção do rompimento tem informação:** vantagem sem custos no treino e fora, acima do acaso.
2. **Os custos (~0,08 R) levam quase tudo:** a regra clássica fica em 0,00 R líquido.
3. **O treino não confirma com força** (+0,008 R na configuração escolhida) e os anos fora da amostra alternam.
4. **No M15, sobreajuste:** a campeã do treino (+0,19 R) virou −0,06 R.
5. **Não ajudam:** stop no meio da faixa, alvos fixos e o filtro de faixa estreita.
6. **Vendas ganharam e compras perderam:** reflexo do dólar forte de 2021–2026.

**Veredito:** ❌ **reprovado por pouco.** Continuado no [004.1](../004.1_rompimento_asia_wf_EURUSD_H1/) (walk-forward) e no [004.2](../004.2_rompimento_asia_ultralow_EURUSD_H1/) (custos da conta Ultra Low).

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook |
| `parametros.json` | configuração exata |
| `metricas_padrao.csv` | regra clássica, treino × fora |
| `metricas_oos.csv` | melhor do treino, fora da amostra |
| `classica_oos.csv` | regra clássica fora da amostra contra o acaso |
| `grade_otimizacao.csv` | as 128 combinações por tempo gráfico |
| `criterios.csv` | critérios e resultado |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Python:** `notebooks/09_backtest_004_rompimento_asia.ipynb` no VS Code (kernel `financeiro`).
- **PDF:** `python scripts/exportar_pdf.py 09_backtest_004_rompimento_asia`.
