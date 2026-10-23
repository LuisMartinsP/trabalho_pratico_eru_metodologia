"""Verifica se as classes novas das soluções foram exigidas pelo exercício.

A regra de paradigma rotula OO quando a solução cria classes além das do esqueleto
(docs/decisoes_metodologicas.md, seções 10 e 12). Isso só mede uma ESCOLHA de quem resolveu
se o exercício não exigir essas classes. Esta verificação confere três fontes de exigência:

    1. Testes: nomes que os testes importam do módulo da solução e que o esqueleto não define.
       Se um teste importa uma classe, quem resolve é obrigado a criá-la.
    2. Enunciado (instructions.md + instructions.append.md): linhas que citam o nome da classe,
       a palavra "class" ou "iterator". É uma busca textual; as linhas encontradas são
       listadas para leitura manual.
    3. Tipo da classe: se herda de Exception/Error (exceção customizada), o que é um uso
       mínimo de OO e é sinalizado à parte.

Entradas: dados/exercism.jsonl, dados/tabelas/paradigmas.csv e analise.csv (etapas 1, 4 e 5).
Saída: relatorios/classes_exigidas.md

Uso: python src/verificacao/verificar_classes_exigidas.py
"""
import ast
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tabelas as T  # noqa: E402


def importados_pelos_testes(ex):
    modulo = ex["arquivo_solucao"][:-3]
    arvore = ast.parse(ex["testes"])
    nomes = set()
    # "import modulo" (sem apelido): os nomes usados como modulo.Nome também são exigidos
    importa_modulo = any(isinstance(n, ast.Import) and any(a.name == modulo and a.asname is None for a in n.names)
                         for n in ast.walk(arvore))
    for n in ast.walk(arvore):
        if isinstance(n, ast.ImportFrom) and n.module == modulo:
            nomes |= {a.name for a in n.names}
        elif (importa_modulo and isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
              and n.value.id == modulo):
            nomes.add(n.attr)
    return nomes


def definidos(codigo):
    return {n.name for n in ast.parse(codigo).body
            if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))} | {
        t.id for n in ast.parse(codigo).body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}


def classes(codigo):
    return {n.name: n for n in ast.walk(ast.parse(codigo)) if isinstance(n, ast.ClassDef)}


def main():
    exs = {e["slug"]: e for e in T.exercicios()}

    # 1) o que os testes exigem além do esqueleto, em todos os exercícios
    linhas_testes = []
    for slug, ex in exs.items():
        faltam = importados_pelos_testes(ex) - definidos(ex["esqueleto"])
        if faltam:
            tipos = []
            for nome in sorted(faltam):
                ref = classes(ex["solucao_referencia"])
                tipos.append(f"{nome} ({'classe' if nome in ref else 'outro'})")
            linhas_testes.append({"exercício": slug, "exigido pelos testes e ausente do esqueleto": ", ".join(tipos)})

    # 2) cada classe nova nas soluções aceitas
    par = T.ler("paradigmas")
    ac = T.ler("analise")
    ac = ac[ac["aceita"]][["fonte", "slug", "tentativa"]]
    par = par.merge(ac, on=["fonte", "slug", "tentativa"])
    par = par[par["classes_novas"].notna() & (par["classes_novas"] != "")]
    linhas, trechos = [], []
    for r in par.itertuples():
        ex = exs[r.slug]
        if r.fonte == "referencia":
            codigo = ex["solucao_referencia"]
        else:
            codigo = (T.CODIGOS / r.fonte / r.slug / f"t{r.tentativa}" / ex["arquivo_solucao"]).read_text(encoding="utf-8")
        cls = classes(codigo)
        exigidos = importados_pelos_testes(ex)
        for nome in r.classes_novas.split(", "):
            bases = [ast.unparse(b) for b in cls[nome].bases] if nome in cls else []
            citacoes = [l.strip() for l in ex["enunciado"].splitlines()
                        if re.search(rf"\b{re.escape(nome)}\b", l)]
            linhas.append({"fonte": r.fonte, "exercício": r.slug, "rótulo": r.rotulo_d, "classe nova": nome,
                           "herda de": ", ".join(bases) or "–",
                           "exigida pelos testes": "sim" if nome in exigidos else "não",
                           "exceção": "sim" if any(re.search("Exception|Error", b) for b in bases) else "não",
                           "nome citado no enunciado": "sim" if citacoes else "não"})
        gerais = [l.strip() for l in ex["enunciado"].splitlines() if re.search(r"\bclass(es)?\b|iterator", l, re.I)]
        if gerais:
            trechos.append(f"**{r.fonte} / {r.slug}**\n\n" + "\n".join(f"> {l}" for l in gerais))

    texto = f"""# Verificação: classes novas exigidas pelo exercício?

Gerado em {datetime.now():%Y-%m-%d %H:%M} por `src/verificacao/verificar_classes_exigidas.py`.

## 1. O que os testes exigem além do esqueleto (todos os {len(exs)} exercícios)

{T.tabela_md(pd.DataFrame(linhas_testes)) if linhas_testes else "Nada: em todos os exercícios, os testes só usam nomes definidos no esqueleto."}

## 2. Classes novas nas soluções aceitas

{T.tabela_md(pd.DataFrame(linhas)) if linhas else "Nenhuma solução aceita cria classes novas."}

## 3. Trechos do enunciado que falam de classes ou iteradores (para leitura manual)

{chr(10).join(trechos) if trechos else "Nenhum."}
"""
    T.RELATORIOS.mkdir(parents=True, exist_ok=True)
    (T.RELATORIOS / "classes_exigidas.md").write_text(texto, encoding="utf-8")
    print(texto)


if __name__ == "__main__":
    main()
