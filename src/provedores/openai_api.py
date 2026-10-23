"""Provedor OpenAI (pacote openai, Chat Completions). Chave: OPENAI_API_KEY no .env.

O arquivo não se chama openai.py para não esconder o pacote oficial `openai`.
"""
import os
import sys

import openai

from provedores import (ESPERA_INICIAL, MAX_ERROS_TECNICOS, PARAR, CotaEsgotada,
                        esperar, parar, respeitar_ritmo)


def criar_cliente(cfg):
    chave = os.getenv("OPENAI_API_KEY", "").strip()
    if not chave:
        sys.exit("OPENAI_API_KEY não definida no .env")
    return openai.OpenAI(api_key=chave, max_retries=0)  # as repetições são feitas aqui


def chamar(cliente, conversa, exercicio, cfg):
    mensagens = [{"role": "assistant" if m["role"] == "model" else "user",
                  "content": m["parts"][0]["text"]} for m in conversa]
    extra = {"temperature": cfg["temperatura"]} if cfg.get("temperatura") is not None else {}
    slug = exercicio["slug"]
    espera = ESPERA_INICIAL
    for tentativa in range(1, MAX_ERROS_TECNICOS + 1):
        if PARAR.is_set():
            raise CotaEsgotada("execução interrompida")
        respeitar_ritmo(cfg.get("requisicoes_por_minuto"))
        try:
            resposta = cliente.chat.completions.create(model=cfg["modelo"], messages=mensagens, **extra)
            return resposta.choices[0].message.content or ""
        except openai.RateLimitError as erro:
            corpo = getattr(erro, "body", None) or {}
            if isinstance(corpo, dict) and corpo.get("code") == "insufficient_quota":
                parar("créditos da OpenAI esgotados (insufficient_quota)")
            if tentativa == MAX_ERROS_TECNICOS:
                parar("limite de requisições da OpenAI")
            print(f"    {slug}: erro técnico (429, limite por minuto), nova tentativa em {espera}s")
        except openai.AuthenticationError as erro:
            parar(f"acesso negado: confira a OPENAI_API_KEY. {str(erro)[:200]}")
        except openai.APIStatusError as erro:
            if erro.status_code < 500:
                PARAR.set()
                raise  # erro do pedido (ex.: modelo inexistente, parâmetro não suportado)
            print(f"    {slug}: erro técnico ({erro.status_code}), nova tentativa em {espera}s")
        except openai.APIConnectionError as erro:
            print(f"    {slug}: erro técnico ({type(erro).__name__}), nova tentativa em {espera}s")
        esperar(espera)
        espera *= 2
    parar("erros técnicos repetidos; interrompendo para não perder progresso")
