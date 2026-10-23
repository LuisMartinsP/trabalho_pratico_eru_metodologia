"""Provedor Anthropic (pacote anthropic, Messages API). Chave: ANTHROPIC_API_KEY no .env.

O arquivo não se chama anthropic.py para não esconder o pacote oficial `anthropic`.

Parâmetros: como no gpt-5-mini, o modelo roda com as configurações padrão (raciocínio
adaptativo ligado; temperatura padrão). Os modelos Claude mais novos recusam temperatura
diferente do padrão, então `temperatura: null` no perfil. A chamada usa streaming porque
o SDK exige streaming para pedidos com limite de saída alto.
"""
import os
import sys

import anthropic

from provedores import (ESPERA_INICIAL, MAX_ERROS_TECNICOS, PARAR, CotaEsgotada,
                        esperar, parar, respeitar_ritmo)

MAX_TOKENS = 32000  # teto da resposta (inclui o raciocínio); as soluções são bem menores


def criar_cliente(cfg):
    chave = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not chave:
        sys.exit("ANTHROPIC_API_KEY não definida no .env")
    return anthropic.Anthropic(api_key=chave, max_retries=0)  # as repetições são feitas aqui


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
            with cliente.messages.stream(model=cfg["modelo"], max_tokens=MAX_TOKENS,
                                         messages=mensagens, **extra) as fluxo:
                resposta = fluxo.get_final_message()
            # só os blocos de texto: os blocos de raciocínio (thinking) ficam de fora
            return "".join(b.text for b in resposta.content if b.type == "text")
        except anthropic.RateLimitError:
            if tentativa == MAX_ERROS_TECNICOS:
                parar("limite de requisições da Anthropic")
            print(f"    {slug}: erro técnico (429, limite por minuto), nova tentativa em {espera}s")
        except anthropic.AuthenticationError as erro:
            parar(f"acesso negado: confira a ANTHROPIC_API_KEY. {str(erro)[:200]}")
        except anthropic.PermissionDeniedError as erro:
            parar(f"sem permissão para o modelo {cfg['modelo']}. {str(erro)[:200]}")
        except anthropic.APIStatusError as erro:
            if "credit balance" in str(erro).lower():
                parar("créditos da Anthropic esgotados (credit balance too low)")
            if erro.status_code < 500:
                PARAR.set()
                raise  # erro do pedido (ex.: modelo inexistente, parâmetro não suportado)
            # 500, 529 (sobrecarga): repetir
            print(f"    {slug}: erro técnico ({erro.status_code}), nova tentativa em {espera}s")
        except anthropic.APIConnectionError as erro:
            print(f"    {slug}: erro técnico ({type(erro).__name__}), nova tentativa em {espera}s")
        esperar(espera)
        espera *= 2
    parar("erros técnicos repetidos; interrompendo para não perder progresso")
