# Documentos da LHS Quant Lab

Dois tipos, cada um na sua pasta:

## `publicos/` — pode divulgar
Material educativo para o site, Instagram, Telegram e alunos. Nada de dados pessoais, contas ou números internos.

| Documento | Assunto | Fonte (HTML) |
|---|---|---|
| [Criterios-de-Aprovacao-de-Backtest.pdf](publicos/Criterios-de-Aprovacao-de-Backtest.pdf) | Os 7 critérios que um backtest precisa passar | `publicos/fonte/criterios-backtest.html` |
| [Forex-no-Brasil.pdf](publicos/Forex-no-Brasil.pdf) | Operar forex a partir do Brasil: legalidade, câmbio, impostos e ressalvas | `publicos/fonte/forex-no-brasil.html` |

## `privados/` — só do Luiz
Estudo pessoal, planos e estratégia do negócio. **Não publicar.** Fica no GitHub junto com o resto (o repositório é privado).

| Documento | Assunto |
|---|---|
| [Guia-Claude-Jupyter-Forex.pdf](privados/Guia-Claude-Jupyter-Forex.pdf) | Plano de estudo pessoal: Claude + Jupyter para forex |
| [LHS-Capital-Plano-de-Negocio.pdf](privados/LHS-Capital-Plano-de-Negocio.pdf) | Plano de negócio (fonte em `docs/apresentacao-negocio/`) |
| [Pesquisa-de-Mercado-Monetizacao.pdf](privados/Pesquisa-de-Mercado-Monetizacao.pdf) | Como ganhar dinheiro sem prometer setup: Google Trends, produtos e preços, regras (CVM), afiliados, referências no Brasil, plano de 90 dias (fonte e dados do Trends em `privados/fonte/`) |
| [Pre-Mercado-O-Que-Os-Traders-Olham.pdf](privados/Pre-Mercado-O-Que-Os-Traders-Olham.pdf) | O que day traders olham antes de operar (Al Brooks, Felippe Aranha, BabyPips, relatórios matinais) e comparação com o nosso pré-mercado (fonte `privados/fonte/pre-mercado-o-que-os-traders-olham.html`) |

## Documento novo
1. Decidir: **público** (educativo, divulgável) ou **privado** (pessoal, estratégico).
2. HTML na paleta Terminal Âmbar em `<tipo>/fonte/<nome>.html`.
3. PDF com o Edge:
   `msedge.exe --headless --disable-gpu --no-pdf-header-footer --print-to-pdf="<pasta>\<Nome>.pdf" "file:///<caminho do html>"`
4. Linha nova na tabela acima e cópia no Obsidian `01-LHS Quant Lab/Documentos/<Publicos|Privados>/`.
