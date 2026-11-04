# Backtest 004.2 — Rompimento da Ásia na conta Micro Ultra Low · EURUSD H1 (walk-forward)

| | |
|---|---|
| **Data** | 20/10/2026 |
| **Status** | ❌ Reprovado (3/7 critérios): o custo cai 40% e as configurações fixas passam a ganhar, mas o fator de lucro fica em no máximo 1,11 |
| **Base** | [Backtest 004.1](../004.1_rompimento_asia_wf_EURUSD_H1/) (mesmo setup, mesmo walk-forward) |
| **Dados** | Preços do EURUSD Standard (H1 desde 2010) + spread do `EURUSDm#` (conta Micro Ultra Low da XM, registrado desde out/2018; antes, 50% do Standard) |
| **Notebook de origem** | [`notebooks/11_backtest_004_2_ultra_low.ipynb`](../../notebooks/11_backtest_004_2_ultra_low.ipynb) |

## 1. O que foi testado
O mesmo walk-forward do 004.1 (128 combinações, 36 + 6 meses, 2013–2026) com os custos da conta **Micro Ultra Low**:

| | Standard (004.1) | Micro Ultra Low (004.2) |
|---|---|---|
| Símbolo | `EURUSD` | `EURUSDm#` |
| Spread mediano 10h–15h (2023+) | 17 pontos | **9 pontos** |
| Comissão | não tem | não tem |
| Contrato | 100.000 | 1.000 (micro lote) |

**Por que os preços do Standard:** o símbolo Ultra Low só tem barras completas desde meados de 2018. O bid dele é
sempre ~4 pontos acima do Standard (mesmo preço médio, correlação 1,00 nos retornos); uma diferença constante se anula
entre entrada e saída, então só o spread muda o resultado.

## 2. Resultados e conclusão
| | Standard | Ultra Low |
|---|---:|---:|
| Custo médio por operação | 0,085 R | **0,051 R** |
| Walk-forward | +0,020 R · FL 1,04 | +0,024 R · FL 1,04 |
| Regra clássica fixa | −0,012 R · FL 0,98 | **+0,019 R** · FL 1,04 |
| Escolha do 004 fixa | +0,017 R · FL 1,03 | **+0,054 R · FL 1,11** · DD −34% · Sharpe 0,39 |

### Critérios (walk-forward, Ultra Low)
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 1.052 | ✅ |
| Expectativa > 0 R | +0,024 | ✅ |
| Fator de lucro > 1,2 | 1,04 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,077 | ❌ |
| PBO < 0,5 | 0,13 | ✅ |
| Nenhum ano com DD > 20% | pior −20,5% (2019) | ❌ |
| ≥ 2 trades/semana e p90 ≤ 5 dias úteis | 1,5/sem · p90 8 | ❌ |

1. **O custo cai 40%** e as configurações fixas deixam de perder; a escolha do 004 é o melhor resultado do laboratório.
2. **O walk-forward quase não muda:** com custo menor, a otimização escolheu combinações de vantagem bruta menor.
3. **O problema de fundo continua:** 2019–2021 três anos seguidos negativos; drawdown do período acima de −50%.

**Veredito:** ❌ **reprovado.** Não é vantajoso o suficiente para conta real. Se for acompanhar, só em **conta demo**,
com a configuração fixa do 004: faixa 03h–10h, ordem stop 1 pip além, stop no lado oposto, sem alvo, a favor do H4.

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook |
| `parametros.json` | configuração exata (inclui a regra de spread) |
| `walkforward.csv` | combinação escolhida e resultado de cada janela |
| `metricas_oos.csv` | walk-forward × clássica fixa × escolha do 004 fixa |
| `criterios.csv` | os 7 critérios e o resultado |
| `operacoes_oos.csv` | operações fora da amostra |

## 4. Como reproduzir
- **Dados:** `dados/xm/EURUSDm/H1.parquet` (baixado do MT5, símbolo `EURUSDm#`).
- **Python:** `notebooks/11_backtest_004_2_ultra_low.ipynb` no VS Code (kernel `financeiro`).
- **PDF:** `python scripts/exportar_pdf.py 11_backtest_004_2_ultra_low`.
