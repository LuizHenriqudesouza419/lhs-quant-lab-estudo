"""Resumo de fim de dia no Telegram — todo dia às 23:50 (Brasília).

Rodar manualmente:  python scripts/resumo_do_dia.py [--data AAAA-MM-DD] [--teste]
Agendado pelo Windows (tarefa "LHS Quant Lab - Resumo do dia").

Monta a mensagem a partir de:
- registro do dia no Obsidian (01-LHS Quant Lab/LHS-Quant-Lab.md, linha "- **DD/MM/AAAA** — ...")
  com o "Para amanhã" logo abaixo;
- commits do dia nos repositórios da LHS Capital, agrupados pelo prefixo antes de ":";
- pendências: arquivos sem commit e commits não enviados ao GitHub (só avisa, não commita).

--teste imprime a mensagem sem enviar. Só envia uma vez por dia (logs/resumo_do_dia.log); --forcar repete.
"""
import argparse
import html
import re
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant import notificar  # noqa: E402

NOTA = Path.home() / "OneDrive" / "Documents" / "Obsidian Vault" / "01-LHS Quant Lab" / "LHS-Quant-Lab.md"
REPOS = {
    "lhs-quant-lab": RAIZ,
    "mql5-indicadores": RAIZ.parent / "mql5-indicadores",
    "exercicios-python": Path(r"C:\Dev\GitHub\exercicios-python"),
}
LOG = RAIZ / "logs" / "resumo_do_dia.log"


def git(repo: Path, *args) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return r.stdout.strip() if r.returncode == 0 else ""


def md_para_html(texto: str) -> str:
    """Markdown simples do Obsidian → HTML do Telegram (negrito, código, links internos)."""
    texto = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", texto)
    texto = re.sub(r"\[\[([^\]]+)\]\]", r"\1", texto)
    texto = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1", texto)
    texto = html.escape(texto, quote=False)
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def registro_obsidian(dia: date) -> tuple[str, list[str]]:
    """Texto do registro do dia e itens do 'Para amanhã' (vazios se não houver)."""
    if not NOTA.exists():
        return "", []
    linhas = NOTA.read_text(encoding="utf-8").splitlines()
    marca = f"- **{dia:%d/%m/%Y}** — "
    for i, linha in enumerate(linhas):
        if linha.startswith(marca):
            texto = linha[len(marca):]
            amanha = []
            for sub in linhas[i + 1:]:
                if not sub.startswith("  "):
                    break
                m = re.match(r"\s*- \*\*Para amanhã[^*]*\*\*\s*(.*)", sub)
                if m:
                    amanha = [p.strip(" ;.") for p in re.split(r"\(\d+\)", m.group(1)) if p.strip(" ;.")]
            return texto, amanha
    return "", []


def frases(texto: str) -> list[str]:
    """Quebra o registro em itens: cada '**Título:** ...' vira um item."""
    partes = re.split(r"(?=\*\*[^*]+:\*\*)|(?<=\.)\s+(?=\*\*)", texto)
    return [p.strip() for p in partes if p.strip()]


def commits_do_dia(dia: date) -> dict[str, list[str]]:
    inicio, fim = f"{dia} 00:00", f"{dia} 23:59:59"
    saida = {}
    for nome, repo in REPOS.items():
        if (repo / ".git").exists():
            log = git(repo, "log", "--all", f"--since={inicio}", f"--until={fim}", "--format=%s")
            if log:
                saida[nome] = log.splitlines()
    return saida


def pendencias() -> list[str]:
    avisos = []
    for nome, repo in REPOS.items():
        if not (repo / ".git").exists():
            continue
        sujos = git(repo, "status", "--porcelain")
        if sujos:
            avisos.append(f"{nome}: {len(sujos.splitlines())} arquivo(s) sem commit")
        frente = git(repo, "rev-list", "--count", "@{u}..HEAD")
        if frente and frente != "0":
            avisos.append(f"{nome}: {frente} commit(s) não enviados ao GitHub")
    return avisos


def montar(dia: date) -> str:
    texto, amanha = registro_obsidian(dia)
    commits = commits_do_dia(dia)
    total = sum(len(v) for v in commits.values())
    msg = [f"🌙 <b>Fim do dia — {dia:%d/%m/%Y}</b>", ""]

    if texto:
        msg += [f"• {md_para_html(f)}" for f in frases(texto)]
    elif commits:
        msg.append("<i>Sem registro no Obsidian hoje; pelo que foi commitado:</i>")
        for nome, lista in commits.items():
            grupos = Counter(s.split(":", 1)[0].strip() if ":" in s else s for s in lista)
            msg += [f"• <b>{html.escape(g)}</b>" + (f" ({n} commits)" if n > 1 else "") for g, n in grupos.items()]
    else:
        msg.append("Nenhum commit nem registro hoje.")

    if total:
        por_repo = " · ".join(f"{n} {r}" for r, n in ((r, len(v)) for r, v in commits.items()))
        msg += ["", f"📦 {total} commit(s): {html.escape(por_repo)}"]

    pend = pendencias()
    msg += ["", "⚠️ <b>Pendências</b>", *[f"• {html.escape(p)}" for p in pend]] if pend else ["", "✅ Tudo salvo e no GitHub."]

    if amanha:
        msg += ["", "🎯 <b>Para amanhã</b>", *[f"{i}. {md_para_html(a)}" for i, a in enumerate(amanha, 1)]]
    return "\n".join(msg)[: notificar.LIMITE_TEXTO]


def main():
    p = argparse.ArgumentParser(description="Resumo de fim de dia no Telegram")
    p.add_argument("--data", help="AAAA-MM-DD (padrão: hoje)")
    p.add_argument("--teste", action="store_true", help="só imprime, não envia")
    p.add_argument("--forcar", action="store_true", help="envia mesmo se já foi enviado nesse dia")
    a = p.parse_args()
    dia = date.fromisoformat(a.data) if a.data else date.today()
    msg = montar(dia)
    if a.teste:
        print(msg)
        return 0
    if not a.forcar and LOG.exists() and f"{dia} enviado" in LOG.read_text(encoding="utf-8"):
        print("já enviado hoje (use --forcar para mandar de novo)")
        return 0
    ok = notificar.enviar_texto(msg, html=True)
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{dia} {'enviado' if ok else 'FALHOU'} {datetime.now():%Y-%m-%d %H:%M}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
