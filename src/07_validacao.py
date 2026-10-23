"""Etapa 7: validação humana do classificador de paradigma.

Dois passos:

    python src/07_validacao.py amostra    sorteia a amostra e prepara os arquivos dos avaliadores
    python src/07_validacao.py avaliar    compara as respostas com a ferramenta -> relatorios/validacao.md

Amostra (dados/validacao/), a partir de dados/tabelas/analise.csv (tentativas aceitas):
    - Estratos aleatórios: fonte × rótulo da ferramenta (regra oficial, SEM o filtro de pontos),
      até `por_estrato` soluções em cada um (config/analise.yaml). Sorteio estratificado porque
      o sorteio simples traria quase só procedurais. Servem para ESTIMAR o acerto.
    - Estrato "difícil": `casos_dificeis` soluções perto do limiar (fração funcional entre 0,5
      e 0,8) ou de exercícios em que humano e modelo divergiram. Servem para entender os erros
      e são reportados À PARTE (incluí-los no acerto geral o subestimaria).
    - Às cegas: cada solução vira codigos/V###.py, sem fonte nem rótulo; a ordem é embaralhada.
      O esqueleto vai no topo do arquivo, comentado, para o avaliador saber o que foi imposto.
Arquivos gerados:
    instrucoes.md                    definições dos rótulos para os avaliadores
    codigos/V###.py                  as soluções
    respostas_avaliador_1.csv, _2    planilhas a preencher (id, rotulo, confianca, observacao)
    gabarito.csv                     fonte, exercício e rótulo da ferramenta (NÃO abrir antes de avaliar)
    estratos.csv                     tamanho de cada estrato na população (para ponderar o acerto)

Avaliação (relatorios/validacao.md):
    - kappa de Cohen entre os avaliadores (se houver dois) e lista das discordâncias;
      o consenso usa respostas_consenso.csv se existir (discordâncias resolvidas em conversa),
      senão só os itens em que os dois concordam
    - acerto da ferramenta contra o consenso nos estratos aleatórios: por estrato, geral
      ponderado pelo tamanho dos estratos (IC por bootstrap estratificado) e sem ponderação
      (IC de Wilson); só nos rótulos determinados pelo filtro (os usados na análise); matriz
      de confusão; kappa ferramenta × consenso
    - acerto no estrato difícil, à parte

Rótulos válidos nas respostas: oo, funcional, procedural, misto, neutro.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402

ROTULOS = ["oo", "funcional", "procedural", "misto", "neutro"]
PASTA = T.VALIDACAO
AVALIADORES = [PASTA / "respostas_avaliador_1.csv", PASTA / "respostas_avaliador_2.csv"]

INSTRUCOES = """# Instruções para a avaliação de paradigma

Para cada arquivo em `codigos/`, leia a solução e escolha **um** rótulo para o estilo
predominante do código que quem resolveu **acrescentou**. O esqueleto do exercício vem
comentado no topo do arquivo: nomes de funções, classes e métodos que ele já trazia foram
impostos e não contam.

| rótulo | quando usar |
|---|---|
| funcional | o problema é resolvido por transformação de valores: compreensões, geradores, `map`/`filter`/`reduce`, recursão, funções passadas como argumento; pouca ou nenhuma variável alterada passo a passo |
| procedural | o problema é resolvido passo a passo: laços `for`/`while`, acumuladores (`total += ...`), listas ou dicionários preenchidos e alterados ao longo do código |
| oo | a estrutura de classes criada por quem resolveu (além das que o esqueleto ou o exercício exigem; ver `exigencias.md`) é a parte mais relevante da solução. Se as classes novas são acessórias, ou se as classes são só as exigidas, classifique pelo estilo do código dentro delas |
| misto | há uma mistura relevante de estilos e nenhum predomina com clareza (nenhum chega a uns 2/3 do código) |
| neutro | o código é trivial demais para ter estilo (ex.: um `return` com uma conta ou um texto) |

Preencha a sua planilha (`respostas_avaliador_1.csv` ou `_2.csv`):

- `rotulo`: um dos cinco rótulos acima, em minúsculas;
- `confianca`: 1 (dúvida), 2 (razoável) ou 3 (certeza);
- `observacao`: opcional.

Regras: avalie sozinho, sem consultar o outro avaliador nem o `gabarito.csv`; não tente
adivinhar se o código é humano ou de IA; julgue só o estilo, não a qualidade nem a correção.
Discordâncias entre avaliadores são resolvidas depois, em conversa, no arquivo
`respostas_consenso.csv` (mesmas colunas).
"""


# ------------------------------------------------------------------ amostra
def sortear(args, cfg):
    respondidas = [a for a in AVALIADORES if a.exists() and pd.read_csv(a)["rotulo"].notna().any()]
    if respondidas and not args.refazer:
        sys.exit(f"Já há respostas em {respondidas[0].name}. Sortear de novo apagaria a amostra em uso. "
                 "Se for isso mesmo, rode com --refazer.")
    v = cfg["validacao"]
    rng = np.random.default_rng(v["semente"])
    a = T.ler("analise")
    pop = a[a["aceita"] & a["tem_codigo"] & ~a["erro_sintaxe"]].copy()
    pop["estrato"] = pop["fonte"] + " / " + pop["paradigma_sem_filtro"]

    aleat = []
    for _, g in pop.groupby("estrato"):
        k = min(v["por_estrato"], len(g))
        aleat.append(g.iloc[rng.choice(len(g), size=k, replace=False)])
    aleat = pd.concat(aleat)

    resto = pop.drop(aleat.index)
    divergentes = set()
    if T.caminho("pareado").exists():
        p = T.ler("pareado")
        divergentes = set(p.loc[p["mesmo_paradigma"] == False, "slug"])  # noqa: E712
    dificil = resto[resto["frac_funcional"].between(0.5, 0.8) | resto["slug"].isin(divergentes)]
    k = min(v["casos_dificeis"], len(dificil))
    dificil = dificil.iloc[rng.choice(len(dificil), size=k, replace=False)].assign(estrato="difícil")

    amostra = pd.concat([aleat, dificil]).sample(frac=1, random_state=v["semente"]).reset_index(drop=True)
    amostra["id"] = [f"V{i + 1:03d}" for i in range(len(amostra))]

    exs = {e["slug"]: e for e in T.exercicios()}
    codigos = PASTA / "codigos"
    if codigos.exists():
        for f in codigos.glob("*.py"):
            f.unlink()
    codigos.mkdir(parents=True, exist_ok=True)
    for r in amostra.itertuples():
        ex = exs[r.slug]
        if r.fonte == "referencia":
            codigo = ex["solucao_referencia"]
        else:
            codigo = (T.CODIGOS / r.fonte / r.slug / f"t{r.tentativa}" / ex["arquivo_solucao"]).read_text(encoding="utf-8")
        esq = "\n".join("# | " + l for l in ex["esqueleto"].rstrip().splitlines())
        (codigos / f"{r.id}.py").write_text(
            f"# Avaliação {r.id}\n# ESQUELETO DO EXERCÍCIO (imposto; não conta para o rótulo):\n{esq}\n"
            f"# {'-' * 70}\n# SOLUÇÃO:\n\n{codigo}", encoding="utf-8")

    for arq in AVALIADORES:
        pd.DataFrame({"id": amostra["id"], "rotulo": "", "confianca": "", "observacao": ""}).to_csv(
            arq, index=False, encoding="utf-8")
    amostra.rename(columns={"paradigma_sem_filtro": "rotulo_ferramenta", "paradigma": "rotulo_filtrado"})[
        ["id", "fonte", "slug", "tentativa", "estrato", "rotulo_ferramenta", "rotulo_filtrado", "total_pontos",
         "frac_funcional"]].to_csv(PASTA / "gabarito.csv", index=False, encoding="utf-8")
    pop.groupby("estrato").size().rename("tamanho_na_populacao").reset_index().to_csv(
        PASTA / "estratos.csv", index=False, encoding="utf-8")
    (PASTA / "instrucoes.md").write_text(INSTRUCOES, encoding="utf-8")

    print(f"Amostra: {len(amostra)} soluções ({len(aleat)} aleatórias em {aleat['estrato'].nunique()} estratos "
          f"+ {len(dificil)} difíceis) em {PASTA}")
    print(aleat.groupby("estrato").size().to_string())
    print("\nEntregue a cada avaliador: instrucoes.md, a pasta codigos/ e a sua planilha de respostas. "
          "Não entregue gabarito.csv.")


# ------------------------------------------------------------------ avaliação
def ler_respostas(arq):
    if not arq.exists():
        return None
    # aceita vírgula ou ponto e vírgula (Excel em português salva com ";") e UTF-8 ou Latin-1
    try:
        r = pd.read_csv(arq, dtype=str, sep=None, engine="python", encoding="utf-8-sig").fillna("")
    except UnicodeDecodeError:
        r = pd.read_csv(arq, dtype=str, sep=None, engine="python", encoding="latin-1").fillna("")
    r["rotulo"] = r["rotulo"].str.strip().str.lower()
    r = r[r["rotulo"] != ""]
    invalidos = r[~r["rotulo"].isin(ROTULOS)]
    if len(invalidos):
        sys.exit(f"{arq.name}: rótulos inválidos {sorted(set(invalidos['rotulo']))} (ids {list(invalidos['id'])[:5]}). "
                 f"Use: {', '.join(ROTULOS)}")
    return r.set_index("id")["rotulo"] if len(r) else None


def kappa(a, b):
    a, b = pd.Series(a).reset_index(drop=True), pd.Series(b).reset_index(drop=True)
    if len(a) == 0:
        return np.nan
    po = (a == b).mean()
    pe = sum((a == k).mean() * (b == k).mean() for k in set(a) | set(b))
    return np.nan if pe == 1 else (po - pe) / (1 - pe)


def leitura_kappa(k):
    if pd.isna(k):
        return "–"
    return ("fraca" if k < 0.2 else "razoável" if k < 0.4 else "moderada" if k < 0.6
            else "substancial" if k < 0.8 else "quase perfeita")


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - m, c + m


def pct(k, n):
    lo, hi = wilson(k, n)
    return "–" if n == 0 else f"{100 * k / n:.0f}% [{100 * lo:.0f}–{100 * hi:.0f}] (n = {n})"


def acerto_ponderado(df, tamanhos, rng, reps=2000):
    """Acerto geral ponderado pelo tamanho de cada estrato na população, com IC de 95% por
    bootstrap estratificado (reamostra dentro de cada estrato)."""
    grupos = {e: g["acertou"].to_numpy() for e, g in df.groupby("estrato")}
    pesos = {e: tamanhos.get(e, 0) for e in grupos}
    total = sum(pesos.values())
    est = sum(pesos[e] * g.mean() for e, g in grupos.items()) / total
    boot = [sum(pesos[e] * rng.choice(g, len(g)).mean() for e, g in grupos.items()) / total for _ in range(reps)]
    return est, np.percentile(boot, 2.5), np.percentile(boot, 97.5)


def avaliar(cfg):
    gab = pd.read_csv(PASTA / "gabarito.csv").set_index("id")
    tamanhos = pd.read_csv(PASTA / "estratos.csv").set_index("estrato")["tamanho_na_populacao"].to_dict()
    r1, r2 = (ler_respostas(a) for a in AVALIADORES)
    if r1 is None:
        sys.exit("Nenhuma resposta em respostas_avaliador_1.csv.")
    partes = []

    if r2 is not None:
        ambos = r1.index.intersection(r2.index)
        k = kappa(r1[ambos], r2[ambos])
        disc = pd.DataFrame({"id": ambos, "avaliador 1": r1[ambos].values, "avaliador 2": r2[ambos].values})
        disc = disc[disc["avaliador 1"] != disc["avaliador 2"]]
        partes.append(f"""## 1. Concordância entre avaliadores

Itens avaliados pelos dois: **{len(ambos)}** · concordância bruta: {pct(len(ambos) - len(disc), len(ambos))} ·
**kappa de Cohen = {f"{k:.2f}".replace(".", ",")}** ({leitura_kappa(k)}, escala de Landis e Koch).

Discordâncias (resolver em conversa e registrar em respostas_consenso.csv):

{T.tabela_md(disc) if len(disc) else "nenhuma"}
""")
        consenso = ler_respostas(PASTA / "respostas_consenso.csv")
        if consenso is None:
            consenso = r1[ambos][r1[ambos] == r2[ambos]]
            origem = "itens em que os dois avaliadores concordaram (discordâncias ainda não resolvidas ficam de fora)"
        else:
            origem = "respostas_consenso.csv"
    else:
        consenso, origem = r1, "um único avaliador (sem medida de concordância entre humanos)"
        partes.append("## 1. Concordância entre avaliadores\n\nSó há respostas de um avaliador; o kappa entre "
                      "humanos não pode ser calculado.\n")

    d = gab.join(consenso.rename("humano"), how="inner")
    d["acertou"] = d["rotulo_ferramenta"] == d["humano"]
    aleat, dificil = d[d["estrato"] != "difícil"], d[d["estrato"] == "difícil"]
    rng = np.random.default_rng(cfg["validacao"]["semente"])

    if len(aleat):
        est, lo, hi = acerto_ponderado(aleat, tamanhos, rng)
        det = aleat[aleat["rotulo_filtrado"].isin(["oo", "funcional", "procedural", "misto"])]
        por_estrato = (aleat.groupby("estrato").agg(n=("acertou", "size"), acertos=("acertou", "sum")).reset_index())
        por_estrato["acerto"] = [pct(int(a), int(n)) for a, n in zip(por_estrato["acertos"], por_estrato["n"])]
        por_estrato["na população"] = por_estrato["estrato"].map(tamanhos)
        conf = pd.crosstab(aleat["rotulo_ferramenta"], aleat["humano"]).reindex(index=ROTULOS, columns=ROTULOS,
                                                                               fill_value=0)
        conf.insert(0, "ferramenta \\ humano", conf.index)
        kf = kappa(aleat["rotulo_ferramenta"], aleat["humano"])
        partes.append(f"""## 2. Acerto da ferramenta (estratos aleatórios)

Referência: {origem}.

- **Acerto geral ponderado pelos estratos: {100 * est:.0f}% [IC 95%: {100 * lo:.0f}–{100 * hi:.0f}]**
  (bootstrap estratificado; estima o acerto na população de soluções aceitas)
- Acerto sem ponderação: {pct(int(aleat['acertou'].sum()), len(aleat))} (IC de Wilson)
- Só nos rótulos determinados pelo filtro de pontos (os usados na análise):
  {pct(int(det['acertou'].sum()), len(det))}
- Kappa ferramenta × humano: {f"{kf:.2f}".replace(".", ",")} ({leitura_kappa(kf)})

Por estrato:

{T.tabela_md(por_estrato[["estrato", "n", "acerto", "na população"]])}

Matriz de confusão (linhas: ferramenta; colunas: humano):

{T.tabela_md(conf)}
""")
    if len(dificil):
        erros = dificil[~dificil["acertou"]].reset_index()[["id", "fonte", "slug", "rotulo_ferramenta", "humano",
                                                            "total_pontos"]]
        partes.append(f"""## 3. Casos difíceis (à parte)

Acerto: {pct(int(dificil['acertou'].sum()), len(dificil))}. Não entra no acerto geral.

{T.tabela_md(erros) if len(erros) else "nenhum erro"}
""")

    texto = "# Validação humana do classificador de paradigma\n\n" + "\n".join(partes)
    T.RELATORIOS.mkdir(parents=True, exist_ok=True)
    (T.RELATORIOS / "validacao.md").write_text(texto, encoding="utf-8")
    print(f"Relatório: {T.RELATORIOS / 'validacao.md'}")


def main():
    parser = argparse.ArgumentParser(description="Validação humana do classificador de paradigma.")
    parser.add_argument("passo", choices=["amostra", "avaliar"])
    parser.add_argument("--refazer", action="store_true", help="sorteia de novo mesmo com respostas já preenchidas")
    args = parser.parse_args()
    cfg = T.analise()
    if args.passo == "amostra":
        sortear(args, cfg)
    else:
        avaliar(cfg)


if __name__ == "__main__":
    main()
