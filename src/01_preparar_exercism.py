"""Etapa 1: prepara a base de tarefas a partir do Exercism (trilha de Python).

Base escolhida após avaliar MBPP e FPEval (ver docs/decisoes_metodologicas.md).
O Exercism traz tarefas de programação gerais, não só algorítmicas, e cerca
de 31% dos esqueletos são classes, então o paradigma OO aparece de forma
natural, sem precisar ser imposto pelo prompt.

Fonte: https://github.com/exercism/python (licença MIT).

O que o script faz:
1. Clona o repositório em dados/_cache/exercism-python e fixa a versão no commit
   do estudo (COMMIT_EXERCISM), para que todas as máquinas usem os mesmos exercícios.
2. Lê config.json e mantém os exercícios práticos ativos (não obsoletos).
3. Para cada exercício, junta enunciado, esqueleto, testes e solução de
   referência, e classifica o esqueleto como "classe", "funcao" ou "ambos".
4. Roda os testes contra a solução de referência e registra se passou,
   para descartar depois exercícios com teste quebrado.
5. Salva tudo em dados/exercism.jsonl (um exercício por linha).

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/01_preparar_exercism.py
"""
import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "dados" / "_cache" / "exercism-python"
SAIDA = RAIZ / "dados" / "exercism.jsonl"
REPO_URL = "https://github.com/exercism/python.git"
TIMEOUT_TESTES = 60  # segundos por exercício


COMMIT_EXERCISM = "6105f6d9d3ef66ce3d5c8f529d2882af3d76b706"  # versão usada no estudo (30/09/2026)


def clonar_repositorio():
    """Clona o Exercism (se preciso) e fixa a versão no commit do estudo, para que toda
    máquina (inclusive a do GitHub Actions) use os mesmos enunciados, esqueletos e testes."""
    if not CACHE.exists():
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        print(f"Clonando {REPO_URL} ...")
        subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(CACHE)], check=True)
    else:
        print(f"Usando cópia já existente em {CACHE}")
    atual = subprocess.run(["git", "-C", str(CACHE), "rev-parse", "HEAD"],
                           check=True, capture_output=True, text=True).stdout.strip()
    if atual != COMMIT_EXERCISM:
        print(f"Fixando o Exercism no commit {COMMIT_EXERCISM[:7]} ...")
        subprocess.run(["git", "-C", str(CACHE), "fetch", "--depth", "1", "origin", COMMIT_EXERCISM], check=True)
        subprocess.run(["git", "-C", str(CACHE), "checkout", "--quiet", COMMIT_EXERCISM], check=True)
    return COMMIT_EXERCISM


def ler(caminho):
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def tipo_do_esqueleto(codigo):
    """Classifica o esqueleto pelo que ele define no nível superior."""
    arvore = ast.parse(codigo)
    tem_classe = any(isinstance(n, ast.ClassDef) for n in arvore.body)
    tem_funcao = any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in arvore.body)
    if tem_classe and tem_funcao:
        return "ambos"
    if tem_classe:
        return "classe"
    if tem_funcao:
        return "funcao"
    return "outro"


def referencia_passa(pasta, arquivos_solucao, arquivos_teste, arquivos_exemplo):
    """Roda os testes do exercício usando a solução de referência no lugar do esqueleto."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # copia tudo da pasta do exercício (alguns testes usam arquivos auxiliares)
        for item in pasta.iterdir():
            if item.name.startswith("."):
                continue
            destino = tmp / item.name
            if item.is_dir():
                shutil.copytree(item, destino)
            else:
                shutil.copy(item, destino)
        # a solução de referência substitui o esqueleto
        shutil.copy(pasta / arquivos_exemplo[0], tmp / arquivos_solucao[0])
        modulos = [Path(t).stem for t in arquivos_teste]
        try:
            resultado = subprocess.run(
                [sys.executable, "-m", "unittest", *modulos],
                cwd=tmp, capture_output=True, text=True, timeout=TIMEOUT_TESTES,
            )
            return resultado.returncode == 0
        except subprocess.TimeoutExpired:
            return False


def main():
    commit = clonar_repositorio()
    praticos = CACHE / "exercises" / "practice"
    config = json.loads(ler(CACHE / "config.json"))
    ativos = [e for e in config["exercises"]["practice"] if e.get("status") != "deprecated"]
    print(f"Exercícios práticos ativos: {len(ativos)}")

    registros = []
    for ex in ativos:
        slug = ex["slug"]
        pasta = praticos / slug
        meta = json.loads(ler(pasta / ".meta" / "config.json"))
        arq = meta["files"]

        enunciado = ler(pasta / ".docs" / "instructions.md")
        extra = ler(pasta / ".docs" / "instructions.append.md")
        if extra:
            enunciado += "\n\n" + extra

        esqueleto = ler(pasta / arq["solution"][0])
        registro = {
            "slug": slug,
            "nome": ex.get("name", slug),
            "dificuldade": ex.get("difficulty"),
            "enunciado": enunciado,
            "esqueleto": esqueleto,
            "testes": "\n\n".join(ler(pasta / t) for t in arq["test"]),
            "solucao_referencia": ler(pasta / arq["example"][0]),
            "arquivo_solucao": arq["solution"][0],
            "arquivos_teste": arq["test"],
            "tipo_esqueleto": tipo_do_esqueleto(esqueleto),
            "referencia_passa": referencia_passa(pasta, arq["solution"], arq["test"], arq["example"]),
            "commit_exercism": commit,
        }
        registros.append(registro)
        status = "ok" if registro["referencia_passa"] else "FALHOU"
        print(f"  {slug:30s} {registro['tipo_esqueleto']:7s} referência: {status}")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with SAIDA.open("w", encoding="utf-8") as f:
        for r in registros:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    tipos = {}
    for r in registros:
        tipos[r["tipo_esqueleto"]] = tipos.get(r["tipo_esqueleto"], 0) + 1
    falhas = sum(not r["referencia_passa"] for r in registros)
    print(f"\nSalvo em: {SAIDA}")
    print(f"Tipos de esqueleto: {tipos}")
    print(f"Referências que falharam nos testes: {falhas}")


if __name__ == "__main__":
    main()
