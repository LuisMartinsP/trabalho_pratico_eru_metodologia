"""Etapa 8: monta o banco relacional dados/estudo.sqlite a partir das tabelas do pipeline.

O banco é DERIVADO: os CSVs de dados/tabelas/ continuam sendo a fonte da verdade, e o
arquivo é apagado e recriado a cada execução (rodou o pipeline, rode esta etapa de novo).
Não precisa instalar nada: o SQLite vem com o Python (módulo sqlite3).

Tabelas
    fontes      (fonte PK)                        humano e cada LLM
    exercicios  (slug PK)                         dificuldade, esqueleto e o código do esqueleto
    simbolos    (simbolo PK)                      tipo de smell, categoria do Pylint, descrição e se
                                                  é ignorado na análise principal (simbolos_ignorados)
    solucoes    (fonte, slug, tentativa) PK       status, aceita, sloc e o código da tentativa
    paradigmas  (fonte, slug, tentativa) PK/FK    pontos e rótulos (regras D, C e Dyer original)
    avisos      (id PK; fonte, slug, tentativa FK; simbolo FK)
                                                  um aviso do Pylint, com a linha de código

Views (consultas prontas, usadas como tabelas)
    v_solucoes       cada tentativa com exercício, paradigma oficial, nº de avisos e densidade
    v_comparaveis    tentativas aceitas dos exercícios aceitos em TODAS as fontes
    v_avisos         cada aviso com tipo, descrição, paradigma da solução e esqueleto; as colunas
                     linha_e_comentario (linha começa com #) e linha_de_documentacao (comentário
                     de linha inteira ou docstring) servem para separar documentação de código
    v_tipos_solucao  avisos por tipo em cada tentativa aceita (com zeros)
    v_pareado        humano × cada LLM no mesmo exercício (tentativas aceitas)

As contagens e densidades das views seguem a análise principal: sem os avisos herdados do
esqueleto e sem os símbolos ignorados (config/analise.yaml, simbolos_ignorados);
densidade_com_estilo inclui os ignorados. v_avisos traz todos os avisos, com as colunas
herdado_esqueleto e ignorado, para filtrar.
A coluna `paradigma` segue a regra oficial e o filtro de config/analise.yaml.

Uso (a partir da raiz do projeto, com o .venv ativado), depois das etapas 2 e 4:
    python src/08_banco.py
Exemplo de consulta:
    SELECT tipo, fonte, COUNT(*) FROM v_avisos
    WHERE aceita AND NOT herdado_esqueleto AND NOT ignorado GROUP BY tipo, fonte;
"""
import ast
import sqlite3
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402
from catalogo_smells import DESCRICAO, ORDEM_TIPOS, TIPO_DE  # noqa: E402

BANCO = T.DADOS / "estudo.sqlite"
APELIDO = {"referencia": "humano"}

ESQUEMA = """
CREATE TABLE fontes (
    fonte   TEXT PRIMARY KEY,
    apelido TEXT NOT NULL,
    eh_llm  INTEGER NOT NULL CHECK (eh_llm IN (0, 1))
);
CREATE TABLE exercicios (
    slug             TEXT PRIMARY KEY,
    dificuldade      INTEGER,
    tipo_esqueleto   TEXT,
    grupo_esqueleto  TEXT,      -- "classe" inclui os esqueletos com classe e funções
    sloc_esqueleto   INTEGER,
    arquivo_solucao  TEXT,
    codigo_esqueleto TEXT
);
CREATE TABLE simbolos (
    simbolo          TEXT PRIMARY KEY,
    tipo             TEXT NOT NULL,
    ordem_tipo       INTEGER NOT NULL,
    categoria_pylint TEXT,
    descricao        TEXT,
    ignorado         INTEGER NOT NULL CHECK (ignorado IN (0, 1))
);
CREATE TABLE solucoes (
    fonte        TEXT    NOT NULL REFERENCES fontes(fonte),
    slug         TEXT    NOT NULL REFERENCES exercicios(slug),
    tentativa    INTEGER NOT NULL,
    status       TEXT,
    aceita       INTEGER NOT NULL,
    ultima       INTEGER NOT NULL,
    tem_codigo   INTEGER NOT NULL,
    erro_sintaxe INTEGER NOT NULL,
    sloc         INTEGER,
    codigo       TEXT,
    PRIMARY KEY (fonte, slug, tentativa)
);
CREATE TABLE paradigmas (
    fonte TEXT NOT NULL, slug TEXT NOT NULL, tentativa INTEGER NOT NULL,
    classes_novas TEXT,
    pontos_func_d INTEGER, pontos_proc_d INTEGER, pontos_oo_d INTEGER, total_pontos_d INTEGER,
    rotulo_d TEXT, filtrado_d TEXT,
    pontos_func_c INTEGER, pontos_proc_c INTEGER, pontos_oo_c INTEGER, total_pontos_c INTEGER,
    rotulo_c TEXT, filtrado_c TEXT,
    rotulo_dyer_original TEXT,
    PRIMARY KEY (fonte, slug, tentativa),
    FOREIGN KEY (fonte, slug, tentativa) REFERENCES solucoes (fonte, slug, tentativa)
);
CREATE TABLE avisos (
    id                INTEGER PRIMARY KEY,
    fonte             TEXT    NOT NULL,
    slug              TEXT    NOT NULL,
    tentativa         INTEGER NOT NULL,
    simbolo           TEXT    NOT NULL REFERENCES simbolos(simbolo),
    codigo_pylint     TEXT,
    linha             INTEGER,
    codigo_da_linha   TEXT,
    linha_de_documentacao INTEGER NOT NULL,  -- comentário de linha inteira ou linha de docstring
    mensagem          TEXT,
    herdado_esqueleto INTEGER NOT NULL,
    FOREIGN KEY (fonte, slug, tentativa) REFERENCES solucoes (fonte, slug, tentativa)
);
CREATE INDEX idx_avisos_solucao ON avisos (fonte, slug, tentativa);
CREATE INDEX idx_avisos_simbolo ON avisos (simbolo);
"""


def views(regra, n_fontes):
    """SQL das views. `regra` = regra oficial (d ou c); `n_fontes` = nº de fontes no banco."""
    return f"""
CREATE VIEW v_solucoes AS
WITH proprios AS (
    SELECT a.fonte, a.slug, a.tentativa,
           SUM(NOT a.herdado_esqueleto AND NOT m.ignorado) AS n_avisos,
           SUM(NOT a.herdado_esqueleto AND m.ignorado)     AS n_ignorados,
           SUM(a.herdado_esqueleto)                        AS n_herdados
    FROM avisos a JOIN simbolos m USING (simbolo)
    GROUP BY a.fonte, a.slug, a.tentativa
), aceitos_em_todas AS (
    SELECT slug FROM solucoes WHERE aceita GROUP BY slug HAVING COUNT(DISTINCT fonte) = {n_fontes}
)
SELECT s.fonte, f.apelido, f.eh_llm, s.slug, s.tentativa, s.status, s.aceita, s.ultima,
       s.erro_sintaxe, s.sloc,
       e.dificuldade, e.tipo_esqueleto, e.grupo_esqueleto,
       p.filtrado_{regra} AS paradigma,
       p.rotulo_{regra}   AS paradigma_sem_filtro,
       p.filtrado_c       AS paradigma_c,
       p.rotulo_dyer_original AS paradigma_dyer,
       p.pontos_func_{regra} AS pontos_func, p.pontos_proc_{regra} AS pontos_proc,
       p.total_pontos_{regra} AS total_pontos,
       CASE WHEN p.pontos_func_{regra} + p.pontos_proc_{regra} > 0
            THEN 1.0 * p.pontos_func_{regra} / (p.pontos_func_{regra} + p.pontos_proc_{regra}) END
            AS frac_funcional,
       p.classes_novas,
       COALESCE(a.n_avisos, 0)   AS n_avisos,
       COALESCE(a.n_ignorados, 0) AS n_ignorados,
       COALESCE(a.n_herdados, 0) AS n_herdados,
       CASE WHEN s.sloc > 0 THEN 100.0 * COALESCE(a.n_avisos, 0) / s.sloc END AS densidade,
       CASE WHEN s.sloc > 0 THEN 100.0 * (COALESCE(a.n_avisos, 0) + COALESCE(a.n_ignorados, 0)) / s.sloc END
            AS densidade_com_estilo,
       s.slug IN (SELECT slug FROM aceitos_em_todas) AS comparavel,
       s.codigo
FROM solucoes s
JOIN fontes f USING (fonte)
JOIN exercicios e USING (slug)
LEFT JOIN paradigmas p USING (fonte, slug, tentativa)
LEFT JOIN proprios a USING (fonte, slug, tentativa);

CREATE VIEW v_comparaveis AS
SELECT * FROM v_solucoes WHERE aceita AND comparavel;

CREATE VIEW v_avisos AS
SELECT a.id, a.fonte, v.apelido, a.slug, a.tentativa, v.aceita, v.comparavel,
       m.tipo, a.simbolo, m.categoria_pylint, m.descricao,
       a.linha, a.codigo_da_linha,
       TRIM(a.codigo_da_linha) LIKE '#%' AS linha_e_comentario,
       a.linha_de_documentacao,
       TRIM(a.codigo_da_linha) = ''      AS linha_em_branco,
       a.mensagem, a.herdado_esqueleto, m.ignorado,
       v.paradigma, v.tipo_esqueleto, v.grupo_esqueleto, v.dificuldade, v.sloc
FROM avisos a
JOIN simbolos m USING (simbolo)
JOIN v_solucoes v USING (fonte, slug, tentativa);

CREATE VIEW v_tipos_solucao AS
WITH tipos AS (SELECT DISTINCT tipo, ordem_tipo FROM simbolos WHERE NOT ignorado)
SELECT v.fonte, v.apelido, v.slug, v.tentativa, v.comparavel, v.paradigma, v.sloc,
       t.tipo, t.ordem_tipo,
       COUNT(a.id) AS n_avisos,
       CASE WHEN v.sloc > 0 THEN 100.0 * COUNT(a.id) / v.sloc END AS densidade
FROM v_solucoes v
CROSS JOIN tipos t
LEFT JOIN avisos a
       ON a.fonte = v.fonte AND a.slug = v.slug AND a.tentativa = v.tentativa
      AND NOT a.herdado_esqueleto
      AND a.simbolo IN (SELECT simbolo FROM simbolos WHERE tipo = t.tipo AND NOT ignorado)
WHERE v.aceita
GROUP BY v.fonte, v.slug, v.tentativa, t.tipo;

CREATE VIEW v_pareado AS
SELECT m.fonte AS modelo, h.slug, h.dificuldade, h.tipo_esqueleto, h.grupo_esqueleto,
       h.sloc AS humano_sloc,             m.sloc AS modelo_sloc,
       h.n_avisos AS humano_n_avisos,     m.n_avisos AS modelo_n_avisos,
       h.densidade AS humano_densidade,   m.densidade AS modelo_densidade,
       h.paradigma AS humano_paradigma,   m.paradigma AS modelo_paradigma,
       h.frac_funcional AS humano_frac_funcional, m.frac_funcional AS modelo_frac_funcional,
       m.tentativa AS modelo_tentativa_aceita,
       m.densidade - h.densidade AS dif_densidade,
       h.paradigma NOT IN ('neutro', 'indeterminado')
         AND m.paradigma NOT IN ('neutro', 'indeterminado') AS comparavel_paradigma,
       h.paradigma = m.paradigma AS mesmo_paradigma
FROM v_solucoes h
JOIN v_solucoes m ON m.slug = h.slug AND m.eh_llm AND m.aceita
WHERE h.fonte = 'referencia' AND h.aceita;
"""


def linhas_de_docstring(codigo):
    """Números das linhas ocupadas por docstrings (de módulo, classe ou função), pela árvore
    sintática. Código com erro de sintaxe devolve conjunto vazio."""
    try:
        arvore = ast.parse(codigo)
    except SyntaxError:
        return set()
    linhas = set()
    for no in ast.walk(arvore):
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and no.body:
            primeiro = no.body[0]
            if (isinstance(primeiro, ast.Expr) and isinstance(primeiro.value, ast.Constant)
                    and isinstance(primeiro.value.value, str)):
                linhas.update(range(primeiro.lineno, primeiro.end_lineno + 1))
    return linhas


def ler_codigo(caminho):
    return caminho.read_text(encoding="utf-8") if caminho.exists() else None


def montar(fontes, regra):
    sol = T.ler("solucoes", fontes)
    av = T.ler("avisos", fontes)
    par = T.ler("paradigmas", fontes)
    exs = {ex["slug"]: ex for ex in T.exercicios()}

    sem_tipo = sorted(set(av["simbolo"]) - set(TIPO_DE))
    if sem_tipo:
        sys.exit(f"Símbolos sem tipo em src/catalogo_smells.py: {', '.join(sem_tipo)}")

    tab_fontes = pd.DataFrame([{"fonte": f, "apelido": APELIDO.get(f, f), "eh_llm": int(f != "referencia")}
                               for f in fontes])

    ex = T.ler("exercicios")
    ex["grupo_esqueleto"] = ex["tipo_esqueleto"].map(lambda t: "funcao" if t == "funcao" else "classe")
    ex["arquivo_solucao"] = ex["slug"].map(lambda s: exs[s]["arquivo_solucao"])
    ex["codigo_esqueleto"] = [ler_codigo(T.CODIGOS / "_esqueleto" / s / a)
                              for s, a in zip(ex["slug"], ex["arquivo_solucao"])]

    categoria = av.drop_duplicates("simbolo").set_index("simbolo")["categoria"]
    ignorados = set(T.analise()["smells"].get("simbolos_ignorados") or [])
    simbolos = pd.DataFrame([{"simbolo": s, "tipo": t, "ordem_tipo": ORDEM_TIPOS.index(t),
                              "categoria_pylint": categoria.get(s), "descricao": DESCRICAO[s],
                              "ignorado": int(s in ignorados)}
                             for s, t in TIPO_DE.items()])

    sol = sol.copy()
    arquivos = ex.set_index("slug")["arquivo_solucao"]
    sol["codigo"] = [ler_codigo(T.CODIGOS / f / s / f"t{n}" / arquivos[s]) if tc else None
                     for f, s, n, tc in zip(sol["fonte"], sol["slug"], sol["tentativa"], sol["tem_codigo"])]
    faltando = int((sol["tem_codigo"] & sol["codigo"].isna()).sum())
    if faltando:
        sys.exit(f"{faltando} tentativa(s) sem arquivo em dados/codigos/. Rode: python src/02_pylint.py")

    linhas_por_sol = {k: (c or "").splitlines() for k, c in
                      zip(zip(sol["fonte"], sol["slug"], sol["tentativa"]), sol["codigo"])}

    def linha(r):
        ls = linhas_por_sol.get((r.fonte, r.slug, r.tentativa), [])
        return ls[r.linha - 1] if 1 <= r.linha <= len(ls) else None

    av = av.rename(columns={"codigo": "codigo_pylint"})
    av["codigo_da_linha"] = [linha(r) for r in av.itertuples()]
    docs = {k: linhas_de_docstring(c or "") for k, c in
            zip(zip(sol["fonte"], sol["slug"], sol["tentativa"]), sol["codigo"])}
    av["linha_de_documentacao"] = [
        int((c or "").strip().startswith("#") or r.linha in docs.get((r.fonte, r.slug, r.tentativa), ()))
        for r, c in zip(av.itertuples(), av["codigo_da_linha"])]
    av = av[["fonte", "slug", "tentativa", "simbolo", "codigo_pylint", "linha", "codigo_da_linha",
             "linha_de_documentacao",
             "mensagem", "herdado_esqueleto"]]

    for df, cols in [(sol, ["aceita", "ultima", "tem_codigo", "erro_sintaxe"]), (av, ["herdado_esqueleto"])]:
        for c in cols:
            df[c] = df[c].astype(int)

    BANCO.unlink(missing_ok=True)
    con = sqlite3.connect(BANCO)
    try:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(ESQUEMA)
        # ordem importa: as tabelas referenciadas entram antes das que apontam para elas
        for nome, df in [("fontes", tab_fontes), ("exercicios", ex), ("simbolos", simbolos),
                         ("solucoes", sol), ("paradigmas", par), ("avisos", av)]:
            df.to_sql(nome, con, if_exists="append", index=False)
        problemas = con.execute("PRAGMA foreign_key_check").fetchall()
        if problemas:
            sys.exit(f"Chaves estrangeiras inválidas: {problemas[:5]}")
        con.executescript(views(regra, len(fontes)))
        con.commit()
        contagens = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                     for t in ["fontes", "exercicios", "simbolos", "solucoes", "paradigmas", "avisos",
                               "v_comparaveis", "v_pareado"]}
    finally:
        con.close()
    return contagens


def main():
    cfg = T.analise()
    fontes = T.resolver_fontes(sys.argv[1:])
    regra = cfg["paradigma"]["regra_oficial"]
    contagens = montar(fontes, regra)
    print(f"Banco: {BANCO.relative_to(T.RAIZ).as_posix()} · fontes: {', '.join(fontes)} · "
          f"paradigma oficial: regra {regra.upper()}")
    for nome, n in contagens.items():
        print(f"  {nome:<14} {n:>6} linhas")


if __name__ == "__main__":
    main()
