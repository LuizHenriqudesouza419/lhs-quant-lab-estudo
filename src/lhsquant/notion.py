"""Envio de relatórios para o Notion, uma subpágina por relatório.

Credenciais no arquivo `.env` da raiz do projeto (fora do git):

    NOTION_TOKEN=ntn_...                                # integração interna (notion.so/profile/integrations)
    NOTION_PAGINA_PREMERCADO=3bdffbfd0af9804da835de4b36e0d523   # "Relatórios de Mercado"
    NOTION_PAGINA_BACKTESTS=400ffbfd0af98193bea2e2fbf3299cf7    # "Relatórios de Backtest"

A integração precisa estar conectada às duas páginas (… → Conexões → adicionar a integração).
Se o `.env` não estiver preenchido, só avisa e segue: uma falha no Notion nunca
derruba a rotina que chamou.
"""
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ / ".env"
API = "https://api.notion.com/v1"
VERSAO = "2022-06-28"
LIMITE_TEXTO = 2000  # máximo de caracteres por trecho de rich_text
INLINE = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\)")


def _env(nome: str) -> str:
    load_dotenv(ARQUIVO_ENV, override=True)
    return os.getenv(nome, "").strip()


def configurado(pagina: str = "NOTION_PAGINA_PREMERCADO") -> bool:
    return bool(_env("NOTION_TOKEN") and _env(pagina))


def _chamar(metodo: str, caminho: str, corpo: dict | None = None) -> dict:
    r = requests.request(metodo, f"{API}/{caminho}", json=corpo, timeout=60,
                         headers={"Authorization": f"Bearer {_env('NOTION_TOKEN')}", "Notion-Version": VERSAO})
    if not r.ok:
        raise RuntimeError(f"Notion {r.status_code}: {r.text[:300]}")
    return r.json()


def _trecho(conteudo: str, **extra) -> list:
    return [{"type": "text", "text": {"content": conteudo[i:i + LIMITE_TEXTO], **extra.get("text", {})},
             **({"annotations": extra["annotations"]} if "annotations" in extra else {})}
            for i in range(0, len(conteudo), LIMITE_TEXTO)]


def _texto(s: str) -> list:
    """Converte **negrito**, *itálico*, `código` e [links](url) em rich_text do Notion."""
    partes, pos = [], 0
    for m in INLINE.finditer(s):
        partes += _trecho(s[pos:m.start()]) if m.start() > pos else []
        negrito, italico, codigo, rotulo, url = m.groups()
        if rotulo:  # link relativo (arquivo do repo) não existe no Notion: fica só o texto
            partes += _trecho(rotulo, text={"link": {"url": url}}) if url.startswith("http") else _texto(rotulo)
        else:
            partes += _trecho(negrito or italico or codigo, annotations={
                "bold": bool(negrito), "italic": bool(italico), "code": bool(codigo)})
        pos = m.end()
    return partes + (_trecho(s[pos:]) if pos < len(s) else [])


def _bloco(tipo: str, s: str) -> dict:
    return {"type": tipo, tipo: {"rich_text": _texto(s)}}


def _tabela(linhas: list) -> dict:
    celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas
               if not re.fullmatch(r"\|[\s\-|:]+\|", l.strip())]
    largura = len(celulas[0])
    return {"type": "table", "table": {
        "table_width": largura, "has_column_header": True, "has_row_header": False,
        "children": [{"type": "table_row", "table_row": {
            "cells": [_texto(c) for c in (linha + [""] * largura)[:largura]]}} for linha in celulas]}}


def markdown_para_blocos(md: str) -> list:
    """Conversor simples para os relatórios (títulos, listas, citações, tabelas, parágrafos)."""
    blocos, tabela = [], []
    linhas = md.splitlines()
    if linhas and linhas[0].startswith("# "):  # o título vira o nome da página
        linhas = linhas[1:]
    for linha in linhas:
        if linha.startswith("|"):
            tabela.append(linha)
            continue
        if tabela:
            blocos.append(_tabela(tabela))
            tabela = []
        s = linha.strip()
        if not s:
            continue
        if s.startswith("### "):
            blocos.append(_bloco("heading_3", s[4:]))
        elif s.startswith("## "):
            blocos.append(_bloco("heading_2", s[3:]))
        elif s.startswith("# "):
            blocos.append(_bloco("heading_1", s[2:]))
        elif s.startswith("- "):
            blocos.append(_bloco("bulleted_list_item", s[2:]))
        elif re.match(r"\d+\. ", s):
            blocos.append(_bloco("numbered_list_item", s.split(" ", 1)[1]))
        elif s.startswith("> "):
            blocos.append(_bloco("quote", s[2:]))
        else:
            blocos.append(_bloco("paragraph", s))
    if tabela:
        blocos.append(_tabela(tabela))
    return blocos


def _titulo_filho(bloco: dict) -> str:
    return bloco["child_page"]["title"] if bloco["type"] == "child_page" else ""


def substituir_pagina(pai_env: str, titulo: str, md: str, icone: str) -> str:
    """Cria a subpágina `titulo` dentro da página-pai; uma subpágina com o mesmo título vai para a lixeira."""
    pai, cursor = _env(pai_env), None
    while True:  # percorre as subpáginas existentes (100 por chamada)
        r = _chamar("GET", f"blocks/{pai}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else ""))
        for b in r["results"]:
            if _titulo_filho(b) == titulo:
                _chamar("PATCH", f"pages/{b['id']}", {"archived": True})
        if not r.get("has_more"):
            break
        cursor = r["next_cursor"]
    blocos = markdown_para_blocos(md)
    pagina = _chamar("POST", "pages", {"parent": {"page_id": pai}, "icon": {"emoji": icone},
                                       "properties": {"title": {"title": _texto(titulo)}},
                                       "children": blocos[:100]})
    for i in range(100, len(blocos), 100):  # a API aceita até 100 blocos por chamada
        _chamar("PATCH", f"blocks/{pagina['id']}/children", {"children": blocos[i:i + 100]})
    return pagina["url"]


def enviar_premercado(a: dict, md: str) -> str | None:
    """Cria (ou substitui) a página do dia em "Relatórios de Mercado". Devolve a URL, ou None se não configurado/falhar."""
    if not configurado("NOTION_PAGINA_PREMERCADO"):
        print("[notion] não configurado — preencha NOTION_TOKEN no .env")
        return None
    try:
        icone = {"ALTA": "🟢", "BAIXA": "🔴", "NEUTRO": "🟡"}[a["vies"]]
        # mesmo título = nova versão do dia: a anterior vai para a lixeira
        return substituir_pagina("NOTION_PAGINA_PREMERCADO", f"Pré-mercado EURUSD — {a['gerado']:%d/%m/%Y}", md, icone)
    except Exception as e:
        print(f"[notion] falhou: {e!r}")
        return None


def enviar_backtest(id_: str, setup: str, status: str, md: str) -> str:
    """Cria (ou substitui) a página de um backtest em "Relatórios de Backtest"."""
    icone = {"reprovado": "❌", "promissor": "🟡", "aprovado": "✅"}[status]
    return substituir_pagina("NOTION_PAGINA_BACKTESTS", f"{id_} — {setup}", md, icone)
