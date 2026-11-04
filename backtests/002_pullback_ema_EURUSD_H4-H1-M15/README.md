# Backtest 002 — Pullback na EMA com 3 tempos gráficos · EURUSD H4, H1 e M15

| | |
|---|---|
| **Data** | 19/10/2026 |
| **Status** | ❌ Reprovado (1/7 critérios): negativo até antes dos custos e com poucos sinais para day trade |
| **Dados** | XM (MT5), EURUSD. M15 desde out/2022 (limite de barras do MT5); H4 e H1 como filtro |
| **Notebook de origem** | [`notebooks/05_backtest_002_pullback_ema.ipynb`](../../notebooks/05_backtest_002_pullback_ema.ipynb) |

## 1. O que foi testado
**Ideia:** com **H4 e H1 em tendência na mesma direção**, esperar o **M15 recuar até a EMA rápida** e entrar quando ele
volta a andar a favor dos gráficos maiores.

- **Tendência (H4 e H1):** fechamento acima da EMA de tendência, EMA 50 acima dela e EMA de tendência subindo (vs. 20 barras atrás). Baixa é o espelho.
- **Gatilho (M15):** EMA rápida > lenta; 3 barras sem tocar a EMA rápida (recuo novo); a barra toca a EMA rápida e fecha de volta a favor, com candle a favor.
- **Saída:** stop inicial no fundo das 3 últimas barras − 0,1 ATR (só entra se ficar entre 0,5 e 3 ATR); trailing Chandelier 3 × ATR 14;
  sai também se o H1 perder a tendência ou às 23h (zera no fim do dia, sem swap).
- **Sem look-ahead:** H4/H1 levados ao M15 pelo horário de **fechamento** (`merge_asof`); sinal na barra fechada, entrada na abertura seguinte.
- **Custos:** spread real de cada barra (×1,5 na virada do dia) + slippage + comissão. Comparação sempre "sem custos × líquido".
- **Otimização:** 12 combinações (EMA de tendência {100, 200} × pullback {10, 20, 30}/{50, 100}), validadas por consistência em 8 blocos,
  **PBO** (CSCV, 70 divisões) e **walk-forward** (treino 12 meses, teste 3).

## 2. Resultados e conclusão
### Fora da amostra (walk-forward, nov/2023 → out/2026, líquido)
| Métrica | Valor |
|---|---:|
| Nº de operações | 86 |
| Win rate | 18,6% |
| Payoff | 1,43 |
| Expectativa | **−0,51 R** (sem custos: −0,24 R) |
| Fator de lucro | 0,33 |
| Retorno (1% de risco) | −35,9% |
| Máx. drawdown | −35,4% |
| Sharpe / Sortino | −2,26 / −2,89 |
| Frequência | 0,56 operação/semana · p90 de 22 dias úteis sem operar |

### Critérios (definidos antes de rodar)
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 86 | ❌ |
| Expectativa > 0 R | −0,510 | ❌ |
| Fator de lucro > 1,2 | 0,33 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,942 | ❌ |
| PBO < 0,5 | 0,87 | ❌ |
| Nenhum ano com DD > 20% | pior −15,3% | ✅ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 0,6/sem · p90 22 | ❌ |

**1. Não há vantagem nem antes dos custos.** Fora da amostra, a expectativa bruta já é −0,24 R. Os custos levam a −0,51 R.
**2. O pullback não ganha do acaso.** Entradas aleatórias com H4 e H1 alinhados foram melhores em 94% dos sorteios (p = 0,94).
**3. A otimização escolhe sorte.** PBO de 0,87. Nenhuma das 12 combinações fica positiva líquida no período todo; a melhor (T200 · 10/50) dá −0,14 R.
**4. O filtro H4 + H1 não ajuda.** Todos os grupos (H4+H1, só H4, só H1, sem filtro, contra a tendência) ficam entre −0,30 e −0,49 R, com intervalos de confiança sobrepostos.
**5. Poucos sinais para day trade.** 0,6 operação/semana, longe das 2 exigidas.

**Diagnóstico que gerou o 002.1:** 40% das operações chegavam a +1 R, mas só ~25% fechavam no lucro. Com stop de ~1 ATR,
o trailing de 3 ATR só protege depois de +2 R; antes disso o lucro volta inteiro.

**Veredito:** ❌ **reprovado.**

> Os números acima mudam conforme os dados forem atualizados. Ao rodar de novo, confira as tabelas.

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook com todas as saídas |
| `parametros.json` | configuração exata (tendência, pullback, grade, saída, custos, walk-forward) |
| `metricas_oos.csv` | fora da amostra: walk-forward × padrão fixo |
| `criterios.csv` | os 7 critérios de aprovação e o resultado |
| `grade_otimizacao.csv` | as 12 combinações no período todo |
| `blocos.csv` | resultado de cada combinação em cada um dos 8 blocos |
| `walkforward.csv` | combinação escolhida em cada janela e R do teste |
| `grupos.csv` | comparação de filtros (H4+H1, só H4, só H1, sem filtro, contra a tendência, alvo fixo 2R) |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Python:** abra `notebooks/05_backtest_002_pullback_ema.ipynb` no VS Code (kernel `financeiro`) e rode tudo.
- **PDF:** `python scripts/exportar_pdf.py 05_backtest_002_pullback_ema`.
