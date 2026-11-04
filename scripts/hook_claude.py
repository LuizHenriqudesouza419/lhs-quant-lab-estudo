"""Hooks do Claude Code -> Telegram (configurados em ~/.claude/settings.json).

    hook_claude.py prompt        # UserPromptSubmit: marca a hora do pedido
    hook_claude.py fim           # Stop: avisa se a resposta levou >= 3 min
    hook_claude.py notificacao   # Notification (permission_prompt): Claude esperando aprovação

Lê o JSON do hook pela entrada padrão. Nunca falha: um erro aqui não pode
atrapalhar a sessão do Claude.
"""
import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

PASTA = RAIZ / "logs" / "claude_sessoes"
MINIMO = 180  # segundos: respostas mais curtas não geram aviso
LIMITE_RESUMO = 800


def ultima_resposta(d: dict) -> str:
    """Último texto do Claude na conversa (campo do hook ou, se faltar, o transcript)."""
    if d.get("last_assistant_message"):
        return d["last_assistant_message"]
    try:
        linhas = Path(d["transcript_path"]).read_text(encoding="utf-8").splitlines()
    except (KeyError, OSError):
        return ""
    for linha in reversed(linhas):
        try:
            item = json.loads(linha)
        except ValueError:
            continue
        if item.get("type") != "assistant":
            continue
        conteudo = item.get("message", {}).get("content", [])
        textos = [c.get("text", "") for c in conteudo if isinstance(c, dict) and c.get("type") == "text"]
        if any(textos):
            return "\n".join(textos).strip()
    return ""


def main():
    evento = sys.argv[1] if len(sys.argv) > 1 else ""
    d = json.loads(sys.stdin.buffer.read().decode("utf-8") or "{}")
    marca = PASTA / f"{d.get('session_id', 'sem-sessao')}.txt"
    projeto = Path(d.get("cwd", "")).name or "?"

    if evento == "prompt":
        PASTA.mkdir(parents=True, exist_ok=True)
        marca.write_text(str(time.time()), encoding="utf-8")
        return

    from lhsquant import notificar  # só carrega quando vai mandar algo
    from lhsquant.avisos import duracao_fmt

    if evento == "fim" and marca.exists():
        segundos = time.time() - float(marca.read_text(encoding="utf-8"))
        marca.unlink()
        if segundos >= MINIMO:
            resumo = ultima_resposta(d)
            if len(resumo) > LIMITE_RESUMO:
                resumo = resumo[:LIMITE_RESUMO].rstrip() + "…"
            notificar.enviar_texto(f"✅ Claude terminou em {duracao_fmt(segundos)} · {projeto}\n\n{resumo}")
    elif evento == "notificacao":
        notificar.enviar_texto(f"⏸ Claude esperando sua aprovação · {projeto}\n{d.get('message', '')}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
