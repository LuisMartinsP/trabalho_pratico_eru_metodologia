"""Etapa 5: junta smells e paradigmas nas tabelas de análise.

Entradas (conferidas no manifesto; se estiverem desatualizadas, o script para e diz o que rodar):
    dados/exercism.jsonl           (etapa 1)
    dados/tabelas/solucoes.csv     (etapa 2)
    dados/tabelas/avisos.csv       (etapa 2)
    dados/tabelas/paradigmas.csv   (etapa 4; precisa ter sido gerada com o min_pontos atual)

Saídas:
    dados/tabelas/exercicios.csv   uma linha por exercício: dificuldade, tipo e tamanho do esqueleto
    dados/tabelas/analise.csv      uma linha por tentativa: smells (contagens e densidade) + paradigma
    dados/tabelas/pareado.csv      uma linha por exercício × modelo: humano e modelo lado a lado,
                                   só com as tentativas aceitas dos dois

Definições (config/analise.yaml):
    n_avisos      avisos usados na análise: só os próprios da solução se
                  excluir_herdados_do_esqueleto = true; todos, se false
    densidade     100 × n_avisos / sloc
    paradigma     rótulo filtrado da regra oficial (com "indeterminado" abaixo de min_pontos)
    frac_funcional  pontos funcionais / (funcionais + procedurais) da regra oficial; vazio se 0 pontos
    paradigma_c   rótulo filtrado da outra regra (C), para a análise de sensibilidade
    comparavel    humano e modelo têm rótulo determinado (oo, funcional, procedural ou misto);
                  só esses pares entram na comparação de paradigma

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/05_consolidar.py                       # fontes de config/analise.yaml
    python src/05_consolidar.py referencia gpt-mini
"""
import argparse
import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from radon.raw import analyze

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402

CATEGORIAS = ["convention", "refactor", "warning", "error"]
DETERMINADOS = ["oo", "funcional", "procedural", "misto"]


def parametros_esperados():
    """Parâmetros com que as tabelas das etapas 2 e 4 precisam ter sido geradas."""
    cfg = T.analise()
    para = importlib.import_module("04_paradigma")
    pylint = {"pylintrc": T.hash_arquivos(T.PYLINTRC), "exercism_commit": T.commit_exercism()}
    paradigma = {"min_pontos": cfg["paradigma"]["min_pontos"],
                 "classificadores": T.hash_arquivos(*para.CLASSIFICADORES),
                 "exercism_commit": T.commit_exercism()}
    return cfg, pylint, paradigma


def tabela_exercicios(exercicios):
    return pd.DataFrame([{"slug": e["slug"], "dificuldade": e["dificuldade"], "tipo_esqueleto": e["tipo_esqueleto"],
                          "sloc_esqueleto": analyze(e["esqueleto"]).sloc} for e in exercicios])


def tabela_analise(sol, av, par, exs, cfg):
    regra = cfg["paradigma"]["regra_oficial"]
    outra = "c" if regra == "d" else "d"
    excluir = cfg["smells"]["excluir_herdados_do_esqueleto"]

    chave = ["fonte", "slug", "tentativa"]
    cont = av.groupby(chave).agg(n_avisos_todos=("simbolo", "size"),
                                 n_herdados=("herdado_esqueleto", "sum")).reset_index()
    usados = av[~av["herdado_esqueleto"]] if excluir else av
    por_cat = (usados.groupby(chave + ["categoria"]).size().unstack(fill_value=0)
               .reindex(columns=CATEGORIAS, fill_value=0).reset_index())

    d = (sol.merge(exs, on="slug", how="left")
         .merge(cont, on=chave, how="left").merge(por_cat, on=chave, how="left"))
    for c in ["n_avisos_todos", "n_herdados", *CATEGORIAS]:
        d[c] = d[c].fillna(0).astype(int)
    d["n_avisos_proprios"] = d["n_avisos_todos"] - d["n_herdados"]
    d["n_avisos"] = d["n_avisos_proprios"] if excluir else d["n_avisos_todos"]
    d["densidade"] = np.where(d["sloc"] > 0, 100 * d["n_avisos"] / d["sloc"].where(d["sloc"] > 0), np.nan)
    d["grupo_esqueleto"] = np.where(d["tipo_esqueleto"] == "funcao", "funcao", "classe")

    p = par.rename(columns={f"filtrado_{regra}": "paradigma", f"rotulo_{regra}": "paradigma_sem_filtro",
                            f"pontos_func_{regra}": "pontos_func", f"pontos_proc_{regra}": "pontos_proc",
                            f"total_pontos_{regra}": "total_pontos", f"filtrado_{outra}": f"paradigma_{outra}"})
    p["frac_funcional"] = np.where(p["total_pontos"] > 0, p["pontos_func"] / p["total_pontos"].where(p["total_pontos"] > 0),
                                   np.nan)
    d = d.merge(p[chave + ["paradigma", "paradigma_sem_filtro", f"paradigma_{outra}", "pontos_func", "pontos_proc",
                           "total_pontos", "frac_funcional", "classes_novas", "rotulo_dyer_original"]],
                on=chave, how="left")
    colunas = ["fonte", "slug", "tentativa", "status", "aceita", "ultima", "tem_codigo", "erro_sintaxe",
               "dificuldade", "tipo_esqueleto", "grupo_esqueleto", "sloc_esqueleto", "sloc",
               "n_avisos", "n_avisos_todos", "n_avisos_proprios", "n_herdados", *CATEGORIAS, "densidade",
               "paradigma", "paradigma_sem_filtro", f"paradigma_{outra}", "pontos_func", "pontos_proc",
               "total_pontos", "frac_funcional", "classes_novas", "rotulo_dyer_original"]
    return d[colunas], outra


def tabela_pareada(analise, modelos, outra):
    ac = analise[analise["aceita"]]
    h = ac[ac["fonte"] == "referencia"].set_index("slug")
    lado = ["sloc", "n_avisos", "n_avisos_todos", "densidade", *CATEGORIAS, "paradigma", "paradigma_sem_filtro",
            f"paradigma_{outra}", "total_pontos", "frac_funcional", "tentativa"]
    blocos = []
    for modelo in modelos:
        m = ac[ac["fonte"] == modelo].set_index("slug")
        comuns = h.index.intersection(m.index)
        b = pd.DataFrame({"modelo": modelo, "slug": comuns})
        for c in ["dificuldade", "tipo_esqueleto", "grupo_esqueleto"]:
            b[c] = h.loc[comuns, c].values
        for c in lado:
            b[f"humano_{c}"] = h.loc[comuns, c].values
            b[f"modelo_{c}"] = m.loc[comuns, c].values
        b = b.drop(columns=["humano_tentativa"]).rename(columns={"modelo_tentativa": "modelo_tentativa_aceita"})
        b["dif_sloc"] = b["modelo_sloc"] - b["humano_sloc"]
        b["dif_densidade"] = b["modelo_densidade"] - b["humano_densidade"]
        b["dif_frac_funcional"] = b["modelo_frac_funcional"] - b["humano_frac_funcional"]
        for suf, col in (("", "paradigma"), (f"_{outra}", f"paradigma_{outra}")):
            comp = b[f"humano_{col}"].isin(DETERMINADOS) & b[f"modelo_{col}"].isin(DETERMINADOS)
            b[f"comparavel{suf}"] = comp
            b[f"mesmo_paradigma{suf}"] = np.where(comp, b[f"humano_{col}"] == b[f"modelo_{col}"], None)
        blocos.append(b)
    return pd.concat(blocos, ignore_index=True) if blocos else pd.DataFrame()


def main():
    parser = argparse.ArgumentParser(description="Junta smells e paradigmas nas tabelas de análise.")
    parser.add_argument("fontes", nargs="*", help="referencia e modelos (sem argumentos: config/analise.yaml)")
    args = parser.parse_args()
    fontes = T.resolver_fontes(args.fontes)
    if "referencia" not in fontes:
        sys.exit("A consolidação precisa da fonte 'referencia' (linha de base humana).")
    modelos = [f for f in fontes if f != "referencia"]

    cfg, exige_pylint, exige_paradigma = parametros_esperados()
    sol = T.ler("solucoes", fontes, exige_pylint)
    av = T.ler("avisos", fontes, exige_pylint)
    par = T.ler("paradigmas", fontes, exige_paradigma)
    exercicios = T.exercicios()

    exs = T.salvar("exercicios", tabela_exercicios(exercicios), "05_consolidar.py",
                   parametros={"exercism_commit": T.commit_exercism()})
    analise, outra = tabela_analise(sol, av, par, exs, cfg)
    snapshot = {"fontes": fontes, "config": cfg}
    T.salvar("analise", analise, "05_consolidar.py", fontes, snapshot, substituir=False)
    pareado = tabela_pareada(analise, modelos, outra)
    if len(pareado):
        T.salvar("pareado", pareado, "05_consolidar.py", modelos, snapshot, substituir=False)

    ac = analise[analise["aceita"]]
    for f in fontes:
        a = ac[ac["fonte"] == f]
        print(f"[{f}] aceitas: {len(a)} · avisos usados: {int(a['n_avisos'].sum())} "
              f"(herdados fora: {cfg['smells']['excluir_herdados_do_esqueleto']}) · "
              f"paradigma determinado: {int(a['paradigma'].isin(DETERMINADOS).sum())}")
    for mdl in modelos:
        p = pareado[pareado["modelo"] == mdl]
        print(f"[referencia × {mdl}] pares: {len(p)} · comparáveis no paradigma: {int(p['comparavel'].sum())}")
    print(f"\nTabelas em {T.TABELAS}")


if __name__ == "__main__":
    main()
