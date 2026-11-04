"""Avisos de andamento no Telegram: início (com previsão), etapas, fim e erro.

    from lhsquant.avisos import tarefa

    with tarefa("Backtest 002 — IFR EURUSD M15") as t:
        ...
        t.etapa("H4 ok, rodando H1")
        ...
        t.concluir("PF 1,12 líquido · 214 trades", arquivo=pdf)

A previsão é a mediana das últimas durações da mesma tarefa (logs/duracoes.json).
Início e etapas chegam sem som; fim, erro e sinal, com som. Uma falha no Telegram
nunca derruba a tarefa (ver notificar.py).
"""
import json
import statistics
import traceback
from datetime import datetime, timedelta
from html import escape

from . import notificar

HISTORICO = notificar.RAIZ / "logs" / "duracoes.json"
SINAIS = notificar.RAIZ / "logs" / "sinais_enviados.json"
MAX_HISTORICO = 10  # durações guardadas por tarefa


def _ler(arquivo) -> dict:
    try:
        return json.loads(arquivo.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _gravar(arquivo, dados: dict):
    arquivo.parent.mkdir(exist_ok=True)
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


def duracao_fmt(segundos: float) -> str:
    h, resto = divmod(int(round(segundos)), 3600)
    m, s = divmod(resto, 60)
    if h:
        return f"{h}h{m:02d}min"
    return f"{m}min{s:02d}s" if m else f"{s}s"


def estimativa(chave: str) -> float | None:
    """Duração prevista (s) pela mediana das últimas execuções; None sem histórico."""
    duracoes = _ler(HISTORICO).get(chave)
    return statistics.median(duracoes) if duracoes else None


def _registrar(chave: str, segundos: float):
    hist = _ler(HISTORICO)
    hist[chave] = (hist.get(chave, []) + [round(segundos, 1)])[-MAX_HISTORICO:]
    _gravar(HISTORICO, hist)


class Tarefa:
    def __init__(self, nome: str, chave: str | None = None, avisar_inicio: bool = True):
        self.nome = nome
        self.chave = chave or nome  # mesma chave = mesma previsão (ex.: "backtest M15")
        self.avisar_inicio = avisar_inicio
        self._fim = ("", False, None, None)

    def decorrido(self) -> float:
        return (datetime.now() - self.inicio).total_seconds()

    def __enter__(self):
        self.inicio = datetime.now()
        if self.avisar_inicio:
            texto = f"🔵 Iniciado: {self.nome}\n⏱ {self.inicio:%H:%M}"
            prev = estimativa(self.chave)
            if prev:
                pronto = self.inicio + timedelta(seconds=prev)
                texto += f" · previsão ~{duracao_fmt(prev)} (pronto ~{pronto:%H:%M})"
            else:
                texto += " · sem histórico para prever a duração"
            notificar.enviar_texto(texto, silencioso=True)
        return self

    def etapa(self, texto: str):
        notificar.enviar_texto(f"🟡 {self.nome}: {texto} ({duracao_fmt(self.decorrido())})", silencioso=True)

    def concluir(self, texto: str = "", html: bool = False, arquivo=None, imagem=None):
        """Define o que vai na mensagem de fim (enviada ao sair do `with` sem erro)."""
        self._fim = (texto, html, arquivo, imagem)

    def __exit__(self, tipo, erro, tb):
        segundos = self.decorrido()
        if tipo is None:
            _registrar(self.chave, segundos)
            texto, html, arquivo, imagem = self._fim
            nome = escape(self.nome) if html else self.nome
            cabecalho = f"✅ Concluído: {nome} em {duracao_fmt(segundos)}"
            if notificar.enviar_texto(cabecalho + (f"\n\n{texto}" if texto else ""), html=html):
                if imagem:
                    notificar.enviar_imagem(imagem)
                if arquivo:
                    notificar.enviar_arquivo(arquivo)
        else:
            trecho = "".join(traceback.format_exception(tipo, erro, tb))[-1500:]
            notificar.enviar_texto(f"🔴 Falhou: {self.nome} após {duracao_fmt(segundos)}\n\n{trecho}")
        return False  # o erro continua subindo para quem chamou


def tarefa(nome: str, **kwargs) -> Tarefa:
    return Tarefa(nome, **kwargs)


def sinal(simbolo: str, timeframe: str, padrao: str, detalhes: str = "", imagem=None,
          bloqueio_horas: float = 4) -> bool:
    """Alerta de padrão achado por um robô. Só informativo: nunca envia ordem.

    O mesmo símbolo + timeframe + padrão não é repetido dentro de `bloqueio_horas`.
    """
    chave = f"{simbolo}|{timeframe}|{padrao}"
    enviados = _ler(SINAIS)
    agora = datetime.now()
    ultimo = enviados.get(chave)
    if ultimo and agora - datetime.fromisoformat(ultimo) < timedelta(hours=bloqueio_horas):
        return False
    texto = f"🎯 Sinal: {padrao}\n{simbolo} {timeframe} · {agora:%d/%m %H:%M}"
    if detalhes:
        texto += f"\n\n{detalhes}"
    texto += "\n\nInformativo, não é ordem."
    ok = notificar.enviar_imagem(imagem, texto) if imagem else notificar.enviar_texto(texto)
    if ok:
        enviados[chave] = agora.isoformat(timespec="seconds")
        _gravar(SINAIS, enviados)
    return ok
