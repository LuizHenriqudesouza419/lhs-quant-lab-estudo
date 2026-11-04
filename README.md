# LHS Quant Lab

> **Status:** projeto de estudo / teste — desenvolvimento pausado. Fica público como registro do meu aprendizado em backtesting, Python e MQL5.

Laboratório de backtests de forex: dados de vários pares, milhares de combinações de setups,
resultados versionados, geração de EAs/indicadores MQL5 e relatórios pelo Telegram.

> Só lê dados e testa. Não envia ordens.

**Foco inicial: day trading.** Os backtests usam por padrão os gráficos intradiários **H4, H1 e M15**
(o H4 também como filtro de tendência), com custos reais, filtro de sessão (Ásia/Londres/NY)
e opção de zerar a posição no fim do dia.

## Pastas

| Pasta | Conteúdo |
|---|---|
| `docs/` | documentos, guias e links (arquitetura, roadmap, identidade visual) |
| `estilo/` | paleta oficial Terminal Âmbar (`paleta.json`), fonte única das cores |
| `src/lhsquant/` | código do motor (dados, setups, backtest, métricas) |
| `setups/` | definição dos setups e grades de parâmetros (YAML) |
| `notebooks/` | notebooks de análise e os gerados por teste |
| `mql5/` | EAs e indicadores gerados para o MT5 |
| `app/` | interface web (Streamlit) — `app/diario/`: Diário de Trading ([guia](docs/diario-trading.md)) |
| `backtests/` | backtests concluídos: relatório, PDF, métricas, trades e EA de cada teste (versionado) |
| `resultados/` | banco e relatórios dos backtests (não versionado) |
| `dados/` | atalho para `C:\Dados\mercado` (não versionado) |
| `scripts/` | rotinas do agendador, coleta de dados, Telegram |

Ambiente: conda `financeiro` (Python 3.11).

## Telegram

1. No @BotFather: `/newbot` → copie o token para `.env` (`TELEGRAM_TOKEN=...`; modelo em `.env.example`).
2. Mande uma mensagem para o bot e rode `python scripts/configurar_telegram.py` (grava o `TELEGRAM_CHAT_ID` e envia um teste).
3. No código: `from lhsquant import notificar` → `enviar_texto()`, `enviar_imagem()`, `enviar_arquivo()`.
