"""Etapa 4: classifica o paradigma de cada tentativa com código válido.

Duas regras de pontos, aplicadas só ao código acrescentado ao esqueleto:
    D (oficial)  pontos por OPERAÇÃO: src/paradigma_operacoes.py (decisões, seção 11)
    C            pontos por COMANDO:  src/paradigma_adaptado.py  (decisões, seções 9 e 10)
A regra oficial e o mínimo de pontos ficam em config/analise.yaml; a C é guardada para a
análise de sensibilidade.

Rótulo de cada regra (rotulo_d / rotulo_c):
    oo           a solução CRIOU classes novas, além das que o esqueleto já trazia
    funcional    senão: pontos funcionais >= 2/3 de (funcionais + procedurais)
    procedural   senão: pontos procedurais >= 2/3
    misto        nenhum dos dois chega a 2/3
    neutro       nenhum ponto (código sem sinal de estilo)
Rótulo filtrado (filtrado_d / filtrado_c): igual ao rótulo, exceto que funcional, procedural
e misto com menos de `min_pontos` pontos (funcionais + procedurais) viram "indeterminado".
Com tão poucos pontos o rótulo depende de uma ou duas construções e muda com ±1 ponto
(decisões, seção 12). Neutro e OO não passam pelo filtro: neutro já é a ausência de pontos,
e OO é decidido pelas classes novas, não pelos pontos.

Também é registrado o rótulo da regra original de Dyer e Chauhan (src/paradigma_dyer.py),
sem adaptação, só para documentar por que ela não é usada (decisões, seção 9).

Saída: dados/tabelas/paradigmas.csv (uma linha por tentativa com código válido). Cada fonte
substitui só as próprias linhas.

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/04_paradigma.py                         # fontes de config/analise.yaml
    python src/04_paradigma.py referencia gpt-mini
"""
import argparse
import ast
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paradigma_adaptado  # noqa: E402
import paradigma_dyer  # noqa: E402
import paradigma_operacoes  # noqa: E402
import tabelas as T  # noqa: E402

SRC = Path(__file__).resolve().parent
CLASSIFICADORES = [SRC / "paradigma_operacoes.py", SRC / "paradigma_adaptado.py", SRC / "paradigma_dyer.py",
                   Path(__file__).resolve()]
ORDEM = ["oo", "funcional", "procedural", "misto", "neutro", "indeterminado"]


def classes_novas(codigo, esqueleto):
    no_esq = {n.name for n in ast.walk(ast.parse(esqueleto)) if isinstance(n, ast.ClassDef)}
    return sorted({n.name for n in ast.walk(ast.parse(codigo)) if isinstance(n, ast.ClassDef)} - no_esq)


def estilo(func, proc):
    total = func + proc
    if total == 0:
        return "neutro"
    if func >= 2 * total / 3:
        return "funcional"
    if proc >= 2 * total / 3:
        return "procedural"
    return "misto"


def rotular(pontos, novas, min_pontos):
    total = pontos["func"] + pontos["proc"]
    rotulo = "oo" if novas else estilo(pontos["func"], pontos["proc"])
    filtrado = rotulo if rotulo in ("oo", "neutro") or total >= min_pontos else "indeterminado"
    return total, rotulo, filtrado


def classificar_fonte(fonte, exercicios, min_pontos):
    linhas, invalidas = [], 0
    for t in T.tentativas(fonte, exercicios):
        ex, codigo = t["ex"], t["codigo"]
        try:
            ast.parse(codigo)
        except SyntaxError:
            invalidas += 1
            continue
        if not codigo.strip():
            invalidas += 1
            continue
        novas = classes_novas(codigo, ex["esqueleto"])
        linha = {"fonte": fonte, "slug": ex["slug"], "tentativa": t["tentativa"], "classes_novas": ", ".join(novas)}
        for sufixo, mod in (("d", paradigma_operacoes), ("c", paradigma_adaptado)):
            p = mod.classificar(codigo, ex["esqueleto"])
            total, rotulo, filtrado = rotular(p, novas, min_pontos)
            linha |= {f"pontos_func_{sufixo}": p["func"], f"pontos_proc_{sufixo}": p["proc"],
                      f"pontos_oo_{sufixo}": p["oo"], f"total_pontos_{sufixo}": total,
                      f"rotulo_{sufixo}": rotulo, f"filtrado_{sufixo}": filtrado}
        try:
            linha["rotulo_dyer_original"] = paradigma_dyer.classificar(codigo)["paradigma"]
        except Exception:  # noqa: BLE001
            linha["rotulo_dyer_original"] = None
        linhas.append(linha)
    return pd.DataFrame(linhas, columns=T.COLUNAS["paradigmas"]), invalidas


def main():
    parser = argparse.ArgumentParser(description="Classifica o paradigma de cada tentativa.")
    parser.add_argument("fontes", nargs="*", help="referencia, perfis de config/modelos.yaml ou pastas em dados/ "
                                                  "(sem argumentos: as fontes de config/analise.yaml)")
    args = parser.parse_args()
    cfg = T.analise()["paradigma"]
    exercicios = T.exercicios()
    fontes = T.resolver_fontes(args.fontes)
    parametros = {"min_pontos": cfg["min_pontos"], "classificadores": T.hash_arquivos(*CLASSIFICADORES),
                  "exercism_commit": T.commit_exercism()}
    oficial = cfg["regra_oficial"]
    print(f"Regra oficial: {oficial.upper()} · mínimo de pontos: {cfg['min_pontos']}")

    for fonte in fontes:
        df, invalidas = classificar_fonte(fonte, exercicios, cfg["min_pontos"])
        if df.empty:
            print(f"[{fonte}] nenhuma tentativa encontrada; nada gravado")
            continue
        T.salvar("paradigmas", df, "04_paradigma.py", [fonte], parametros)
        aceitas = df.merge(pd.DataFrame([{"slug": t["ex"]["slug"], "tentativa": t["tentativa"]}
                                         for t in T.tentativas(fonte, exercicios) if t["aceita"]]),
                           on=["slug", "tentativa"])
        cont = aceitas[f"filtrado_{oficial}"].value_counts().reindex(ORDEM, fill_value=0)
        print(f"[{fonte}] {len(df)} tentativa(s) classificadas ({invalidas} sem código válido) · aceitas: "
              + " · ".join(f"{k}: {v}" for k, v in cont.items()))
    print(f"\nTabela: {T.caminho('paradigmas')}")


if __name__ == "__main__":
    main()
