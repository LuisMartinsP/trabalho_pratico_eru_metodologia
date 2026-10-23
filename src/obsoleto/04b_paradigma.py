"""OBSOLETO: substituído por `python src/04_paradigma.py --versao b`.

Mantido só como registro da metodologia. A versão B rotulava como OO todo exercício com
esqueleto de classe, o que faz o rótulo vir do exercício e não da solução (ex.: `luhn`).
A versão adotada é a C; ver docs/decisoes_metodologicas.md, seção 10.
Este arquivo importava ../04_paradigma.py (antiga versão A) e não roda mais a partir de src/obsoleto/.
"""
"""Etapa 4 (versão B): classificação de paradigma com OO definido pela estrutura.

Diferença em relação a 04_paradigma.py (versão A):
    A  OO, funcional e procedural disputam o mesmo placar; o OO quase sempre "perde"
       para o código dentro dos próprios métodos e muitas soluções com classes caem em "misto".
    B  OO é decidido pela ESTRUTURA, antes do estilo:
         - OO se o esqueleto do exercício é uma classe ("classe" ou "ambos"),
           ou se a solução criou classes novas;
         - caso contrário, funcional / procedural / misto / neutro, usando só os pontos
           funcionais e procedurais da regra adaptada (mesmo critério dos 2/3).
       O campo "origem_oo" diz se o OO veio do esqueleto ("esqueleto") ou da solução ("solucao").

Saídas (separadas das da versão A, para comparar):
    dados/paradigmas_b/<fonte>.csv
    dados/paradigmas_b/<fonte>/<paradigma>/<slug>.py
    relatorios/paradigmas_b.md     inclui a comparação A × B

Uso:
    python src/04b_paradigma.py referencia gpt-mini
"""
import argparse
import ast
import importlib.util
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import paradigma_adaptado  # noqa: E402

_spec = importlib.util.spec_from_file_location("etapa4a", AQUI / "04_paradigma.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)  # reaproveita fontes, leitura de soluções e tabelas da versão A

SAIDA = A.DADOS / "paradigmas_b"
RELATORIO = A.RAIZ / "relatorios" / "paradigmas_b.md"
ORDEM = ["oo", "funcional", "procedural", "misto", "neutro"]


def classes_novas(codigo, esqueleto):
    """Nomes de classes definidas na solução que não existem no esqueleto."""
    no_esq = {n.name for n in ast.walk(ast.parse(esqueleto)) if isinstance(n, ast.ClassDef)}
    return sorted({n.name for n in ast.walk(ast.parse(codigo)) if isinstance(n, ast.ClassDef)} - no_esq)


def rotulo_b(ex, codigo):
    a = paradigma_adaptado.classificar(codigo, ex["esqueleto"])
    novas = classes_novas(codigo, ex["esqueleto"])
    if ex["tipo_esqueleto"] in ("classe", "ambos"):
        return "oo", "esqueleto", novas, a
    if novas:
        return "oo", "solucao", novas, a
    func, proc = a["func"], a["proc"]
    total = func + proc
    if total == 0:
        return "neutro", "", novas, a
    if func >= 2 * total / 3:
        return "funcional", "", novas, a
    if proc >= 2 * total / 3:
        return "procedural", "", novas, a
    return "misto", "", novas, a


def classificar_fonte(fonte, exercicios):
    linhas = []
    pasta = SAIDA / fonte
    if pasta.exists():
        shutil.rmtree(pasta)
    for ex, codigo, tentativas in A.solucoes(fonte, exercicios):
        rot, origem, novas, a = rotulo_b(ex, codigo)
        linhas.append({"fonte": fonte, "slug": ex["slug"], "tipo_esqueleto": ex["tipo_esqueleto"],
                       "tentativas": tentativas, "paradigma": rot, "origem_oo": origem,
                       "classes_novas": ", ".join(novas),
                       "pontos_funcional": a["func"], "pontos_procedural": a["proc"], "pontos_oo": a["oo"],
                       "paradigma_versao_a": a["paradigma"]})
        destino = pasta / rot / f"{ex['slug']}.py"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(codigo, encoding="utf-8")
    df = pd.DataFrame(linhas)
    SAIDA.mkdir(parents=True, exist_ok=True)
    df.to_csv(SAIDA / f"{fonte}.csv", index=False, encoding="utf-8")
    print(f"[{fonte}] {len(df)} soluções · " + " · ".join(f"{p}: {int((df['paradigma'] == p).sum())}" for p in ORDEM))
    return df


def relatorio(dfs):
    md = A.tabela_md
    fontes = list(dfs)
    total = pd.DataFrame({f: df["paradigma"].value_counts().reindex(ORDEM, fill_value=0) for f, df in dfs.items()})
    total.insert(0, "paradigma", total.index)

    origem = pd.DataFrame({f: df[df["paradigma"] == "oo"]["origem_oo"].value_counts()
                           .reindex(["esqueleto", "solucao"], fill_value=0) for f, df in dfs.items()})
    origem.insert(0, "OO veio de", origem.index)

    a_x_b = []
    for f, df in dfs.items():
        t = pd.crosstab(df["paradigma_versao_a"], df["paradigma"])
        t = t.reindex(index=["funcional", "procedural", "oo", "misto", "neutro"], columns=ORDEM, fill_value=0)
        t.insert(0, f"{f}: versão A \\ versão B", t.index)
        a_x_b.append(md(t))

    pares = ""
    if "referencia" in dfs:
        h = dfs["referencia"].set_index("slug")
        blocos = []
        for f in fontes:
            if f == "referencia":
                continue
            m = dfs[f].set_index("slug")
            comuns = h.index.intersection(m.index)
            par = pd.DataFrame({"humano": h.loc[comuns, "paradigma"], f: m.loc[comuns, "paradigma"]})
            iguais = int((par["humano"] == par[f]).sum())
            mat = pd.crosstab(par["humano"], par[f]).reindex(index=ORDEM, columns=ORDEM, fill_value=0)
            mat.insert(0, f"humano \\ {f}", mat.index)
            blocos.append(f"### Humano × {f}\n\nEm comum: **{len(par)}** · mesmo paradigma: **{iguais}** "
                          f"({100 * iguais / max(len(par), 1):.0f}%)\n\n{md(mat)}\n")
        pares = "\n".join(blocos)

    texto = f"""# Paradigmas das soluções: versão B (OO pela estrutura)

Gerado em {datetime.now():%Y-%m-%d %H:%M}

**Regra B:** OO se o esqueleto é uma classe ou se a solução criou classes novas;
senão, funcional / procedural / misto / neutro pelos pontos funcionais e
procedurais da regra adaptada (2/3).

## 1. Total por fonte

{md(total)}

## 2. De onde veio o OO

{md(origem)}

## 3. Humano × modelo, exercício a exercício

{pares or "(precisa da referência e de um modelo)"}

## 4. Como a versão A vira a versão B

Linhas: rótulo na versão A; colunas: rótulo na versão B.

{chr(10).join(a_x_b)}
"""
    RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    RELATORIO.write_text(texto, encoding="utf-8")
    print(f"\nRelatório: {RELATORIO}")


def main():
    parser = argparse.ArgumentParser(description="Classificação de paradigma, versão B (OO pela estrutura).")
    parser.add_argument("fontes", nargs="*")
    args = parser.parse_args()
    exercicios = [json.loads(l) for l in A.ENTRADA.read_text(encoding="utf-8").splitlines()]
    exercicios = [e for e in exercicios if e["referencia_passa"]]
    fontes = [A.resolver_fonte(f) for f in args.fontes] or ["referencia", *A.modelos_disponiveis()]
    dfs = {f: d for f in dict.fromkeys(fontes) if len(d := classificar_fonte(f, exercicios))}
    if dfs:
        relatorio(dfs)


if __name__ == "__main__":
    main()
