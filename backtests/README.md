# Backtests

Cada backtest tem uma pasta própria, `ID_setup_SIMBOLO_TF`, com relatório (`README.md`), PDF,
notebook executado, parâmetros, métricas, trades e o EA da versão testada.

| ID | Setup | Par / TF | Período | Trades | Sharpe | Máx. DD | Status |
|---|---|---|---|---:|---:|---:|---|
| [001](001_sma20x50_EURUSD_H4/) | Cruzamento SMA 20×50 | EURUSD H4 | 2010–2026 | 586 | −0,12 | −34,6% | ❌ reprovado |
| [001.1](001.1_sma_wf_ml_EURUSD_H4/) | 20×50 + walk-forward + filtro ML (logística) | EURUSD H4 | OOS 2014–2026 | 53 | 0,42 | −5,8% | 🟡 promissor, não aprovado |
| [001.2](001.2_sma_chandelier_EURUSD_H4-H1-M15/) | 20×50 + saída Chandelier (+ ML) | EURUSD H4/H1/M15 | OOS 2014/2015/2023–2026 | 461 (H4) | −0,17 (H4, K=3) | −23,6% | ❌ reprovado |
| [002](002_pullback_ema_EURUSD_H4-H1-M15/) | Pullback na EMA 20/50 do M15 com H4 + H1 a favor | EURUSD H4/H1/M15 | OOS nov/2023–2026 | 86 | −2,26 | −35,4% | ❌ reprovado |
| [002.1](002.1_pullback_saida_freq_EURUSD_H4-H1-M15/) | 002 + saídas curtas/zero a zero + mais sinais | EURUSD H4/H1/M15 | OOS nov/2023–2026 | 856 | −3,17 | −87,4% | ❌ reprovado |
| [003](003_bollinger_lateral_EURUSD_H4-H1-M15/) | Bollinger 21 em mercado lateral (média de 200), volta à média | EURUSD H4/H1/M15 | OOS 2021/2025–2026 | 36 (H4) | 0,23 (H4) | −4,7% | ❌ reprovado |
| [003.1](003.1_bollinger_swap_EURUSD_H4-H1/) | 003 segurando a posição, com swap real + ADX | EURUSD H4/H1 | OOS 2021–2026 | 517 (H1) | −0,32 (H1) | −20,5% | ❌ reprovado |
| [004](004_rompimento_asia_EURUSD_M15-H1/) | Rompimento da faixa asiática na abertura de Londres | EURUSD M15/H1 (filtro H4) | OOS 2021–2026 (H1) | 608 (H1) | 0,27 (H1) | −24,1% | ❌ reprovado por pouco (5/6) |
| [004.1](004.1_rompimento_asia_wf_EURUSD_H1/) | 004 com walk-forward 36+6 meses + PBO | EURUSD H1 | OOS 2013–2026 | 1.069 | 0,14 | −48,4% | ❌ reprovado (5/7) |
| [004.2](004.2_rompimento_asia_ultralow_EURUSD_H1/) | 004.1 com custos da conta Micro Ultra Low | EURUSD H1 | OOS 2013–2026 | 1.052 | 0,16 | −52,7% | ❌ reprovado (3/7) |
