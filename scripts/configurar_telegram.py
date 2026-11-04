"""Configura o bot do Telegram do LHS Quant Lab.

1. Crie o bot no @BotFather (/newbot) e cole o token no .env:  TELEGRAM_TOKEN=...
2. Mande qualquer mensagem para o seu bot no Telegram.
3. Rode:  python scripts/configurar_telegram.py

O script descobre o seu chat_id, grava no .env e manda uma mensagem de teste.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from lhsquant import notificar  # noqa: E402

MODELO_ENV = "# segredos do LHS Quant Lab — nunca versionar\nTELEGRAM_TOKEN=\nTELEGRAM_CHAT_ID=\n"


def gravar_env(chave: str, valor: str):
    linhas = notificar.ARQUIVO_ENV.read_text(encoding="utf-8").splitlines()
    linhas = [l for l in linhas if not l.startswith(f"{chave}=")] + [f"{chave}={valor}"]
    notificar.ARQUIVO_ENV.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main():
    if not notificar.ARQUIVO_ENV.exists():
        notificar.ARQUIVO_ENV.write_text(MODELO_ENV, encoding="utf-8")
    token, chat_id = notificar._credenciais()
    if not token:
        print(f"Cole o token do @BotFather em {notificar.ARQUIVO_ENV} (TELEGRAM_TOKEN=...) e rode de novo.")
        return 1

    bot = notificar.chamar("getMe", token=token)["result"]
    print(f"Bot encontrado: @{bot['username']}")

    if not chat_id:
        updates = notificar.chamar("getUpdates", token=token)["result"]
        chats = [u["message"]["chat"] for u in updates if "message" in u]
        if not chats:
            print(f"Nenhuma mensagem recebida. Mande um 'oi' para @{bot['username']} e rode de novo.")
            return 1
        chat = chats[-1]
        chat_id = str(chat["id"])
        gravar_env("TELEGRAM_CHAT_ID", chat_id)
        print(f"chat_id gravado no .env: {chat_id} ({chat.get('first_name') or chat.get('title')})")

    ok = notificar.enviar_texto("✅ LHS Quant Lab conectado. Os relatórios vão chegar aqui.")
    print("Mensagem de teste enviada." if ok else "Falha ao enviar a mensagem de teste.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
