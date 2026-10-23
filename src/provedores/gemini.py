"""Provedor Google Gemini (pacote google-genai). Chave: GEMINI_API_KEY no .env."""
import os
import re
import sys

from google import genai
from google.genai import errors, types

from provedores import (ESPERA_INICIAL, MAX_ERROS_TECNICOS, PARAR, CotaEsgotada,
                        esperar, parar, respeitar_ritmo)


def criar_cliente(cfg):
    chave = os.getenv("GEMINI_API_KEY", "").strip()
    if not chave:
        sys.exit("GEMINI_API_KEY não definida no .env")
    return genai.Client(api_key=chave)


def chamar(cliente, conversa, exercicio, cfg):
    temperatura = cfg.get("temperatura")
    config = types.GenerateContentConfig(temperature=temperatura) if temperatura is not None else None
    slug = exercicio["slug"]
    espera = ESPERA_INICIAL
    for tentativa in range(1, MAX_ERROS_TECNICOS + 1):
        if PARAR.is_set():
            raise CotaEsgotada("execução interrompida")
        respeitar_ritmo(cfg.get("requisicoes_por_minuto"))
        try:
            resposta = cliente.models.generate_content(model=cfg["modelo"], contents=conversa, config=config)
            return resposta.text or ""
        except errors.APIError as erro:
            codigo = getattr(erro, "code", None)
            mensagem = str(erro)
            limite = re.search(r"quotaId['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9_-]+)", mensagem)
            limite = limite.group(1) if limite else ""
            atraso = re.search(r"retryDelay['\"]?\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)s", mensagem)
            if codigo == 429 and "PerDay" in limite:
                parar(f"cota diária esgotada ({limite}); continue amanhã")
            if codigo == 429 and tentativa == MAX_ERROS_TECNICOS:
                parar(f"limite de requisições ({limite or 'sem detalhe'})")
            if codigo in (401, 403):
                parar(f"acesso negado ({codigo}): confira a GEMINI_API_KEY. {mensagem[:200]}")
            if codigo is not None and codigo < 500 and codigo != 429:
                PARAR.set()
                raise  # erro do pedido (ex.: modelo inexistente): não adianta repetir
            if atraso:  # a API diz quanto esperar: usa esse tempo (com folga de 1s)
                espera = max(espera, float(atraso.group(1)) + 1)
            print(f"    {slug}: erro técnico ({codigo}{', ' + limite if limite else ''}), "
                  f"nova tentativa em {espera:.0f}s")
        except CotaEsgotada:
            raise
        except Exception as erro:  # rede, timeout de conexão etc.
            print(f"    {slug}: erro técnico ({type(erro).__name__}), nova tentativa em {espera:.0f}s")
        esperar(espera)
        espera *= 2
    parar("erros técnicos repetidos; interrompendo para não perder progresso")
