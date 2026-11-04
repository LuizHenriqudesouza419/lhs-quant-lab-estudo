# Backtest 001.1 — SMA 20 × 50 + walk-forward + machine learning · EURUSD H4

| | |
|---|---|
| **Data** | 18/10/2026 |
| **Status** | 🟡 Promissor, ainda não aprovado: poucos trades e só um dos dois modelos confirma |
| **Base** | [Backtest 001](../001_sma20x50_EURUSD_H4/) (mesma regra, mesmos custos) |
| **Dados** | XM (MT5), EURUSD H4, 04/01/2010 → 16/10/2026; fora da amostra 2014 → 2026 |
| **Notebook de origem** | [`notebooks/03_backtest_001_1_walkforward_ml.ipynb`](../../notebooks/03_backtest_001_1_walkforward_ml.ipynb) |

## 1. O que foi testado
**Pergunta:** a regra reprovada no 001 melhora com **otimização walk-forward** ou com um **filtro de machine learning**?

- **Regra base:** SMA 20 acima da SMA 50 → comprado; abaixo → vendido; sinal na barra fechada (`shift(1)`).
- **Walk-forward:** a cada ano, escolhe entre 19 combinações de médias a de maior Sharpe líquido nos 4 anos anteriores
  (mínimo de 30 trades) e opera com ela só no ano seguinte.
- **Meta-labeling:** a regra base decide direção e momento; um modelo (regressão logística ou random forest rasa) prevê se
  cada cruzamento vai dar lucro líquido e a operação só é feita se a probabilidade for ≥ 0,50. Retreino anual, janela
  expansiva, treino só com operações já encerradas (*purging*).
- **Features:** ADX 14, ATR %, ATR14/ATR100, inclinação da SMA 50, momento de 20 barras, distância à SMA 200, nº de cruzamentos
  recentes e direção, todas da barra do sinal.

**Custos:** spread real de cada barra + 2 pontos de slippage por lado + comissão 0 (iguais ao 001). Seed 42.

## 2. Resultados (fora da amostra, 2014 → 2026)
| Versão | Retorno | Sharpe | Máx. DD | Trades | Win rate | Fator de lucro |
|---|---:|---:|---:|---:|---:|---:|
| Buy & hold | −18,6% | −0,17 | −31,6% | — | — | — |
| 20×50 fixo | −26,6% | −0,27 | −34,6% | 461 | 36,7% | 0,86 |
| Walk-forward | −1,5% | 0,02 | −22,7% | 228 | 35,1% | 1,02 |
| 20×50 + ML logística | **+16,8%** | **0,42** | **−5,8%** | 53 | 52,8% | 2,05 |
| 20×50 + ML random forest | +0,8% | 0,05 | −6,5% | 18 | 44,4% | 1,11 |

- **Walk-forward:** Sharpe médio de 0,30 no treino → 0,04 no teste (**WFE 0,14**). Bateu a 20×50 fixa em 9 de 13 anos,
  mas sem vantagem real. Escolheu médias lentas de 150–200 em 10 de 13 anos.
- **ML logística:** win rate de 53% nas aceitas contra 35% nas rejeitadas; **percentil 99** contra 300 filtros aleatórios
  com o mesmo nº de operações; percentil 85–99 em todos os limiares de 0,35 a 0,50. Porém o **AUC é 0,52**, só 53 trades
  (20 deles em 2014) e a random forest não confirma (percentil 71).
- A feature que mais separa vencedoras de perdedoras é a **distância à SMA 200, a favor da operação**.

## 3. Conclusão
O walk-forward **não salva** a regra. O filtro de ML com regressão logística mostra um sinal interessante, mas com poucos trades
e sem confirmação da random forest, ainda pode ser sorte. **Não vai para conta demo nem real.**

### Próximo passo
Testar a regra **sem ML**: 20×50 só a favor da SMA 200 (compra só acima, venda só abaixo). Depois validar em GBPUSD,
USDJPY e D1.

## 4. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook com todas as saídas |
| `parametros.json` | configuração exata (walk-forward, modelos, features, percentis) |
| `metricas.csv` | comparação final fora da amostra |
| `walkforward.csv` | combinação escolhida por ano, Sharpe de treino e de teste |
| `ml_operacoes_oos.csv` | cada operação fora da amostra com features, probabilidades e decisão do filtro |
| `ml_qualidade.csv` | AUC e acerto/expectativa das aceitas × rejeitadas |

## 5. Como reproduzir
- **Python:** abra `notebooks/03_backtest_001_1_walkforward_ml.ipynb` no VS Code (kernel `financeiro`) e rode tudo.
  A seção 3 confere se o motor reproduz o 001 (−20,2%, 586 trades).
- **PDF:** `python scripts/exportar_pdf.py 03_backtest_001_1_walkforward_ml`.
