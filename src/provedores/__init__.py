"""Infraestrutura comum aos provedores de LLM: parada global e controle de ritmo.

Cada provedor (gemini.py, openai_api.py, anthropic_api.py, teste.py) expõe:
    criar_cliente(cfg)                         -> cliente
    chamar(cliente, conversa, exercicio, cfg)  -> texto da resposta

`conversa` é uma lista de {"role": "user"|"model", "parts": [{"text": ...}]}.
Erros técnicos são repetidos dentro do provedor; quando não há mais o que fazer
(cota esgotada, chave inválida), o provedor levanta CotaEsgotada e aciona PARAR.
"""
import importlib
import threading
import time

ESPERA_INICIAL = 10     # segundos; dobra a cada erro técnico
MAX_ERROS_TECNICOS = 5  # tentativas por chamada antes de desistir dela

PARAR = threading.Event()  # acionado quando a cota acaba: todas as threads param logo


class CotaEsgotada(Exception):
    """A API recusou por cota/créditos/acesso: interrompe sem perder o progresso."""


_trava_ritmo = threading.Lock()
_proxima_chamada = [0.0]


def respeitar_ritmo(rpm):
    """Espaça as chamadas para não passar de `rpm` por minuto (vale para todas as threads)."""
    if not rpm:
        return
    intervalo = 60.0 / rpm
    with _trava_ritmo:
        agora = time.monotonic()
        espera = _proxima_chamada[0] - agora
        _proxima_chamada[0] = max(agora, _proxima_chamada[0]) + intervalo
    if espera > 0 and PARAR.wait(espera):
        raise CotaEsgotada("execução interrompida")


def esperar(segundos):
    """Espera entre tentativas técnicas; acorda na hora se outra thread mandou parar."""
    if PARAR.wait(segundos):
        raise CotaEsgotada("execução interrompida")


def parar(mensagem):
    PARAR.set()
    raise CotaEsgotada(mensagem)


def carregar(provedor):
    """Importa o módulo do provedor (gemini, openai, anthropic ou teste)."""
    modulos = {"gemini": "provedores.gemini", "openai": "provedores.openai_api",
               "anthropic": "provedores.anthropic_api", "teste": "provedores.teste"}
    if provedor not in modulos:
        raise SystemExit(f"Provedor desconhecido: {provedor}. Opções: {', '.join(modulos)}")
    try:
        return importlib.import_module(modulos[provedor])
    except ModuleNotFoundError as erro:
        raise SystemExit(f"Provedor desconhecido ou dependência ausente: {provedor} ({erro})") from erro
