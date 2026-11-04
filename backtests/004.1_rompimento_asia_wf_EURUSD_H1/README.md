# Backtest 004.1 — Rompimento da Ásia com walk-forward · EURUSD H1 (16 anos)

| | |
|---|---|
| **Data** | 20/10/2026 |
| **Status** | ❌ Reprovado (5/7 critérios): vantagem real (PBO 0,12, melhor que o acaso), mas fator de lucro 1,04 e frequência 1,6/semana |
| **Base** | [Backtest 004](../004_rompimento_asia_EURUSD_M15-H1/) (mesmo setup e mesmas 128 combinações) |
| **Dados** | XM (MT5), EURUSD H1 desde set/2010 (conta Standard); H4 como filtro |
| **Notebook de origem** | [`notebooks/10_backtest_004_1_walkforward_h1.ipynb`](../../notebooks/10_backtest_004_1_walkforward_h1.ipynb) |

## 1. O que foi testado
O 004 usou uma única divisão treino × teste. Aqui a otimização é refeita a cada janela: escolhe a melhor das 128
combinações nos **36 meses** anteriores e opera os **6 meses** seguintes, andando 6 meses por vez. São 27 janelas e
cerca de **13 anos fora da amostra** (out/2013 → out/2026). Inclui o **PBO** (CSCV, 10 blocos, 252 combinações) e o
teste do acaso refazendo o walk-forward inteiro com direção sorteada.

## 2. Resultados e conclusão
### Fora da amostra (2013–2026)
| Métrica | Walk-forward | Clássica fixa | Escolha do 004 fixa |
|---|---:|---:|---:|
| Nº de operações | 1.069 | 2.994 | 1.326 |
| Win rate | 41,3% | 41,8% | 40,7% |
| Payoff | 1,47 | 1,36 | 1,50 |
| Expectativa sem custos | +0,105 R | +0,063 R | +0,101 R |
| Expectativa líquida | **+0,020 R** | −0,012 R | +0,017 R |
| Fator de lucro | 1,04 | 0,98 | 1,03 |
| Máx. drawdown (período) | −48% | −69% | −46% |
| Sharpe | 0,14 | −0,15 | 0,12 |

### Critérios
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 1.069 | ✅ |
| Expectativa > 0 R | +0,020 | ✅ |
| Fator de lucro > 1,2 | 1,04 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,017 | ✅ |
| PBO < 0,5 | 0,12 | ✅ |
| Nenhum ano com DD > 20% | pior −14,7% | ✅ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 1,6/sem · p90 8 | ❌ |

1. **A vantagem é real, mas fina:** +0,105 R sem custos, melhor que o acaso e PBO baixo (as campeãs continuam acima da mediana).
2. **Os custos levam ~80%:** ~0,085 R por operação; com comissão de US$ 7, −0,009 R.
3. **Difícil de aguentar:** 2016–2021 quase só negativos; drawdown do período −48% (nenhum ano isolado passou de −15%).
4. **Peças que o walk-forward repete:** stop no lado oposto (24/27), a favor do H4 (21/27), faixa estreita (22/27), sem alvo (17/27).
5. **Vendas +0,10 R × compras −0,06 R:** efeito do dólar forte.

**Veredito:** ❌ **reprovado.** Próximo teste: custos menores → [004.2](../004.2_rompimento_asia_ultralow_EURUSD_H1/).

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook |
| `parametros.json` | configuração exata (janelas, grade, custos) |
| `walkforward.csv` | combinação escolhida e resultado de cada janela |
| `metricas_oos.csv` | walk-forward × clássica fixa × escolha do 004 fixa |
| `criterios.csv` | os 7 critérios e o resultado |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Python:** `notebooks/10_backtest_004_1_walkforward_h1.ipynb` no VS Code (kernel `financeiro`).
- **PDF:** `python scripts/exportar_pdf.py 10_backtest_004_1_walkforward_h1`.
