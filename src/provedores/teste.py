"""Provedor de teste: devolve a solução de referência, sem chamar API nenhuma.

Serve para validar o pipeline (fila, testes, retomada, Pylint) sem gastar cota.
"""


def criar_cliente(cfg):
    return None


def chamar(cliente, conversa, exercicio, cfg):
    return f"```python\n{exercicio['solucao_referencia']}\n```"
