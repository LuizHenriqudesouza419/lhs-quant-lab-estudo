"""Envio de mensagens, imagens e arquivos para o Telegram.

Credenciais no arquivo `.env` da raiz do projeto (fora do git):

    TELEGRAM_TOKEN=123456:ABC...   # dado pelo @BotFather
    TELEGRAM_CHAT_ID=123456789     # preenchido por scripts/configurar_telegram.py

Se o `.env` não estiver preenchido, as funções só avisam e seguem em frente:
uma falha no Telegram nunca derruba a rotina que chamou.
"""
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ / ".env"
API = "https://api.telegram.org/bot{token}/{metodo}"
LIMITE_TEXTO = 4096  # máximo de caracteres por mensagem no Telegram


def _credenciais():
    load_dotenv(ARQUIVO_ENV, override=True)
    return os.getenv("TELEGRAM_TOKEN", "").strip(), os.getenv("TELEGRAM_CHAT_ID", "").strip()


def configurado() -> bool:
    token, chat_id = _credenciais()
    return bool(token and chat_id)


def chamar(metodo: str, dados: dict | None = None, arquivos: dict | None = None, token: str | None = None) -> dict:
    """Chama um método da Bot API e devolve o JSON. Levanta erro se falhar."""
    token = token or _credenciais()[0]
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN vazio no .env")
    r = requests.post(API.format(token=token, metodo=metodo), data=dados, files=arquivos, timeout=60)
    resposta = r.json()
    if not resposta.get("ok"):
        raise RuntimeError(f"Telegram recusou {metodo}: {resposta.get('description')}")
    return resposta


def _enviar(metodo: str, dados: dict, arquivos: dict | None = None) -> bool:
    token, chat_id = _credenciais()
    if not (token and chat_id):
        print("[telegram] não configurado — rode scripts/configurar_telegram.py")
        return False
    try:
        chamar(metodo, {"chat_id": chat_id, **dados}, arquivos, token)
        return True
    except Exception as e:
        print(f"[telegram] falha ao enviar: {e}")
        return False


def _som(silencioso: bool) -> dict:
    return {"disable_notification": "true"} if silencioso else {}


def enviar_texto(texto: str, html: bool = False, silencioso: bool = False) -> bool:
    """Manda texto; mensagens longas são quebradas em partes. `silencioso` chega sem som."""
    extra = {"parse_mode": "HTML"} if html else {}
    partes = [texto[i:i + LIMITE_TEXTO] for i in range(0, len(texto), LIMITE_TEXTO)] or [""]
    return all(_enviar("sendMessage", {"text": p, **extra, **_som(silencioso)}) for p in partes)


def enviar_imagem(caminho, legenda: str = "", silencioso: bool = False) -> bool:
    """Manda PNG/JPG (gráficos de backtest, por exemplo)."""
    with open(caminho, "rb") as f:
        return _enviar("sendPhoto", {"caption": legenda[:1024], **_som(silencioso)}, {"photo": f})


def enviar_arquivo(caminho, legenda: str = "", silencioso: bool = False) -> bool:
    """Manda qualquer arquivo até 50 MB (PDF, HTML, CSV...)."""
    with open(caminho, "rb") as f:
        return _enviar("sendDocument", {"caption": legenda[:1024], **_som(silencioso)},
                       {"document": (Path(caminho).name, f)})
