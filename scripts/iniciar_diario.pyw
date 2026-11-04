"""Abre o Diário de Trading (atalho da Área de Trabalho).

Se o programa já estiver rodando, só abre o navegador; senão inicia o Streamlit
escondido (sem janela de console) e abre quando estiver pronto.
"""
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
APP = RAIZ / "app" / "diario"
PORTA = 8765
URL = f"http://localhost:{PORTA}"
LOG = RAIZ / "logs" / "diario_app.log"


def no_ar():
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", PORTA)) == 0


if not no_ar():
    LOG.parent.mkdir(exist_ok=True)
    python = Path(sys.executable).with_name("python.exe")  # pythonw não tem console para o Streamlit
    subprocess.Popen([str(python), "-m", "streamlit", "run", "app.py", "--server.port", str(PORTA)],
                     cwd=APP, stdout=open(LOG, "a", encoding="utf-8"), stderr=subprocess.STDOUT,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(120):  # até 60 s
        if no_ar():
            break
        time.sleep(0.5)
webbrowser.open(URL)
