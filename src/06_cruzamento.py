"""Etapa 6: cruza paradigmas e smells e gera relatorios/resultados.md.

Entradas: dados/tabelas/analise.csv e pareado.csv (etapa 5). Unidade de comparação: o
EXERCÍCIO, com a solução humana e a do modelo lado a lado (só tentativas aceitas dos dois).
Todas as associações são observacionais: o paradigma não foi sorteado.

Perguntas e testes (mesma numeração do artigo):
    QP1  O modelo escolhe outro paradigma que o humano para o mesmo exercício? E os modelos
         escolhem o mesmo paradigma entre si?
         - distribuição dos rótulos (com "indeterminado" abaixo de min_pontos)
         - matriz humano × modelo nos pares comparáveis (os dois com rótulo determinado)
         - McNemar exato: proporção de soluções procedurais, humano × modelo
         - Wilcoxon pareado na fração funcional (pares com pontos suficientes nos dois)
         - sensibilidade: a mesma análise com a regra C e sem o filtro de pontos
         - concordância de paradigma entre os modelos e entropia dos rótulos por fonte
    QP2  Os smells diferem? Em quantidade e em tipo?
         - Wilcoxon pareado na densidade (avisos próprios por 100 sloc); efeito: correlação
           rank-bisserial pareada
         - sensibilidade: com os avisos de estilo ignorados e com os herdados do esqueleto
         - perfil: avisos por categoria e por símbolo, lado a lado
         - por tipo de smell (src/catalogo_smells.py): Wilcoxon pareado por tipo, correção de Holm
           sobre todos os testes por tipo (tipos × pares de fontes)
    QP3  Os modelos diferem entre si em correção funcional e em smells?
         - acerto na 1ª tentativa e no final, McNemar exato nos exercícios pareados
         - densidade e tipos de smell, Wilcoxon pareado (mesma família de Holm da QP2)
    QP4  (exploratória) A diferença de smells acompanha a divergência de paradigma ou a dificuldade?
         - diferença de densidade nos pares que divergiram × nos que concordaram
           (Mann-Whitney e delta de Cliff)
         - Spearman entre a diferença de fração funcional e a diferença de densidade
         - Spearman entre a dificuldade do exercício e a diferença de densidade
    Secundária: 1ª tentativa × tentativa aceita nos exercícios corrigidos pelo modelo, e a
    trajetória dos smells tentativa a tentativa.

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/06_cruzamento.py
"""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402
from catalogo_smells import ORDEM_TIPOS, TIPO_DE  # noqa: E402

CATEGORIAS = ["convention", "refactor", "warning", "error"]
ORDEM = ["oo", "funcional", "procedural", "misto", "neutro", "indeterminado"]
DETERMINADOS = ["oo", "funcional", "procedural", "misto"]
FAIXAS = [(1, 2, "1–2 (fácil)"), (3, 5, "3–5 (média)"), (6, 10, "6–10 (difícil)")]


def apelido(fonte):
    return "humano" if fonte == "referencia" else fonte


# ------------------------------------------------------------------ estatística
def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - meia, centro + meia


def pct_ic(k, n):
    lo, hi = wilson(k, n)
    return "–" if n == 0 else f"{100 * k / n:.0f}% [{100 * lo:.0f}–{100 * hi:.0f}]"


def fmt_p(p):
    return "–" if p is None or pd.isna(p) else "<0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def fmt(v, casas=2):
    return "–" if v is None or pd.isna(v) else f"{v:.{casas}f}".replace(".", ",")


def wilcoxon_pareado(x, y):
    """Wilcoxon (y − x), sem os empates em zero. Devolve n usados, mediana da diferença, p e
    a correlação rank-bisserial pareada (−1 a 1; positiva = y maior)."""
    d = (pd.Series(y).astype(float) - pd.Series(x).astype(float)).dropna()
    nz = d[d != 0]
    if len(nz) < 5:
        return {"n_pares": len(d), "n_sem_empate": len(nz), "mediana_dif": d.median(), "p": np.nan, "r": np.nan}
    p = stats.wilcoxon(nz).pvalue
    postos = stats.rankdata(nz.abs())
    r = (postos[nz > 0].sum() - postos[nz < 0].sum()) / postos.sum()
    return {"n_pares": len(d), "n_sem_empate": len(nz), "mediana_dif": d.median(), "p": p, "r": r}


def cliff(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) == 0 or len(b) == 0:
        return np.nan
    return ((a[:, None] > b[None, :]).sum() - (a[:, None] < b[None, :]).sum()) / (len(a) * len(b))


def magnitude(d):
    if pd.isna(d):
        return "–"
    d = abs(d)
    return "desprezível" if d < 0.147 else "pequeno" if d < 0.33 else "médio" if d < 0.474 else "grande"


def mcnemar(h, m):
    """McNemar exato para um evento binário pareado (h = humano, m = modelo)."""
    b = int((h & ~m).sum())  # só o humano
    c = int((~h & m).sum())  # só o modelo
    p = stats.binomtest(b, b + c, 0.5).pvalue if b + c else np.nan
    return b, c, p


def holm(pvalores):
    """Correção de Holm; ignora os NaN (testes sem dados suficientes)."""
    p = np.asarray(pvalores, float)
    saida = np.full_like(p, np.nan)
    validos = np.where(~np.isnan(p))[0]
    ordem = validos[np.argsort(p[validos])]
    acumulado = 0.0
    for i, j in enumerate(ordem):
        acumulado = max(acumulado, min(1.0, (len(ordem) - i) * p[j]))
        saida[j] = acumulado
    return saida


def entropia(rotulos):
    p = pd.Series(rotulos).value_counts(normalize=True)
    return float(-(p * np.log2(p)).sum()) if len(p) else np.nan


def avisos_usados(avisos, cfg):
    """Avisos da análise principal: sem herdados do esqueleto (se excluídos) e sem os ignorados."""
    a = avisos[~avisos["herdado_esqueleto"]] if cfg["smells"]["excluir_herdados_do_esqueleto"] else avisos
    return a[~a["simbolo"].isin(cfg["smells"].get("simbolos_ignorados") or [])]


def aceitas_em_todas(analise):
    """Tentativas aceitas dos exercícios aceitos em todas as fontes (uma por fonte × exercício)."""
    ac = analise[analise["aceita"]]
    n = ac.groupby("slug")["fonte"].nunique()
    return ac[ac["slug"].isin(n[n == analise["fonte"].nunique()].index)]


# ------------------------------------------------------------------ seções
def secao_dados(analise, cfg, modelos):
    ult = analise[(analise["fonte"] != "referencia") & analise["ultima"]]
    linhas = []
    for mdl in modelos:
        u = ult[ult["fonte"] == mdl]
        n = len(u)
        p1 = int((u["aceita"] & (u["tentativa"] == 1)).sum())
        pc = int((u["aceita"] & (u["tentativa"] > 1)).sum())
        linhas.append({"modelo": mdl, "exercícios tentados": n, "passou na 1ª": p1, "passou com correção": pc,
                       "falhou": n - p1 - pc, "acerto final": pct_ic(p1 + pc, n)})
    p = cfg["paradigma"]
    return f"""## 0. Dados e parâmetros

- Regra de paradigma oficial: **{p['regra_oficial'].upper()}**; mínimo de pontos para rótulo
  determinado: **{p['min_pontos']}**.
- Avisos herdados do esqueleto: **{'excluídos' if cfg['smells']['excluir_herdados_do_esqueleto'] else 'incluídos'}**
  na análise principal.
- Avisos de estilo ignorados na análise principal (Siddiq et al., 2022): {', '.join(f'`{x}`' for x in cfg['smells'].get('simbolos_ignorados') or []) or 'nenhum'}.
  Entram na análise de sensibilidade da QP2.
- Intervalos entre colchetes: IC de 95% de Wilson.

{T.tabela_md(pd.DataFrame(linhas)) if linhas else ""}
"""


def secao_descritivo(analise, pareado):
    comuns = set(pareado["slug"])
    ac = analise[analise["aceita"] & analise["slug"].isin(comuns)]
    linhas = []
    for f, g in ac.groupby("fonte", sort=False):
        sl = g["sloc"].sum()
        linhas.append({"fonte": f, "soluções": len(g), "sloc (soma)": int(sl), "sloc (mediana)": g["sloc"].median(),
                       "avisos": int(g["n_avisos"].sum()), "herdados (fora)": int(g["n_herdados"].sum()),
                       "de estilo (fora)": int(g["n_ignorados"].sum()),
                       "avisos/100 sloc": 100 * g["n_avisos"].sum() / sl, "densidade mediana": g["densidade"].median(),
                       "sem aviso": pct_ic(int((g["n_avisos"] == 0).sum()), len(g)),
                       **{c: int(g[c].sum()) for c in CATEGORIAS}})
    grupo = (ac.groupby(["grupo_esqueleto", "fonte"])
             .apply(lambda g: pd.Series({"soluções": len(g), "avisos/100 sloc": 100 * g["n_avisos"].sum() / g["sloc"].sum()}),
                    include_groups=False).reset_index())
    return f"""## 1. Descritivo dos smells

Só os {len(comuns)} exercícios com solução aceita nas duas fontes. "avisos" são os usados na
análise (sem os herdados do esqueleto, se excluídos, e sem os avisos de estilo ignorados).

{T.tabela_md(pd.DataFrame(linhas))}

Por tipo de esqueleto ("classe" inclui os esqueletos com classe e funções):

{T.tabela_md(grupo)}
"""


def secao_simbolos(analise, avisos, pareado, cfg):
    comuns = set(pareado["slug"])
    ac = analise[analise["aceita"] & analise["slug"].isin(comuns)][["fonte", "slug", "tentativa"]]
    a = avisos_usados(avisos, cfg).merge(ac, on=["fonte", "slug", "tentativa"])
    t = a.groupby(["simbolo", "categoria", "fonte"]).agg(avisos=("slug", "size"), soluções=("slug", "nunique"))
    t = t.unstack("fonte", fill_value=0)
    t.columns = [f"{f} ({m})" for m, f in t.columns]
    t = t[sorted(t.columns, key=lambda c: (c.split(" (")[0] != "referencia", c))]
    t = t.assign(_t=t[[c for c in t.columns if "(avisos)" in c]].sum(axis=1)).sort_values("_t", ascending=False)
    t = t.drop(columns="_t").reset_index()
    return f"""### Avisos por símbolo

{T.tabela_md(t)}
"""


def secao_qp1(pareado, cfg, outra):
    blocos = []
    for mdl, p in pareado.groupby("modelo", sort=False):
        dist = pd.DataFrame({"humano": p["humano_paradigma"].value_counts(), mdl: p["modelo_paradigma"].value_counts()}
                            ).reindex(ORDEM).fillna(0).astype(int)
        dist.insert(0, "paradigma", dist.index)
        comp = p[p["comparavel"]]
        mat = pd.crosstab(comp["humano_paradigma"], comp["modelo_paradigma"]).reindex(
            index=DETERMINADOS, columns=DETERMINADOS, fill_value=0)
        mat.insert(0, f"humano \\ {mdl}", mat.index)

        def teste(col_h, col_m, mascara):
            q = p[mascara]
            h, m = q[col_h] == "procedural", q[col_m] == "procedural"
            b, c, pv = mcnemar(h, m)
            return {"pares": len(q), "procedural humano": pct_ic(int(h.sum()), len(q)),
                    f"procedural {mdl}": pct_ic(int(m.sum()), len(q)), "só humano": b, f"só {mdl}": c,
                    "McNemar p": fmt_p(pv)}
        sens = pd.DataFrame([
            {"regra": f"{cfg['paradigma']['regra_oficial'].upper()} (oficial), filtrada",
             **teste("humano_paradigma", "modelo_paradigma", p["comparavel"])},
            {"regra": f"{outra.upper()}, filtrada",
             **teste(f"humano_paradigma_{outra}", f"modelo_paradigma_{outra}", p[f"comparavel_{outra}"])},
            {"regra": f"{cfg['paradigma']['regra_oficial'].upper()}, sem filtro",
             **teste("humano_paradigma_sem_filtro", "modelo_paradigma_sem_filtro",
                     p["humano_paradigma_sem_filtro"].isin(DETERMINADOS) & p["modelo_paradigma_sem_filtro"].isin(DETERMINADOS))},
        ])
        minp = cfg["paradigma"]["min_pontos"]
        suf = (p["humano_total_pontos"] >= minp) & (p["modelo_total_pontos"] >= minp)
        w = wilcoxon_pareado(p.loc[suf, "humano_frac_funcional"], p.loc[suf, "modelo_frac_funcional"])
        grupos = []
        for g, q in p[p["comparavel"]].groupby("grupo_esqueleto"):
            grupos.append({"esqueleto": g, "pares": len(q),
                           "procedural humano": pct_ic(int((q["humano_paradigma"] == "procedural").sum()), len(q)),
                           f"procedural {mdl}": pct_ic(int((q["modelo_paradigma"] == "procedural").sum()), len(q))})
        iguais = int((comp["humano_paradigma"] == comp["modelo_paradigma"]).sum())
        blocos.append(f"""### Humano × {mdl}

Distribuição dos rótulos nos {len(p)} exercícios pareados:

{T.tabela_md(dist)}

Pares comparáveis (os dois com rótulo determinado): **{len(comp)}** · mesmo paradigma:
**{pct_ic(iguais, len(comp))}**. Linhas: humano; colunas: {mdl}.

{T.tabela_md(mat)}

Proporção de soluções procedurais (McNemar exato nos pares discordantes) e sensibilidade
à regra e ao filtro:

{T.tabela_md(sens)}

Fração funcional, pares com pelo menos {minp} pontos nos dois (Wilcoxon pareado, {mdl} − humano):
n = {w['n_pares']} ({w['n_sem_empate']} sem empate) · mediana da diferença = {fmt(w['mediana_dif'])} ·
p = {fmt_p(w['p'])} · r rank-bisserial = {fmt(w['r'])}.

Por tipo de esqueleto (pares comparáveis):

{T.tabela_md(pd.DataFrame(grupos))}
""")
    return "## 2. QP1: escolha de paradigma\n\n" + "\n".join(blocos)


def secao_qp2(pareado):
    blocos = []
    for mdl, p in pareado.groupby("modelo", sort=False):
        q = p[(p["humano_sloc"] > 0) & (p["modelo_sloc"] > 0)].copy()
        q["humano_dens_todos"] = 100 * q["humano_n_avisos_todos"] / q["humano_sloc"]
        q["modelo_dens_todos"] = 100 * q["modelo_n_avisos_todos"] / q["modelo_sloc"]
        linhas = []
        for nome, h, m in (("densidade (avisos usados / 100 sloc)", "humano_densidade", "modelo_densidade"),
                           ("densidade com os avisos de estilo (sensibilidade)", "humano_densidade_com_estilo",
                            "modelo_densidade_com_estilo"),
                           ("densidade com todos os avisos, inclusive herdados (sensibilidade)",
                            "humano_dens_todos", "modelo_dens_todos"),
                           ("nº de avisos usados", "humano_n_avisos", "modelo_n_avisos"),
                           ("sloc", "humano_sloc", "modelo_sloc")):
            w = wilcoxon_pareado(q[h], q[m])
            dif = q[m] - q[h]
            linhas.append({"medida": nome, "pares": w["n_pares"], f"{mdl} maior": int((dif > 0).sum()),
                           "empate": int((dif == 0).sum()), "humano maior": int((dif < 0).sum()),
                           "mediana humano": fmt(q[h].median()), f"mediana {mdl}": fmt(q[m].median()),
                           "Wilcoxon p": fmt_p(w["p"]), "r": fmt(w["r"])})
        cats = []
        for c in CATEGORIAS:
            w = wilcoxon_pareado(100 * q[f"humano_{c}"] / q["humano_sloc"], 100 * q[f"modelo_{c}"] / q["modelo_sloc"])
            cats.append({"categoria": c, "avisos humano": int(q[f"humano_{c}"].sum()),
                         f"avisos {mdl}": int(q[f"modelo_{c}"].sum()),
                         "humano /100 sloc": fmt(100 * q[f"humano_{c}"].sum() / q["humano_sloc"].sum()),
                         f"{mdl} /100 sloc": fmt(100 * q[f"modelo_{c}"].sum() / q["modelo_sloc"].sum()),
                         "Wilcoxon p": fmt_p(w["p"])})
        blocos.append(f"""### Humano × {mdl}

{T.tabela_md(pd.DataFrame(linhas))}

r = correlação rank-bisserial pareada (positiva: {mdl} maior). Por categoria (densidade por
solução no teste; agregada na tabela):

{T.tabela_md(pd.DataFrame(cats))}
""")
    return "## 3. QP2: smells\n\n" + "\n".join(blocos)


def secao_qp4(pareado, analise, cfg):
    blocos = []
    minp = cfg["paradigma"]["min_pontos"]
    for mdl, p in pareado.groupby("modelo", sort=False):
        c = p[p["comparavel"] & p["dif_densidade"].notna()]
        igual = c[c["mesmo_paradigma"] == True]["dif_densidade"]  # noqa: E712
        dif = c[c["mesmo_paradigma"] == False]["dif_densidade"]  # noqa: E712
        mw = stats.mannwhitneyu(dif, igual).pvalue if len(igual) and len(dif) else np.nan
        d = cliff(dif, igual)
        tab = pd.DataFrame([{"pares": "mesmo paradigma", "n": len(igual), "Δ densidade mediana": fmt(igual.median())},
                            {"pares": "paradigmas diferentes", "n": len(dif), "Δ densidade mediana": fmt(dif.median())}])
        trans = (c[c["mesmo_paradigma"] == False]  # noqa: E712
                 .groupby(["humano_paradigma", "modelo_paradigma"])
                 .agg(n=("slug", "size"), delta_mediano=("dif_densidade", "median")).reset_index()
                 .sort_values("n", ascending=False))
        suf = p[(p["humano_total_pontos"] >= minp) & (p["modelo_total_pontos"] >= minp)]
        m = suf[["dif_frac_funcional", "dif_densidade"]].dropna()
        variam = len(m) >= 5 and m["dif_frac_funcional"].nunique() > 1 and m["dif_densidade"].nunique() > 1
        r, pr = stats.spearmanr(m["dif_frac_funcional"], m["dif_densidade"]) if variam else (np.nan, np.nan)
        dd = p[["dificuldade", "dif_densidade"]].dropna()
        rd, prd = stats.spearmanr(dd["dificuldade"], dd["dif_densidade"]) if len(dd) >= 5 else (np.nan, np.nan)
        blocos.append(f"""### Humano × {mdl}

Δ densidade = {mdl} − humano, nos pares comparáveis.

{T.tabela_md(tab)}

Mann-Whitney p = {fmt_p(mw)} · delta de Cliff (diferentes × mesmo) = {fmt(d)} ({magnitude(d)}).

Transições (pares que divergiram):

{T.tabela_md(trans) if len(trans) else "nenhuma"}

Spearman entre Δ fração funcional e Δ densidade (pares com pelo menos {minp} pontos nos dois):
rho = {fmt(r)}, p = {fmt_p(pr)}, n = {len(m)}.

Spearman entre a dificuldade do exercício e Δ densidade (todos os {len(dd)} pares):
rho = {fmt(rd)}, p = {fmt_p(prd)}.
""")
    return ("## 6. QP4 (exploratória): divergência de paradigma, dificuldade e diferença de smells\n\n"
            + "\n".join(blocos) + secao_faixas(analise))


def secao_tentativas(analise, avisos, modelos, cfg):
    blocos = []
    for mdl in modelos:
        a = analise[analise["fonte"] == mdl]
        corrigidos = a[a["aceita"] & (a["tentativa"] > 1)]["slug"]
        um = a[(a["tentativa"] == 1) & a["slug"].isin(corrigidos) & a["tem_codigo"] & ~a["erro_sintaxe"]].set_index("slug")
        ac = a[a["aceita"] & a["slug"].isin(um.index)].set_index("slug")
        um = um.loc[ac.index]
        if not len(ac):
            blocos.append(f"### {mdl}\n\nNenhum exercício corrigido com 1ª tentativa analisável.\n")
            continue
        w_n = wilcoxon_pareado(um["n_avisos"], ac["n_avisos"])
        w_d = wilcoxon_pareado(um["densidade"], ac["densidade"])
        mudou = int((um["paradigma"] != ac["paradigma"]).sum())
        av = avisos_usados(avisos, cfg)
        av = av[(av["fonte"] == mdl) & av["slug"].isin(ac.index)]
        s1 = av[av["tentativa"] == 1].groupby("simbolo").size().rename("1ª tentativa")
        chaves = set(zip(ac.index, ac["tentativa"]))
        sa = av[[k in chaves for k in zip(av["slug"], av["tentativa"])]].groupby("simbolo").size().rename("aceita")
        simb = pd.concat([s1, sa], axis=1).fillna(0).astype(int)
        simb = simb.assign(dif=simb["aceita"] - simb["1ª tentativa"]).sort_values("dif", key=abs, ascending=False)
        blocos.append(f"""### {mdl}

Exercícios corrigidos com sucesso e com 1ª tentativa analisável (código válido): **{len(ac)}**.
Amostra pequena e selecionada pela própria falha; resultado secundário.

- Avisos: soma {int(um['n_avisos'].sum())} na 1ª → {int(ac['n_avisos'].sum())} na aceita · aumentou em
  {int((ac['n_avisos'] > um['n_avisos']).sum())}, diminuiu em {int((ac['n_avisos'] < um['n_avisos']).sum())},
  igual em {int((ac['n_avisos'] == um['n_avisos']).sum())} · Wilcoxon p = {fmt_p(w_n['p'])}
- Densidade mediana: {fmt(um['densidade'].median())} → {fmt(ac['densidade'].median())} · Wilcoxon p = {fmt_p(w_d['p'])}
- sloc (soma): {int(um['sloc'].sum())} → {int(ac['sloc'].sum())}
- Paradigma mudou da 1ª para a aceita em {mudou} de {len(ac)} exercícios

{T.tabela_md(simb.reset_index().rename(columns={"index": "simbolo"})) if len(simb) else ""}
""")
    return ("## 7. Secundária: 1ª tentativa × tentativa aceita\n\n" + "\n".join(blocos)
            + secao_trajetoria(analise, avisos, modelos, cfg))


# ------------------------------------------------------------------ seções novas
def secao_qp1_modelos(analise, modelos):
    """Concordância de paradigma entre os modelos e entropia dos rótulos por fonte."""
    ac = aceitas_em_todas(analise)
    ent = []
    for f, g in ac.groupby("fonte", sort=False):
        det = g[g["paradigma"].isin(DETERMINADOS)]["paradigma"]
        cont = det.value_counts()
        ent.append({"fonte": apelido(f), "soluções com rótulo determinado": len(det),
                    **{r: int(cont.get(r, 0)) for r in DETERMINADOS}, "entropia (bits)": fmt(entropia(det))})
    texto = f"""### Diversidade de paradigmas por fonte

Exercícios aceitos em todas as fontes ({ac['slug'].nunique()}), só rótulos determinados. Entropia de
Shannon dos rótulos: 0 = um único paradigma; máximo = log2(4) = 2 bits.

{T.tabela_md(pd.DataFrame(ent))}
"""
    ac = analise[analise["aceita"]]
    for i, a in enumerate(modelos):
        for b in modelos[i + 1:]:
            pa = ac[ac["fonte"] == a].set_index("slug")["paradigma"]
            pb = ac[ac["fonte"] == b].set_index("slug")["paradigma"]
            comuns = pa.index.intersection(pb.index)
            pa, pb = pa.loc[comuns], pb.loc[comuns]
            comp = pa.isin(DETERMINADOS) & pb.isin(DETERMINADOS)
            mat = pd.crosstab(pa[comp], pb[comp]).reindex(index=DETERMINADOS, columns=DETERMINADOS, fill_value=0)
            mat.insert(0, f"{a} \\ {b}", mat.index)
            iguais = int((pa[comp] == pb[comp]).sum())
            n1, n2, pv = mcnemar(pa[comp] == "procedural", pb[comp] == "procedural")
            texto += f"""
### {a} × {b}

Exercícios aceitos nos dois modelos: {len(comuns)}; pares comparáveis (os dois com rótulo
determinado): **{int(comp.sum())}** · mesmo paradigma: **{pct_ic(iguais, int(comp.sum()))}**.
Linhas: {a}; colunas: {b}.

{T.tabela_md(mat)}

Proporção de procedurais: {a} {pct_ic(int((pa[comp] == 'procedural').sum()), int(comp.sum()))} ·
{b} {pct_ic(int((pb[comp] == 'procedural').sum()), int(comp.sum()))} · só {a}: {n1} · só {b}: {n2} ·
McNemar p = {fmt_p(pv)}.
"""
    return texto


def testes_por_tipo(analise, avisos, cfg):
    """Densidade por tipo de smell nos exercícios aceitos em todas as fontes; Wilcoxon pareado por
    tipo e par de fontes, com Holm sobre todos os testes. Devolve (resumo, testes)."""
    ac = aceitas_em_todas(analise)
    fontes = list(dict.fromkeys(ac["fonte"]))
    a = avisos_usados(avisos, cfg).merge(ac[["fonte", "slug", "tentativa"]], on=["fonte", "slug", "tentativa"])
    sem_tipo = sorted(set(a["simbolo"]) - set(TIPO_DE))
    if sem_tipo:
        sys.exit(f"Símbolos sem tipo em src/catalogo_smells.py: {', '.join(sem_tipo)}")
    a = a.assign(tipo=a["simbolo"].map(TIPO_DE))
    sloc = ac.set_index(["fonte", "slug"])["sloc"]
    resumo, testes = [], []
    pares = [("referencia", m) for m in fontes if m != "referencia"]
    modelos = [f for f in fontes if f != "referencia"]
    pares += [(modelos[i], b) for i in range(len(modelos)) for b in modelos[i + 1:]]
    for tipo in ORDEM_TIPOS:
        n = a[a["tipo"] == tipo].groupby(["fonte", "slug"]).size().reindex(sloc.index, fill_value=0)
        if n.sum() == 0:
            continue
        dens = (100 * n / sloc).unstack("fonte")
        linha = {"tipo": tipo}
        for f in fontes:
            linha[f"{apelido(f)} (avisos)"] = int(n.xs(f, level="fonte").sum())
        for f in fontes:
            linha[f"{apelido(f)} /100 sloc"] = fmt(100 * n.xs(f, level="fonte").sum() / sloc.xs(f, level="fonte").sum())
        resumo.append(linha)
        for x, y in pares:
            w = wilcoxon_pareado(dens[x], dens[y])
            testes.append({"tipo": tipo, "x": x, "y": y, "y maior": int((dens[y] > dens[x]).sum()),
                           "x maior": int((dens[x] > dens[y]).sum()), "p": w["p"], "r": w["r"]})
    t = pd.DataFrame(testes)
    t["p_holm"] = holm(t["p"]) if len(t) else []
    return pd.DataFrame(resumo), t, ac["slug"].nunique()


def tabela_testes(t, x, y):
    q = t[(t["x"] == x) & (t["y"] == y)]
    return pd.DataFrame({"tipo": q["tipo"], f"{apelido(y)} maior": q["y maior"], f"{apelido(x)} maior": q["x maior"],
                         "p": [fmt_p(v) for v in q["p"]], "p (Holm)": [fmt_p(v) for v in q["p_holm"]],
                         "r": [fmt(v) for v in q["r"]]})


def secao_tipos(resumo, testes, n_ex):
    blocos = [f"""## 4. QP2: smells por tipo

Exercícios aceitos em todas as fontes: {n_ex}. Avisos usados na análise, agrupados pelo tipo de
smell (src/catalogo_smells.py). Testes: Wilcoxon pareado na densidade do tipo por solução;
correção de Holm sobre todos os {int(testes['p'].notna().sum())} testes com dados suficientes
(tipos × pares de fontes, inclusive os da QP3); r positivo = a segunda fonte maior. Tipos sem
nenhum aviso não aparecem; "–" = menos de 5 pares com diferença.

{T.tabela_md(resumo)}
"""]
    for (x, y), _ in testes[testes["x"] == "referencia"].groupby(["x", "y"], sort=False):
        blocos.append(f"### humano × {y}\n\n{T.tabela_md(tabela_testes(testes, x, y))}\n")
    return "\n".join(blocos)


def secao_qp3(analise, testes, cfg):
    modelos = [f for f in dict.fromkeys(analise["fonte"]) if f != "referencia"]
    m = analise[analise["fonte"].isin(modelos)]
    status = m.groupby(["fonte", "slug"]).apply(
        lambda g: pd.Series({"primeira": bool(g.loc[g["tentativa"] == 1, "aceita"].any()),
                             "final": bool(g["aceita"].any())}), include_groups=False).reset_index()
    exs = analise.drop_duplicates("slug").set_index("slug")["dificuldade"]
    status["dificuldade"] = status["slug"].map(exs)
    acerto = []
    for f, g in status.groupby("fonte", sort=False):
        acerto.append({"modelo": f, "exercícios": len(g), "passou na 1ª": pct_ic(int(g["primeira"].sum()), len(g)),
                       "passou no final": pct_ic(int(g["final"].sum()), len(g)),
                       "precisou de correção": int((g["final"] & ~g["primeira"]).sum())})
    faixas = []
    for lo, hi, nome in FAIXAS:
        q = status[status["dificuldade"].between(lo, hi)]
        linha = {"dificuldade": nome, "exercícios": q["slug"].nunique()}
        for f, g in q.groupby("fonte", sort=False):
            linha[f"{f} 1ª"] = pct_ic(int(g["primeira"].sum()), len(g))
            linha[f"{f} final"] = pct_ic(int(g["final"].sum()), len(g))
        faixas.append(linha)
    texto = f"""## 5. QP3: os modelos entre si

### Correção funcional

{T.tabela_md(pd.DataFrame(acerto))}

Por dificuldade do exercício (Exercism, 1 a 10):

{T.tabela_md(pd.DataFrame(faixas))}
"""
    ac = analise[analise["aceita"]]
    for i, a in enumerate(modelos):
        for b in modelos[i + 1:]:
            p = status.pivot(index="slug", columns="fonte", values=["primeira", "final"])
            lin = []
            for k, nome in (("primeira", "passou na 1ª tentativa"), ("final", "passou no final")):
                xa, xb = p[(k, a)].astype(bool), p[(k, b)].astype(bool)
                n1, n2, pv = mcnemar(xa, xb)
                lin.append({"medida": nome, "os dois": int((xa & xb).sum()), f"só {a}": n1, f"só {b}": n2,
                            "nenhum": int((~xa & ~xb).sum()), "McNemar p": fmt_p(pv)})
            da = ac[ac["fonte"] == a].set_index("slug")
            db = ac[ac["fonte"] == b].set_index("slug")
            comuns = da.index.intersection(db.index)
            dens = []
            for nome, col in (("densidade (avisos usados / 100 sloc)", "densidade"),
                              ("densidade com os avisos de estilo (sensibilidade)", "densidade_com_estilo"),
                              ("sloc", "sloc")):
                w = wilcoxon_pareado(da.loc[comuns, col], db.loc[comuns, col])
                dif = db.loc[comuns, col] - da.loc[comuns, col]
                dens.append({"medida": nome, "pares": w["n_pares"], f"{b} maior": int((dif > 0).sum()),
                             f"{a} maior": int((dif < 0).sum()), f"mediana {a}": fmt(da.loc[comuns, col].median()),
                             f"mediana {b}": fmt(db.loc[comuns, col].median()), "Wilcoxon p": fmt_p(w["p"]),
                             "r": fmt(w["r"])})
            texto += f"""
### {a} × {b}: acerto (McNemar exato, exercícios pareados)

{T.tabela_md(pd.DataFrame(lin))}

### {a} × {b}: smells (Wilcoxon pareado, {len(comuns)} exercícios aceitos nos dois; r positivo = {b} maior)

{T.tabela_md(pd.DataFrame(dens))}

Por tipo de smell (exercícios aceitos em todas as fontes; Holm da seção 4):

{T.tabela_md(tabela_testes(testes, a, b))}
"""
    return texto


def secao_faixas(analise):
    ac = aceitas_em_todas(analise)
    linhas = []
    for lo, hi, nome in FAIXAS:
        q = ac[ac["dificuldade"].between(lo, hi)]
        linha = {"dificuldade": nome, "exercícios": q["slug"].nunique()}
        for f, g in q.groupby("fonte", sort=False):
            linha[f"{apelido(f)}: avisos/solução"] = fmt(g["n_avisos"].mean())
            linha[f"{apelido(f)}: /100 sloc"] = fmt(100 * g["n_avisos"].sum() / g["sloc"].sum())
        linhas.append(linha)
    return f"""
### Smells por faixa de dificuldade

Exercícios aceitos em todas as fontes. Descritivo; a faixa difícil tem poucos exercícios.

{T.tabela_md(pd.DataFrame(linhas))}
"""


def secao_trajetoria(analise, avisos, modelos, cfg):
    blocos = ["""
### Trajetória tentativa a tentativa

Exercícios em que o modelo precisou de mais de uma tentativa; entram todas as tentativas com
código válido, aceitas ou não. Amostra selecionada pela falha; resultado secundário.
"""]
    usados = avisos_usados(avisos, cfg)
    for mdl in modelos:
        a = analise[(analise["fonte"] == mdl) & analise["tem_codigo"] & ~analise["erro_sintaxe"] & (analise["sloc"] > 0)]
        ult = analise[analise["fonte"] == mdl].groupby("slug")["tentativa"].max()
        varias = ult[ult >= 2].index
        a = a[a["slug"].isin(varias)]
        if not len(a):
            continue
        media = (a.groupby("tentativa").agg(exercícios=("slug", "size"), avisos=("n_avisos", "mean"),
                                            sloc=("sloc", "mean"), densidade=("densidade", "mean")).reset_index())
        pv = a.pivot(index="slug", columns="tentativa", values="n_avisos")
        passos = []
        for x, y in ((1, 2), (2, 3)):
            if x in pv and y in pv:
                q = pv[[x, y]].dropna()
                w = wilcoxon_pareado(q[x], q[y])
                passos.append({"passo": f"{x}ª → {y}ª", "exercícios": len(q), "subiu": int((q[y] > q[x]).sum()),
                               "caiu": int((q[y] < q[x]).sum()), "igual": int((q[y] == q[x]).sum()),
                               "Wilcoxon p": fmt_p(w["p"])})
        u = usados[(usados["fonte"] == mdl) & usados["slug"].isin(varias)]
        u = u.assign(ult=u["slug"].map(ult), tipo=u["simbolo"].map(TIPO_DE))
        t1 = u[u["tentativa"] == 1].groupby("tipo").size().rename("1ª tentativa")
        tu = u[u["tentativa"] == u["ult"]].groupby("tipo").size().rename("última tentativa")
        tipos = pd.concat([t1, tu], axis=1).reindex(ORDEM_TIPOS).dropna(how="all").fillna(0).astype(int)
        tipos = tipos.assign(dif=tipos["última tentativa"] - tipos["1ª tentativa"]).reset_index()
        blocos.append(f"""
#### {mdl}

Médias por tentativa ({len(varias)} exercícios com mais de uma tentativa):

{T.tabela_md(media)}

{T.tabela_md(pd.DataFrame(passos))}

Avisos por tipo, 1ª tentativa × última tentativa (aceita ou não):

{T.tabela_md(tipos)}
""")
    return "\n".join(blocos)


def main():
    cfg = T.analise()
    analise = T.ler("analise")
    pareado = T.ler("pareado")
    avisos = T.ler("avisos")
    ordem = {f: i for i, f in enumerate(T.resolver_fontes([]))}
    analise = analise.sort_values("fonte", key=lambda c: c.map(ordem), kind="stable")
    fontes = list(dict.fromkeys(analise["fonte"]))
    modelos = [f for f in fontes if f != "referencia"]
    outra = "c" if cfg["paradigma"]["regra_oficial"] == "d" else "d"
    m = T.manifesto()
    if m.get("analise", {}).get("fontes", {}).get("referencia", {}).get("parametros", {}).get("config") != cfg:
        sys.exit("config/analise.yaml mudou depois da última consolidação. Rode: python src/05_consolidar.py")

    resumo_tipos, testes, n_ex = testes_por_tipo(analise, avisos, cfg)
    texto = f"""# Resultados: paradigma e code smells, humano × LLM

Gerado em {datetime.now():%Y-%m-%d %H:%M} a partir de dados/tabelas/ (ver manifesto.json).
Unidade: o exercício, com a solução humana (referência do Exercism) e a do modelo lado a
lado; só tentativas aceitas (que passaram nos testes). Associações observacionais.

{secao_dados(analise, cfg, modelos)}
{secao_descritivo(analise, pareado)}
{secao_simbolos(analise, avisos, pareado, cfg)}
{secao_qp1(pareado, cfg, outra)}
{secao_qp1_modelos(analise, modelos)}
{secao_qp2(pareado)}
{secao_tipos(resumo_tipos, testes, n_ex)}
{secao_qp3(analise, testes, cfg)}
{secao_qp4(pareado, analise, cfg)}
{secao_tentativas(analise, avisos, modelos, cfg)}
"""
    T.RELATORIOS.mkdir(parents=True, exist_ok=True)
    (T.RELATORIOS / "resultados.md").write_text(texto, encoding="utf-8")
    print(f"Relatório: {T.RELATORIOS / 'resultados.md'}")


if __name__ == "__main__":
    main()
