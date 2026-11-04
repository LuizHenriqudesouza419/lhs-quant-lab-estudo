# Backtest 001 — Cruzamento SMA 20 × 50 · EURUSD H4

| | |
|---|---|
| **Data** | 17/10/2026 |
| **Status** | ❌ Reprovado: sem vantagem estatística |
| **Dados** | XM (MT5), EURUSD H4, 04/01/2010 → 16/10/2026 (26.119 barras) |
| **Notebook de origem** | [`notebooks/02_primeiro_backtest.ipynb`](../../notebooks/02_primeiro_backtest.ipynb) |

## 1. O que foi testado
**Pergunta:** seguir a tendência do EURUSD no H4 com cruzamento de médias móveis dá lucro depois dos custos?

**Estratégia (trend following, stop and reverse):**
- SMA 20 **acima** da SMA 50 → **comprado**; SMA 20 **abaixo** da SMA 50 → **vendido**.
- Sempre posicionado. A saída é o cruzamento contrário, sem stop nem alvo.
- Sinal calculado na barra **fechada** e executado na barra seguinte (sem look-ahead).

**Custos:** spread real de cada barra + 2 pontos de slippage por lado + comissão 0 (conta Standard XM).
Exposição de 1× o capital, sem alavancagem.

## 2. O que foi feito
1. Carregamento e checagem dos dados (sem datas duplicadas nem preços vazios; descartado o histórico antes de 2010, de qualidade duvidosa).
2. Cálculo das médias, do sinal e da posição com `shift(1)`.
3. Retornos líquidos de custos, curva de capital, drawdown e lista de operações.
4. Métricas completas, comparadas com o **buy & hold**.
5. Comparação com **300 estratégias de sinal aleatório**, com o mesmo nº de operações e custos (seed 42).
6. Divisão **in-sample** (2010–2019) × **out-of-sample** (2020–2026).
7. Sensibilidade dos parâmetros: grade de 19 combinações de médias, só no in-sample.
8. EA para o MT5 (`LHS_CruzamentoMM`) que replica a regra, para ver no Testador de Estratégia em modo visual.

## 3. Resultados
| Métrica | Estratégia (líquida) | Sem custos | Buy & hold |
|---|---:|---:|---:|
| Retorno total | −20,2% | −12,7% | −21,5% |
| CAGR | −1,34% | −0,80% | −1,43% |
| Máx. drawdown | −34,6% | −30,1% | −36,0% |
| Sharpe | −0,12 | −0,05 | −0,13 |
| Sortino | −0,17 | −0,08 | −0,18 |

| Operações | Valor |
|---|---:|
| Nº de trades | 586 |
| Win rate | 38,1% |
| Payoff | 1,52 |
| Expectativa por trade | −0,03% |
| Fator de lucro | 0,93 |

| Período | Retorno | Sharpe | Máx. DD | Trades |
|---|---:|---:|---:|---:|
| In-sample (2010–2019) | −5,9% | −0,02 | −21,2% | 331 |
| Out-of-sample (2020–2026) | −15,2% | −0,28 | −21,9% | 255 |

- **Contra o acaso:** a estratégia superou só **41%** das estratégias aleatórias, ou seja, não se distingue de sorte.
- **Sensibilidade:** só **3 de 19** combinações tiveram Sharpe positivo no in-sample. A melhor, 20×200, teve Sharpe de apenas 0,10. Não há região robusta.

## 4. Conclusão
O cruzamento simples de médias **não tem vantagem** no EURUSD H4 desde 2010. O payoff de 1,5 não compensa
o win rate de 38%, e os custos (~9% do capital ao longo do período) pioram o resultado. Foi negativo
tanto no in-sample quanto no out-of-sample. **Não deve ir para conta demo nem real.**

Lição principal: o histórico antigo (desde 1971) mostrava +498%. Ao usar só dados confiáveis, o resultado
virou −20%. **Qualidade dos dados vem antes de qualquer conclusão.**

### Próximas ideias
- Filtro de tendência/volatilidade (ADX, ATR) para evitar mercado lateral.
- Stop por ATR e alvo, em vez de ficar sempre posicionado.
- Testar outros pares (GBPUSD, USDJPY) e timeframes (D1).
- Walk-forward em vez de uma única divisão IS/OOS.

## 5. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código (textos, tabelas e gráficos) |
| `notebook_executado.ipynb` | cópia congelada do notebook com todas as saídas |
| `parametros.json` | configuração exata usada no teste |
| `metricas.csv` | métricas: período completo, IS, OOS e buy & hold |
| `trades.csv` | as 586 operações (entrada, saída, direção, barras, resultado) |
| `sensibilidade_sharpe_is.csv` | Sharpe in-sample de cada combinação de médias |
| `mql5/LHS_CruzamentoMM.mq5` | EA para o Testador de Estratégia (cópia da versão testada) |
| `mql5/LHS_DuasMedias.mq5` | indicador usado pela EA (SMA rápida azul, lenta vermelha) |

## 6. Como reproduzir
- **Python:** abra `notebooks/02_primeiro_backtest.ipynb` no VS Code (kernel `financeiro`) e rode tudo, com os parâmetros de `parametros.json`.
- **MT5 (visual):** no terminal da XM, Testador de Estratégia (Ctrl+R) → `LHSQuantLab\LHS_CruzamentoMM`, EURUSD, H4,
  2010.01.01 até hoje, depósito de 10.000 USD, com **Visualização** marcada.
  O resultado do MT5 deve ficar parecido, mas não idêntico, porque o MT5 cobra **swap** e executa no tick real.
- **PDF:** `python scripts/exportar_pdf.py 02_primeiro_backtest`.
