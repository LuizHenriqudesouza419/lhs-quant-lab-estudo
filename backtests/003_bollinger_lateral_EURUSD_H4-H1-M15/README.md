# Backtest 003 — Bandas de Bollinger em mercado lateral · EURUSD H4, H1 e M15

| | |
|---|---|
| **Data** | 20/10/2026 |
| **Status** | ❌ Reprovado (3/6 critérios): perde depois dos custos nos três tempos gráficos; o único positivo (H4) tem poucas operações e não supera o acaso |
| **Dados** | XM (MT5), EURUSD. H4 e H1 desde 2010; M15 desde out/2022 |
| **Notebook de origem** | [`notebooks/07_backtest_003_bollinger_lateral.ipynb`](../../notebooks/07_backtest_003_bollinger_lateral.ipynb) |

## 1. O que foi testado
**Hipótese:** em mercado lateral o preço volta à média. Comprar no fundo da banda e vender no topo, com alvo no meio.

| Item | Regra |
|---|---|
| Bandas | Bollinger 21 períodos, 2 desvios; "meio" = média de 21 |
| Lateralidade | média de 200 andou menos que *k* × ATR em 20 barras |
| Entrada | fechou fora da banda (padrão) ou voltou para dentro → abertura da barra seguinte |
| Saída | barra fecha no meio da banda; stop de *N* × ATR |
| Day trade | sinal 9h–21h (servidor), zera às 23h, spread real ×1,5 na virada do dia, slippage 2 pts/lado |

**Padrão (como descrito):** fechou fora, *k* = 0,5, stop 3 ATR, zera no fim do dia. **Grade:** 48 combinações por
tempo gráfico (gatilho × 4 filtros × 3 stops × zerar), escolhida só no treino. **Fora da amostra:** H4/H1 2021–2026,
M15 2025–2026. Comparação com entradas aleatórias no mesmo regime.

## 2. Resultados e conclusão
### Regra padrão, fora da amostra
| Métrica | H4 | H1 | M15 |
|---|---:|---:|---:|
| Nº de operações | 156 | 653 | 630 |
| Win rate | 46% | 49% | 58% |
| Payoff | 0,93 | 0,92 | 0,59 |
| Expectativa sem custos | 0,00 R | +0,03 R | +0,05 R |
| Expectativa líquida | **−0,03 R** | **−0,03 R** | **−0,07 R** |
| Máx. drawdown | −7% | −25% | −39% |

### Melhor do treino, fora da amostra
| | H4 | H1 | M15 |
|---|---:|---:|---:|
| Configuração | voltou para dentro, *k* 0,25, stop 1,5, sem zerar | voltou para dentro, *k* 0,5, stop 3, zera | fechou fora, *k* 0,5, stop 3 |
| Operações | 36 | 517 | 630 |
| Expectativa líquida | +0,105 R | −0,019 R | −0,063 R |
| p vs aleatório | 0,22 | 0,08 | 0,00 |

### Critérios (melhor tempo gráfico: H4)
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 36 | ❌ |
| Expectativa > 0 R | +0,105 | ✅ |
| Fator de lucro > 1,2 | 1,23 | ✅ |
| Melhor que aleatório (p < 0,05) | p = 0,223 | ❌ |
| Nenhum ano com DD > 20% | pior −3,0% | ✅ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 0,1/sem · p90 99 | ❌ |

1. **A regra padrão perde nos três tempos gráficos** depois dos custos.
2. **No M15 há vantagem bruta pequena** (todas as 48 combinações positivas sem custos no treino; melhor que o acaso),
   mas o custo de ~0,11 R por operação a inverte. Mesma lição do 002.1.
3. **No H1, zerar no fim do dia atrapalha:** 269 de 517 operações encerradas antes do meio da banda (−0,125 R em média).
4. **O H4 positivo tem só 36 operações** e não supera o acaso. Sem o filtro: 200 operações e +0,09 R — pista testada no 003.1.
5. **O filtro da média de 200 lateral ajuda pouco.** "Voltou para dentro" foi melhor que "fechou fora" no H4 e no H1.

**Veredito:** ❌ **reprovado.**

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook |
| `parametros.json` | configuração exata e combinação escolhida por tempo gráfico |
| `metricas_padrao.csv` | regra padrão, treino × fora |
| `metricas_oos.csv` | melhor do treino, fora da amostra |
| `grade_otimizacao.csv` | as 48 combinações por tempo gráfico |
| `criterios.csv` | critérios e resultado |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Python:** `notebooks/07_backtest_003_bollinger_lateral.ipynb` no VS Code (kernel `financeiro`).
- **PDF:** `python scripts/exportar_pdf.py 07_backtest_003_bollinger_lateral`.
