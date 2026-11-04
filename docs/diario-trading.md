# Diário de Trading

Definido e construído em 21/10/2026. Sistema local de histórico de operações forex da XM, com diário de trading
e métricas por setup, ativo, horário, sessão e emoção. **Só lê a conta: não envia ordens.**

## Como usar

- **Abrir:** atalho **Diário de Trading LHS** na Área de Trabalho (roda `scripts/iniciar_diario.pyw`:
  sobe o painel escondido em http://localhost:8765 e abre o navegador). Fechar pelo botão
  "Fechar programa" na barra lateral.
- **Importar:** deixe o MT5 aberto na conta desejada e clique em Sincronizar. Real e demo ficam separadas;
  para importar a outra conta, troque o login no terminal e sincronize de novo.
- **Rotina diária:** tarefa "LHS Quant Lab - Importar trades" (seg–sex 19:00) importa a conta logada e manda
  o resumo do dia no Telegram, com alerta se um setup cair abaixo da faixa do backtest.
- **Setups:** cadastrar em `setups/diario.yaml` (nome, magic do EA e pasta do backtest).

## Decisões

| Tema | Decisão |
|---|---|
| Contas | Real (`XMGlobal-MT5 15`) e demo (`MetaQuotes-Demo`), importadas separadas e com filtro em todas as telas |
| Setup do trade | Automático pelo magic number do EA (`setups/magic.yaml`), manual no painel para trades discricionários |
| Interface | Streamlit local em `app/diario/` |
| Importação | Botão "Sincronizar" no painel e tarefa diária no Agendador do Windows |
| Medida | Dinheiro (líquido de comissão e swap) e múltiplo de R (risco do SL inicial) |
| Diário | Motivo da entrada, seguiu o plano (s/n), nota de execução de 1 a 5, emoções (tags), erros (tags), lição e resumo do dia |
| Gráfico do trade | Gerado com os candles da XM (banco Parquet): entrada, saída, SL e TP. Sem print |
| Real × backtest | Compara cada setup ao vivo com o resultado do backtest em `backtests/` e avisa se sair da faixa |

## Estrutura

```
src/lhsquant/diario/
  horario.py        # servidor XM (GMT+2/+3) -> Brasília e sessões
  importar_mt5.py   # history_deals_get/history_orders_get -> trades por position_id
  banco.py          # SQLite em C:\Dados\mercado\diario.db (fora do git)
  metricas.py       # R, expectativa, payoff, win rate, PF, max DD, Sharpe/Sortino, cortes
  grafico_trade.py  # candles + marcações de entrada/saída/SL/TP (plotly)
  comparar_bt.py    # real × backtest por setup
app/diario/         # painel Streamlit (app.py, comum.py, paginas/, .streamlit/config.toml)
setups/diario.yaml  # setups: magic do EA e backtest ligado
scripts/importar_trades.py   # rotina da tarefa diária
scripts/iniciar_diario.pyw   # lançador do atalho
```

## Banco (SQLite)

Arquivo: `dados/diario.db` (= `C:\Dados\mercado\diario.db`). Candles dos gráficos em cache em `dados/diario/candles/`.

- `trades`: conta, tipo de conta (real/demo), ativo, lado, lote, entrada e saída (preço e hora, servidor e Brasília),
  SL/TP iniciais, lucro bruto, comissão, swap, líquido, R, setup, magic, comentário.
- `diario`: id do trade, motivo, seguiu_plano, nota, emoções, erros, lição.
- `resumo_dia`: data, conta, texto livre.

## Painel

1. **Sincronizar**: mostra qual conta está logada no MT5, importa e lista os trades sem setup para marcar.
2. **Diário**: um trade por vez, com o gráfico e o formulário de anotação.
3. **Métricas**: por setup, ativo, hora × dia da semana (Brasília), sessão Ásia/Londres/NY, emoção e erro, em $ e em R.
4. **Real × Backtest**: expectativa, win rate e DD ao vivo contra o esperado pelo backtest.

## Regras técnicas

- R exige o SL inicial. Na XM a ordem de abertura costuma vir com SL = 0 (stop colocado depois), então o importador
  usa: SL da ordem → senão o preço do comentário de saída `[sl ...]` → senão vazio. Stop movido para o lucro não conta
  como risco. O SL pode ser corrigido no Diário; o R é recalculado na hora.
- O servidor da XM roda em GMT+2/+3: tudo é convertido para Brasília antes dos cortes por hora.
- Fechamentos parciais viram um único trade, com preço médio de saída.
- Toda métrica mostra o nº de trades e avisa quando houver menos de 30.

## Identidade visual (Terminal Âmbar)

Fonte única: [`estilo/paleta.json`](../estilo/paleta.json). Regras em [`identidade-visual.md`](identidade-visual.md).

- **Tema escuro como padrão**: `app/.streamlit/config.toml` com fundo `#0E1726`, superfície `#16233A`,
  texto `#F5F2EA` e primária `#E9A23B`. Fontes Space Grotesk (títulos), IBM Plex Sans (texto) e
  IBM Plex Mono (números e tabelas), via CSS do Google Fonts.
- **Plotly**: novo `aplicar_estilo_plotly()` em `src/lhsquant/estilo.py`, que lê o mesmo `paleta.json`
  (template com grade `#26374F`, eixos `#AEBBCD`, legenda sobre superfície).
- **Gráfico do trade**: candle de alta `#5FCF9B`, de baixa `#F08A6C`, entrada âmbar, saída azul `#7FB3E6`,
  SL negativo tracejado e TP positivo tracejado.
- **Curva de capital**: estratégia/real em âmbar, backtest esperado em texto suave tracejado.
- **Selos**: dentro do esperado = Aprovado (`#5FCF9B` sobre `#173B33`), fora = Reprovado
  (`#F08A6C` sobre `#3D2420`), poucos trades = Em teste (`#9CC4EC` sobre `#1C3350`). Sempre com a palavra escrita.
- **Números**: ganho em positivo, perda em negativo, sempre com sinal ("+1,8R", "−42,10 $").
- **Um âmbar forte por tela**: o botão principal (Sincronizar / Salvar anotação).
- Logo `estilo/logo/site/logo-horizontal.svg` no topo da barra lateral e `favicon-32.png` como ícone da aba.
- Relatórios em PDF usam o modo claro (`aplicar_estilo("claro")`).

## Status

Fases 1–4 prontas em 21/10/2026: importação, diário com gráfico, métricas e cortes, Real × Backtest,
tarefa diária com resumo no Telegram e atalho na Área de Trabalho.
