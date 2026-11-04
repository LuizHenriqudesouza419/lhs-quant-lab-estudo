# Backtest 002.1 — Pullback na EMA, nova saída + mais sinais · EURUSD H4, H1 e M15

| | |
|---|---|
| **Data** | 19/10/2026 |
| **Status** | ❌ Reprovado (3/7 critérios): a frequência foi resolvida, mas o setup não tem vantagem bruta e os custos levam ~0,2 R por operação |
| **Base** | [Backtest 002](../002_pullback_ema_EURUSD_H4-H1-M15/) (mesma tendência, mesmo motor) |
| **Dados** | XM (MT5), EURUSD. M15 desde out/2022; H4 e H1 como filtro |
| **Notebook de origem** | [`notebooks/06_backtest_002_1_saida_frequencia.ipynb`](../../notebooks/06_backtest_002_1_saida_frequencia.ipynb) |

## 1. O que foi testado
O 002 tinha dois problemas: a **saída** devolvia o lucro (trailing de 3 ATR largo demais para um stop de ~1 ATR) e a
**frequência** era baixa (0,6 operação/semana). O 002.1 ataca os dois ao mesmo tempo:

| Peça | Variações |
|---|---|
| **Saída** | trailing K = 3, 2, 1,5, 1 ATR · K = 3 + zero a zero ao chegar em +1 R |
| **Regra do recuo novo** | com (3 barras sem tocar a média) · sem (qualquer toque na zona) |
| **Filtro** | H4 + H1 · só H1 |
| **Médias do pullback** | 10/50 · 20/50 |

São **40 combinações**. **Padrão fixado antes de rodar:** 20/50, H4+H1, sem a regra das 3 barras, trailing 1,5 ATR.
Validação, custos e regras de execução iguais às do 002 (consistência por bloco, PBO, walk-forward de 12 → 3 meses,
spread real ×1,5 na virada do dia, slippage, comissão, zerar às 23h).

## 2. Resultados e conclusão
### Fora da amostra (nov/2023 → out/2026, líquido)
| Métrica | Walk-forward | Padrão fixo |
|---|---:|---:|
| Nº de operações | 856 | 910 |
| Win rate | 27,1% | 29,8% |
| Payoff | 1,59 | 1,33 |
| Expectativa líquida | **−0,236 R** | −0,198 R |
| Expectativa sem custos | −0,011 R | +0,025 R |
| Fator de lucro | 0,59 | 0,56 |
| Retorno (1% de risco) | −87,5% | −84,2% |
| Máx. drawdown | −87,4% | −84,2% |
| Sharpe | −3,17 | −3,49 |
| Frequência | 5,5/semana · p90 4 dias | 5,9/semana · p90 5 dias |

### Critérios
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 856 | ✅ |
| Expectativa > 0 R | −0,236 | ❌ |
| Fator de lucro > 1,2 | 0,59 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,040 | ✅ |
| PBO < 0,5 | 0,77 | ❌ |
| Nenhum ano com DD > 20% | pior −57,4% | ❌ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 5,5/sem · p90 4 | ✅ |

**1. A frequência foi resolvida.** Tirar a regra das 3 barras multiplicou os sinais: 5,5 operações/semana, com no máximo 4 dias úteis
sem operar em 90% das vezes. Serve para day trade.
**2. Mas o setup não tem vantagem bruta.** Sem custos, a expectativa fica em torno de **zero** (−0,01 R no walk-forward, +0,03 R no padrão).
É um sinal ligeiramente melhor que o acaso (p = 0,04), mas pequeno demais para pagar o spread.
**3. No M15 o custo é ~0,2 R por operação.** Com stop de ~1 ATR do M15 (poucos pips), o spread + slippage pesa 20% do risco.
Mais operações só multiplicaram o prejuízo: −87% com 1% de risco.
**4. Saída mais curta ajudou pouco.** O melhor da grade (10/50 · recuo novo · H4+H1 · K 1,5) foi de −0,14 R para −0,10 R, ainda negativo.
Alvo fixo de 2R foi pior (−0,27 R). O zero a zero em +1 R foi escolhido em parte das janelas, sem mudar o sinal do resultado.
**5. A otimização segue escolhendo ruído.** PBO de 0,77; todas as 12 janelas do walk-forward ficaram negativas, exceto uma (+1,6 R).
**6. Filtros não mudam o quadro.** H4+H1, só H4, só H1, sem filtro e contra a tendência: todos entre −0,17 e −0,22 R.

**Veredito:** ❌ **reprovado.** O pullback na EMA do M15 está esgotado no EURUSD: já testamos médias, filtros, saídas e frequência.

> Os números acima mudam conforme os dados forem atualizados. Ao rodar de novo, confira as tabelas.

### Lições para o day trade da LHS
- **Antes de otimizar, olhar a expectativa bruta.** Se ela é ~0 sem custos, nenhuma saída ou filtro salva o setup.
- **Stop pequeno no M15 = custo grande em R.** O próximo setup precisa de stop/alvo de vários ATR do M15 (ou gatilho no H1),
  para o spread pesar menos de ~5% do risco.
- **Próximo da fila:** rompimento da faixa asiática na abertura de Londres (H1/M15), que tem alvo naturalmente grande em relação ao spread.

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook com todas as saídas |
| `parametros.json` | configuração exata (grade de saídas, regra do recuo, filtros, custos, walk-forward) |
| `metricas_oos.csv` | fora da amostra: walk-forward × padrão fixo |
| `criterios.csv` | os 7 critérios de aprovação e o resultado |
| `grade_otimizacao.csv` | as 40 combinações no período todo |
| `blocos.csv` | resultado de cada combinação em cada um dos 8 blocos |
| `walkforward.csv` | combinação escolhida em cada janela, frequência no treino e R do teste |
| `grupos.csv` | comparação de filtros e de alvo fixo 2R |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Python:** abra `notebooks/06_backtest_002_1_saida_frequencia.ipynb` no VS Code (kernel `financeiro`) e rode tudo.
- **PDF:** `python scripts/exportar_pdf.py 06_backtest_002_1_saida_frequencia`.
