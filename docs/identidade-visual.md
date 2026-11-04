# Identidade visual — LHS Quant Lab

Paleta oficial: **Terminal Âmbar** (escolhida em 18/10/2026). Marca: **LHS Quant Lab**, @lhsquantlab.

A fonte única das cores é [`estilo/paleta.json`](../estilo/paleta.json). Qualquer mudança começa lá.

## Logo

Escolhida em 19/10/2026: **touro geométrico** (herdado da LHS Capital) em âmbar `#E9A23B` sobre `#0E1726`, com "LHS" (Space Grotesk 700, `#F5F2EA`) e "QUANT LAB" (IBM Plex Mono, `#7FB3E6`). Slogan: **"Aprenda a testar e operar com dados"**. Kit completo em [`estilo/logo/`](../estilo/logo/README.md), gerado por `scripts/gerar_logo.py`.

## Cores — modo escuro (padrão)

Usado em: site, vídeos, Instagram, Telegram, slides, gráficos dos notebooks.

| Papel | Hex | Uso |
|---|---|---|
| Fundo | `#0E1726` | fundo de páginas, slides e gráficos |
| Superfície | `#16233A` | cartões, painéis, legendas |
| Borda | `#26374F` | linhas, grades, divisórias |
| Texto | `#F5F2EA` | títulos e texto principal |
| Texto suave | `#AEBBCD` | textos secundários, eixos, rodapés |
| **Primária (âmbar)** | `#E9A23B` | destaque da marca, botões, curva da estratégia |
| Texto sobre primária | `#0E1726` | texto em botões âmbar |
| Secundária (azul) | `#7FB3E6` | rótulos, links, segunda série dos gráficos |
| Positivo | `#5FCF9B` | selo **Aprovado**, ganhos |
| Negativo | `#F08A6C` | selo **Reprovado**, perdas |

Selos de veredito (texto sobre fundo):

| Selo | Texto | Fundo |
|---|---|---|
| Aprovado | `#5FCF9B` | `#173B33` |
| Reprovado | `#F08A6C` | `#3D2420` |
| Em teste | `#9CC4EC` | `#1C3350` |

## Cores — modo claro (apoio)

Usado em: PDFs, relatórios impressos, LinkedIn em formato documento. Mesma família, com âmbar e azul
escurecidos para ter contraste no fundo claro.

| Papel | Hex |
|---|---|
| Fundo | `#F5F2EA` |
| Superfície | `#FFFDF8` |
| Texto | `#0E1726` |
| Texto suave | `#4A5363` |
| Primária (âmbar escuro) | `#B87510` |
| Secundária (azul) | `#2F6FA8` |
| Positivo / Negativo | `#1F7A4D` / `#B4441C` |

## Fontes

| Uso | Fonte |
|---|---|
| Títulos | Space Grotesk (700) |
| Texto | IBM Plex Sans (400, 600) |
| Números, rótulos e código | IBM Plex Mono |

Todas gratuitas no Google Fonts.

## Regras

- O âmbar é o destaque: no máximo um elemento âmbar forte por tela (botão principal ou curva principal).
- Cor nunca fala sozinha: todo selo e número com cor também traz a palavra ("Reprovado", "−20,2%").
- Texto sobre âmbar sempre escuro (`#0E1726`), nunca branco.
- Em gráficos: estratégia = âmbar, buy & hold ou baseline = texto suave tracejado, segunda série = azul.

## Onde a paleta já está aplicada

| Lugar | Arquivo | Como usar |
|---|---|---|
| Notebooks / matplotlib | `src/lhsquant/estilo.py` | `from lhsquant.estilo import aplicar_estilo, CORES` + `aplicar_estilo()` |
| MT5 (indicadores e EAs) | `mql5/include/LHS_Cores.mqh` | `#include <LHSQuantLab\LHS_Cores.mqh>` + `LHS_PRIMARIA` etc. |
| Apresentação do negócio | `docs/apresentacao-negocio/` | já segue a paleta |
