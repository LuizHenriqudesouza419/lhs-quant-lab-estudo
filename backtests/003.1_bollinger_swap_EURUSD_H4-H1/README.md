# Backtest 003.1 — Bollinger lateral segurando a posição, com swap · EURUSD H4 e H1

| | |
|---|---|
| **Data** | 20/10/2026 |
| **Status** | ❌ Reprovado (2/5 critérios eliminatórios): o swap pesa pouco (−0,01 R), mas a pista do 003 não se confirma no treino e a otimização escolhe ruído |
| **Base** | [Backtest 003](../003_bollinger_lateral_EURUSD_H4-H1-M15/) |
| **Dados** | XM (MT5), EURUSD H4 e H1 desde 2010; swap real da XM (compra −7,48 / venda +1,23 pontos por noite, triplo na quarta) |
| **Notebook de origem** | [`notebooks/08_backtest_003_1_bollinger_swap.ipynb`](../../notebooks/08_backtest_003_1_bollinger_swap.ipynb) |

## 1. O que foi testado
Correção do 003: no H1, zerar no fim do dia cortava as operações antes do alvo, e o H4 segurava posição **sem pagar
swap**. Agora a posição pode ficar aberta até o meio da banda ou o stop, **pagando o swap real** por noite.

- Grade de 60 combinações por tempo gráfico: gatilho × 5 réguas de lateralidade (sem filtro, inclinação da média de
  200 com *k* 1,0/0,5/0,25, **ADX < 20**) × 3 stops × segurar/zerar.
- Escolha só no treino (2010–2020); fora da amostra 2021–2026; teste do acaso com o mesmo swap.
- **Decidido antes:** segurar a posição é swing, então a frequência de day trade é informativa (não elimina).
- **Limitação:** swap de hoje aplicado a todo o histórico; a seção 8 do notebook testa swap em dobro e o cenário conservador.

## 2. Resultados e conclusão
### A pista do 003 (H4, voltou para dentro, sem filtro, stop 1,5 ATR, segurando)
| | Treino 2010–2020 | Fora 2021–2026 |
|---|---:|---:|
| Operações | 366 | 200 |
| Expectativa sem swap | +0,013 R | +0,090 R |
| Swap médio | −0,008 R | −0,011 R |
| **Expectativa com swap** | **+0,005 R** | **+0,079 R** |
| Fator de lucro | 1,01 | 1,18 |

### Critérios (melhor fora da amostra: H1, voltou para dentro, *k* 0,5, stop 3 ATR, zerando)
| Critério | Valor | |
|---|---|---|
| ≥ 100 operações fora da amostra | 517 | ✅ |
| Expectativa > 0 R (com swap) | −0,019 | ❌ |
| Fator de lucro > 1,2 | 0,92 | ❌ |
| Melhor que aleatório (p < 0,05) | p = 0,093 | ❌ |
| Nenhum ano com DD > 20% | pior −9,6% | ✅ |
| Frequência de day trade (informativo) | 1,7/sem | ❌ |

1. **O swap não era o problema:** cerca de −0,01 R por operação; nem em dobro muda o sinal do resultado.
2. **A pista do 003 não se sustenta:** positiva fora da amostra, mas praticamente zero em 11 anos de treino.
3. **A otimização enganou:** no H4, a campeã do treino (ADX < 20, +0,08 R) foi a pior fora (−0,11 R, p = 0,99).
4. **No H1, segurar ajuda mas não cria vantagem:** a regra padrão vai de −0,03 R para +0,003 R.
5. **Família Bollinger encerrada:** mais de 100 combinações em 003 + 003.1, sem vantagem consistente depois dos custos.

**Veredito:** ❌ **reprovado.**

## 3. Arquivos desta pasta
| Arquivo | Conteúdo |
|---|---|
| `README.md` | este relatório |
| `relatorio.pdf` | notebook completo em PDF, sem código |
| `notebook_executado.ipynb` | cópia congelada do notebook |
| `parametros.json` | configuração exata (inclui o swap usado) |
| `metricas_pista.csv` | pista do 003 e regra padrão segurando, com e sem swap |
| `metricas_oos.csv` | melhor do treino, fora da amostra |
| `grade_otimizacao.csv` | as 60 combinações por tempo gráfico |
| `sensibilidade_swap.csv` | sem swap, swap de hoje, em dobro e conservador |
| `criterios.csv` | critérios e resultado |
| `operacoes_oos.csv` | operações fora da amostra (com noites e swap em R) |

## 4. Como reproduzir
- **Python:** `notebooks/08_backtest_003_1_bollinger_swap.ipynb` no VS Code (kernel `financeiro`).
- **PDF:** `python scripts/exportar_pdf.py 08_backtest_003_1_bollinger_swap`.
