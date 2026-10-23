"""Funções compartilhadas para rodar os testes de um exercício do Exercism.

Usado pela etapa de geração (validação a cada tentativa) e por qualquer
etapa que precise reexecutar os testes sem chamar a API.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PRATICOS = RAIZ / "dados" / "_cache" / "exercism-python" / "exercises" / "practice"
TIMEOUT_TESTES = 60  # segundos por execução
LIMITE_SAIDA = 4000  # caracteres da saída dos testes guardados/enviados à LLM


def rodar_testes(slug, codigo, arquivo_solucao, arquivos_teste):
    """Roda os testes do exercício com `codigo` no lugar do esqueleto.

    Devolve (status, saida), em que status é um destes:
        "passou", "falhou", "erro_sintaxe" ou "timeout".
    """
    try:
        compile(codigo, arquivo_solucao, "exec")
    except SyntaxError as erro:
        return "erro_sintaxe", f"SyntaxError: {erro}"

    pasta = PRATICOS / slug
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # copia a pasta do exercício (alguns testes usam arquivos auxiliares)
        for item in pasta.iterdir():
            if item.name.startswith("."):
                continue
            destino = tmp / item.name
            if item.is_dir():
                shutil.copytree(item, destino)
            else:
                shutil.copy(item, destino)
        (tmp / arquivo_solucao).write_text(codigo, encoding="utf-8")

        modulos = [Path(t).stem for t in arquivos_teste]
        try:
            resultado = subprocess.run(
                [sys.executable, "-m", "unittest", *modulos],
                cwd=tmp, capture_output=True, text=True, timeout=TIMEOUT_TESTES,
            )
        except subprocess.TimeoutExpired:
            return "timeout", f"Os testes excederam {TIMEOUT_TESTES} segundos."

    saida = (resultado.stderr + resultado.stdout).strip()
    if len(saida) > LIMITE_SAIDA:
        saida = saida[:LIMITE_SAIDA] + "\n... (saída truncada)"
    return ("passou" if resultado.returncode == 0 else "falhou"), saida
