# Backtest 001.2 — SMA 20 × 50 com saída Chandelier · EURUSD H4, H1 e M15

| | |
|---|---|
| **Data** | 18/10/2026 |
| **Status** | ❌ Reprovado: a saída reduz o prejuízo, mas não cria vantagem |
| **Base** | [Backtest 001.1](../001.1_sma_wf_ml_EURUSD_H4/) (mesma entrada, mesmo filtro de ML) |
| **Dados** | XM (MT5), EURUSD. H4 desde 2010, H1 desde set/2010, M15 desde out/2022 |
| **Notebook de origem** | [`notebooks/04_backtest_001_2_saida_chandelier.ipynb`](../../notebooks/04_backtest_001_2_saida_chandelier.ipynb) |

## 1. O que foi testado
**Pergunta:** trocar a saída por cruzamento contrário por um **trailing stop Chandelier** (maior máxima desde a entrada − K × ATR 14)
salva a regra 20×50? E em gráficos de day trade?

- **Entrada:** cruzamento SMA 20×50 na barra fechada, igual ao 001. Depois de sair, espera o próximo cruzamento.
- **Saída:** o que vier primeiro entre stop Chandelier, cruzamento contrário e fim do dia (H1/M15).
  O stop vale a partir da barra seguinte ao seu cálculo. Saída no preço do stop, ou na abertura se houver gap.
- **Day trade (H1/M15):** entrada só com a barra do sinal fechando entre 9h e 21h do servidor, e posição zerada às 23h e na última barra do dia.
- **Versões:** saída original · Chandelier K = 3 fixo · Chandelier com K por walk-forward (grade 2–5) · Chandelier WF + filtro de ML
  (logística, meta-labeling, retreino por janela).
- **Walk-forward:** H4/H1 com treino de 48 meses e teste de 12; M15 com treino de 12 meses e teste de 3.
- **Custos:** spread real de cada barra + 2 pontos de slippage por lado. Seed 42. O motor com k = 0 reproduz o 001 (−20,2%, 586 trades).

## 2. Resultados e conclusão
### O que encontramos (rodada de 18/10/2026, EURUSD, só fora da amostra)
| TF | Saída original | Chandelier 3×ATR | Chandelier WF | Chandelier WF + ML | Buy & hold |
|---|---:|---:|---:|---:|---:|
| **H4** (desde 2014) | −26,6% · Sharpe −0,27 | **−11,5% · −0,17** | −15,7% · −0,26 | +3,1% · 0,13 (87 trades) | −18,6% |
| **H1** (desde 2015) | −3,5% · −0,11 | −5,5% · −0,21 | −8,7% · −0,35 | +1,0% · 0,15 (63 trades) | −7,1% |
| **M15** (desde nov/2023) | −8,9% · −0,68 | −14,1% · −1,69 | −10,4% · −0,99 | −1,8% · −0,86 (38 trades) | +6,3% |

**1. O Chandelier ajudou só no H4, e não o suficiente.** Com K = 3, o prejuízo caiu de −26,6% para −11,5% e o drawdown
de −34,6% para −23,6%. É uma melhora real, mas a estratégia continua negativa e empata com o buy & hold.
No H1 e no M15 ele **piorou**: com a regra de zerar no fim do dia, a maioria das operações já termina às 23h, e o stop
só corta as que estavam dando certo.

**2. Otimizar o K não funcionou em nenhum timeframe.** O K escolhido no treino foi pior no teste (H4: Sharpe 0,12 → −0,43)
e o walk-forward ficou **abaixo** do K = 3 fixo nos três timeframes. Mais uma vez, otimizar parâmetros encontrou ruído.

**3. No intraday, o inimigo são os custos.** Sem custos, a saída original ganhava +11,0% no H1 e +7,2% no M15.
Líquido, ficou em −3,5% e −8,9%. São 777 e 841 operações pagando ~1,7 pip cada. O cruzamento 20×50 tem uma
vantagem bruta pequena demais para pagar o spread em gráficos curtos.

**4. O filtro de ML enfraqueceu.** No 001.1, o filtro ficou no percentil 99 contra filtros aleatórios. Aqui, sobre as operações
com Chandelier, ficou em 84 (H4), 82 (H1) e 14 (M15), sempre abaixo de 95, com AUC ≈ 0,53. Isso reforça a suspeita
de que parte do resultado do 001.1 foi sorte.

**Veredito:** ❌ **reprovado.** Uma saída melhor **reduz o prejuízo**, mas não cria vantagem onde a entrada não tem.
A entrada por cruzamento 20×50 está esgotada no EURUSD: já testamos parâmetros, walk-forward, ML e saída.

> Os números acima mudam conforme os dados forem atualizados. Ao rodar de novo, confira as tabelas.

### Lições para o day trade da LHS
- **Primeiro a entrada, depois a saída.** A saída só multiplica uma vantagem que a entrada já tenha.
- **No H1 e no M15, o setup precisa de alvo bruto grande em relação ao spread** (poucas operações por dia, movimentos de vários pips),
  ou o custo come tudo.
- **O próximo setup deve ser intradiário de origem**, pensado para a sessão, como o rompimento da faixa asiática na abertura de Londres,
  e não um setup de tendência adaptado para gráfico curto.

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook com todas as saídas |
| `parametros.json` | configuração exata (janelas de day trade, walk-forward, ML, AUC) |
| `metricas.csv` | todas as versões × timeframes, fora da amostra |
| `walkforward_k.csv` | K escolhido em cada janela, Sharpe de treino e de teste |
| `operacoes_oos.csv` | operações fora da amostra (Chandelier WF) com motivo de saída, features e probabilidade do ML |
| `ml_sensibilidade.csv` | filtro de ML por limiar: operações aceitas, retorno e percentil contra o acaso |
| `sensibilidade_k.csv` | Sharpe fora da amostra de cada K fixo |

## 4. Como reproduzir
- **Python:** abra `notebooks/04_backtest_001_2_saida_chandelier.ipynb` no VS Code (kernel `financeiro`) e rode tudo (~1 min).
- **PDF:** `python scripts/exportar_pdf.py 04_backtest_001_2_saida_chandelier`.
