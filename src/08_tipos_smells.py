"""Etapa 8: agrupa os avisos do Pylint por TIPO de smell e gera tabelas para leitura manual.

Cada símbolo do Pylint é atribuído a um tipo (src/catalogo_smells.py). As tabelas mostram
quantos avisos de cada tipo e de cada símbolo cada fonte tem, e listam cada ocorrência com a
linha de código apontada, para julgar se o smell é válido.

Escopo (o mesmo da análise principal): só tentativas aceitas e sem os avisos herdados do
esqueleto (se config/analise.yaml mandar excluí-los). Os resumos usam só os exercícios com
solução aceita em TODAS as fontes, para comparar o mesmo conjunto de problemas; as listas de
ocorrências trazem todas as soluções aceitas, com a coluna `comparavel` marcando esse conjunto.

Testes: Wilcoxon pareado na densidade por solução (avisos do tipo / 100 sloc), para cada par de
fontes; correção de Holm sobre todos os testes da tabela (tipos × pares).

Saídas em relatorios/smells_por_tipo/:
    smells_por_tipo.xlsx      todas as tabelas, uma por aba
    catalogo.csv              símbolo → tipo, categoria do Pylint e descrição
    resumo_por_tipo.csv       tipo × fonte: avisos, soluções afetadas, avisos/100 sloc
    testes_por_tipo.csv       tipo × par de fontes: Wilcoxon, r, p de Holm
    por_simbolo.csv           tipo, símbolo e contagem por fonte
    ocorrencias_<fonte>.csv   um aviso por linha, com a linha de código

Uso (a partir da raiz do projeto, com o .venv ativado), depois da etapa 2:
    python src/08_tipos_smells.py
"""
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402
from catalogo_smells import DESCRICAO, ORDEM_TIPOS, TIPO_DE, TIPOS  # noqa: E402

SAIDA = T.RELATORIOS / "smells_por_tipo"

APELIDO = {"referencia": "humano"}


def apelido(fonte):
    return APELIDO.get(fonte, fonte)


# ------------------------------------------------------------------ estatística
def wilcoxon_pareado(x, y):
    """Wilcoxon (y − x) sem os empates em zero, como na etapa 6. Devolve n, p e a correlação
    rank-bisserial pareada (positiva = y maior). Com menos de 5 diferenças não nulas, p = NaN."""
    d = (pd.Series(y, dtype=float) - pd.Series(x, dtype=float)).dropna()
    nz = d[d != 0]
    if len(nz) < 5:
        return len(nz), np.nan, np.nan
    postos = stats.rankdata(nz.abs())
    r = (postos[nz > 0].sum() - postos[nz < 0].sum()) / postos.sum()
    return len(nz), stats.wilcoxon(nz).pvalue, r


def holm(pvalores):
    p = np.asarray(pvalores, float)
    ok = ~np.isnan(p)
    saida = np.full_like(p, np.nan)
    idx = np.where(ok)[0][np.argsort(p[ok])]
    m, acumulado = len(idx), 0.0
    for i, j in enumerate(idx):
        acumulado = max(acumulado, min(1.0, (m - i) * p[j]))
        saida[j] = acumulado
    return saida


# ------------------------------------------------------------------ dados
def carregar(fontes, excluir_herdados):
    sol = T.ler("solucoes", fontes)
    av = T.ler("avisos", fontes)
    sol = sol[sol["aceita"]]
    av = av.merge(sol[T.CHAVE], on=T.CHAVE)
    if excluir_herdados:
        av = av[~av["herdado_esqueleto"]]
    sem_tipo = sorted(set(av["simbolo"]) - set(TIPO_DE))
    if sem_tipo:
        sys.exit(f"Símbolos sem tipo em TIPOS: {', '.join(sem_tipo)}. Inclua-os no dicionário.")
    av = av.assign(tipo=av["simbolo"].map(TIPO_DE))
    n_fontes = sol.groupby("slug")["fonte"].nunique()
    comuns = set(n_fontes[n_fontes == len(fontes)].index)
    return sol, av, comuns


def linha_de_codigo(fonte, slug, tentativa, linha, arquivos, cache):
    caminho = T.CODIGOS / fonte / slug / f"t{tentativa}" / arquivos[slug]
    if caminho not in cache:
        cache[caminho] = caminho.read_text(encoding="utf-8").splitlines() if caminho.exists() else []
    linhas = cache[caminho]
    if not 1 <= linha <= len(linhas):
        return "", caminho
    return linhas[linha - 1], caminho


# ------------------------------------------------------------------ tabelas
def catalogo(av):
    presentes = set(av["simbolo"])
    categoria = av.drop_duplicates("simbolo").set_index("simbolo")["categoria"]
    return pd.DataFrame([{"tipo": t, "simbolo": s, "categoria_pylint": categoria.get(s, ""),
                          "descricao": DESCRICAO[s], "aparece_nos_dados": s in presentes}
                         for t in ORDEM_TIPOS for s in TIPOS[t]])


def resumo(sol, av, fontes):
    sloc = sol.groupby("fonte")["sloc"].sum()
    n_sol = sol.groupby("fonte").size()
    linhas = []
    for tipo in [*ORDEM_TIPOS, "TOTAL"]:
        a = av if tipo == "TOTAL" else av[av["tipo"] == tipo]
        linha = {"tipo": tipo}
        for f in fontes:
            x = a[a["fonte"] == f]
            linha[f"{apelido(f)} avisos"] = len(x)
            linha[f"{apelido(f)} soluções com o tipo"] = x["slug"].nunique()
            linha[f"{apelido(f)} % soluções"] = round(100 * x["slug"].nunique() / n_sol[f], 1)
            linha[f"{apelido(f)} avisos/100 sloc"] = round(100 * len(x) / sloc[f], 2)
        linhas.append(linha)
    return pd.DataFrame(linhas)


def testes(sol, av, fontes):
    densidade = {}
    sloc = sol.set_index(["fonte", "slug"])["sloc"]
    for tipo in ORDEM_TIPOS:
        n = av[av["tipo"] == tipo].groupby(["fonte", "slug"]).size().reindex(sloc.index, fill_value=0)
        densidade[tipo] = (100 * n / sloc).unstack("fonte")
    linhas = []
    for tipo in ORDEM_TIPOS:
        d = densidade[tipo]
        for a, b in combinations(fontes, 2):  # comparação "b × a": b é o 1º, a é o 2º
            n, p, r = wilcoxon_pareado(d[a], d[b])
            linhas.append({"tipo": tipo, "comparação": f"{apelido(b)} × {apelido(a)}",
                           "média densidade (1º)": round(d[b].mean(), 3),
                           "média densidade (2º)": round(d[a].mean(), 3),
                           "1º maior em": int((d[b] > d[a]).sum()), "2º maior em": int((d[a] > d[b]).sum()),
                           "pares sem empate": n, "p": p, "r (positivo = 1º maior)": r})
    t = pd.DataFrame(linhas)
    t["p Holm"] = holm(t["p"])
    t["significativo (Holm < 0,05)"] = t["p Holm"] < 0.05
    return t


def por_simbolo(av, fontes):
    t = (av.groupby(["tipo", "simbolo", "fonte"]).agg(avisos=("slug", "size"), solucoes=("slug", "nunique"))
         .unstack("fonte", fill_value=0))
    saida = pd.DataFrame(index=t.index)
    for f in fontes:
        saida[f"{apelido(f)} avisos"] = t["avisos"].get(f, 0)
        saida[f"{apelido(f)} soluções"] = t["solucoes"].get(f, 0)
    saida = saida.reset_index()
    saida.insert(2, "descricao", saida["simbolo"].map(DESCRICAO))
    saida["_ordem"] = saida["tipo"].map(ORDEM_TIPOS.index)
    saida["_total"] = saida[[f"{apelido(f)} avisos" for f in fontes]].sum(axis=1)
    return saida.sort_values(["_ordem", "_total"], ascending=[True, False]).drop(columns=["_ordem", "_total"])


def ocorrencias(av, fonte, comuns, arquivos):
    cache, linhas = {}, []
    for _, a in av[av["fonte"] == fonte].iterrows():
        codigo, caminho = linha_de_codigo(fonte, a["slug"], a["tentativa"], int(a["linha"]), arquivos, cache)
        linhas.append({"tipo": a["tipo"], "simbolo": a["simbolo"], "slug": a["slug"], "tentativa": a["tentativa"],
                       "linha": a["linha"], "codigo_da_linha": codigo,
                       "linha_e_comentario": codigo.strip().startswith("#"),
                       "linha_em_branco": codigo.strip() == "", "mensagem": a["mensagem"],
                       "categoria_pylint": a["categoria"], "comparavel": a["slug"] in comuns,
                       "arquivo": caminho.relative_to(T.RAIZ).as_posix()})
    df = pd.DataFrame(linhas)
    if df.empty:
        return df
    df["_ordem"] = df["tipo"].map(ORDEM_TIPOS.index)
    return df.sort_values(["_ordem", "simbolo", "slug", "linha"]).drop(columns="_ordem")


# ------------------------------------------------------------------ excel
def gravar_excel(abas, caminho):
    with pd.ExcelWriter(caminho, engine="openpyxl") as w:
        for nome, df in abas.items():
            df.to_excel(w, sheet_name=nome[:31], index=False)
            ws = w.sheets[nome[:31]]
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for col in ws.columns:
                largura = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(max(10, largura + 2), 70)


def main():
    cfg = T.analise()
    fontes = T.resolver_fontes(sys.argv[1:])
    excluir = cfg["smells"]["excluir_herdados_do_esqueleto"]
    sol, av, comuns = carregar(fontes, excluir)
    arquivos = {ex["slug"]: ex["arquivo_solucao"] for ex in T.exercicios()}

    sol_c, av_c = sol[sol["slug"].isin(comuns)], av[av["slug"].isin(comuns)]
    tabelas = {
        "resumo por tipo": resumo(sol_c, av_c, fontes),
        "testes por tipo": testes(sol_c, av_c, fontes),
        "por símbolo": por_simbolo(av_c, fontes),
        "catálogo": catalogo(av),
    }
    oc = {f: ocorrencias(av, f, comuns, arquivos) for f in fontes}

    SAIDA.mkdir(parents=True, exist_ok=True)
    nomes_csv = {"resumo por tipo": "resumo_por_tipo", "testes por tipo": "testes_por_tipo",
                 "por símbolo": "por_simbolo", "catálogo": "catalogo"}
    for nome, df in tabelas.items():
        df.to_csv(SAIDA / f"{nomes_csv[nome]}.csv", index=False, encoding="utf-8-sig")
    for f, df in oc.items():
        df.to_csv(SAIDA / f"ocorrencias_{apelido(f)}.csv", index=False, encoding="utf-8-sig")
    gravar_excel({**tabelas, **{f"ocorrências {apelido(f)}": df for f, df in oc.items()}},
                 SAIDA / "smells_por_tipo.xlsx")

    print(f"Fontes: {', '.join(fontes)} · herdados do esqueleto {'fora' if excluir else 'dentro'}")
    print(f"Exercícios com solução aceita em todas as fontes (resumos e testes): {len(comuns)}")
    for f in fontes:
        print(f"[{apelido(f)}] avisos: {len(oc[f])} ({int(oc[f]['comparavel'].sum()) if len(oc[f]) else 0} "
              f"nos exercícios comparáveis)")
    t = tabelas["testes por tipo"]
    sig = t[t["significativo (Holm < 0,05)"]]
    print("Diferenças significativas após Holm:" if len(sig) else "Nenhuma diferença significativa após Holm.")
    for _, r in sig.iterrows():
        print(f"  {r['tipo']}: {r['comparação']} · p Holm = {r['p Holm']:.4f} · r = {r['r (positivo = 1º maior)']:.2f}")
    print(f"\nArquivos em {SAIDA.relative_to(T.RAIZ).as_posix()}/")


if __name__ == "__main__":
    main()
