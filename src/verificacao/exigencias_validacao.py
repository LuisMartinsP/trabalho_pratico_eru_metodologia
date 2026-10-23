"""Gera dados/validacao/exigencias.md: o que cada exercício da amostra de validação exige
além do esqueleto, para o avaliador consultar durante a avaliação.

Mostra só informação do EXERCÍCIO (esqueleto, testes, enunciado), nunca a fonte da
solução nem o rótulo da ferramenta, para não quebrar a avaliação às cegas.

Para cada arquivo V###.py:
    - definido no esqueleto: classes, métodos, funções e constantes já impostos
    - importado pelos testes e ausente do esqueleto: nomes que a solução é obrigada a criar
    - usado pelos testes nos objetos e ausente do esqueleto: métodos/atributos chamados nos
      testes (ex.: garden.plants(...)), excluindo os métodos do unittest, dos tipos embutidos
      (str, list, dict...) e das exceções (err.exception.args)
    - trechos do enunciado que falam de classes, métodos ou funções a implementar
A lista de métodos usados pelos testes é obtida automaticamente e pode trazer nomes que não
são exigências (ex.: um atributo de um objeto devolvido pela solução); confira no enunciado.

Uso: python src/verificacao/exigencias_validacao.py   (depois de 07_validacao.py amostra)
"""
import ast
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tabelas as T  # noqa: E402

EMBUTIDOS = set().union(*(dir(t) for t in (str, list, dict, set, int, float, tuple, bytes, frozenset)))
IGNORAR = EMBUTIDOS | {"exception", "args", "maxDiff", "main", "TestCase", "subTest", "fail", "skipTest"}
RE_ENUNCIADO = re.compile(r"\bclass(es)?\b|\bmethods?\b|\bfunctions?\b|\bimplement|\bproperty\b|\battributes?\b", re.I)


def definidos_no_esqueleto(codigo):
    arv = ast.parse(codigo)
    itens = []
    for n in arv.body:
        if isinstance(n, ast.ClassDef):
            metodos = [m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))]
            itens.append(f"classe `{n.name}`" + (f" (métodos: {', '.join(f'`{m}`' for m in metodos)})" if metodos else ""))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            itens.append(f"função `{n.name}`")
        elif isinstance(n, ast.Assign):
            itens += [f"constante `{t.id}`" for t in n.targets if isinstance(t, ast.Name)]
    return itens


def nomes_do_esqueleto(codigo):
    return {n.name for n in ast.walk(ast.parse(codigo)) if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))} | {
        t.id for n in ast.walk(ast.parse(codigo)) if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}


def exigencias_dos_testes(ex):
    modulo = ex["arquivo_solucao"][:-3]
    arv = ast.parse(ex["testes"])
    esq = nomes_do_esqueleto(ex["esqueleto"])
    importados = set()
    for n in ast.walk(arv):
        if isinstance(n, ast.ImportFrom) and n.module == modulo:
            importados |= {a.name for a in n.names}
    # nomes de outros módulos importados pelo teste (math, json, io, unittest.mock...): os
    # atributos deles (math.pi, json.dumps) não são exigências à solução
    externos = {"self", "unittest"}
    for n in ast.walk(arv):
        if isinstance(n, ast.Import):
            externos |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module != modulo:
            externos |= {a.asname or a.name for a in n.names}
    usados = set()
    for n in ast.walk(arv):
        if isinstance(n, ast.Attribute) and not n.attr.startswith("assert"):
            base = n.value
            while isinstance(base, ast.Attribute):
                base = base.value
            if isinstance(base, ast.Name) and base.id in externos:
                continue
            usados.add(n.attr)
    return sorted(importados - esq), sorted(usados - esq - IGNORAR - importados)


def main():
    gab = T.VALIDACAO / "gabarito.csv"
    if not gab.exists():
        sys.exit("Falta a amostra. Rode antes: python src/07_validacao.py amostra")
    ids = pd.read_csv(gab)[["id", "slug"]].sort_values("id")
    exs = {e["slug"]: e for e in T.exercicios()}
    partes = ["# Exigências de cada exercício da amostra\n",
              "Consulta para a avaliação: o que o **exercício** impõe ou exige além do esqueleto. "
              "Não traz a fonte da solução nem o rótulo da ferramenta.\n",
              "Lembrete: estruturas exigidas (classes, métodos, funções) não são escolha de quem resolveu; "
              "julgue o estilo do código dentro delas.\n"]
    for r in ids.itertuples():
        ex = exs[r.slug]
        importados, usados = exigencias_dos_testes(ex)
        trechos = [l.strip() for l in ex["enunciado"].splitlines()
                   if RE_ENUNCIADO.search(l) and not l.strip().startswith("[")]
        partes.append(f"## {r.id} · {r.slug}\n")
        partes.append("- **Definido no esqueleto:** " + ("; ".join(definidos_no_esqueleto(ex["esqueleto"])) or "nada"))
        partes.append("- **Importado pelos testes e ausente do esqueleto:** "
                      + (", ".join(f"`{n}`" for n in importados) or "nada"))
        partes.append("- **Usado pelos testes nos objetos e ausente do esqueleto:** "
                      + (", ".join(f"`{n}`" for n in usados) or "nada"))
        if trechos:
            partes.append("- **Enunciado:**\n" + "\n".join(f"  > {t}" for t in trechos))
        partes.append("")
    destino = T.VALIDACAO / "exigencias.md"
    destino.write_text("\n".join(partes), encoding="utf-8")
    print(f"Consulta: {destino} ({len(ids)} arquivos)")


if __name__ == "__main__":
    main()
