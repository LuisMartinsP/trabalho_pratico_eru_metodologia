"""Tabelas do estudo: caminhos, colunas, leitura/escrita e manifesto.

Todas as tabelas ficam em dados/tabelas/, em formato longo (uma linha por registro, com a
fonte numa coluna) e com a chave (fonte, slug, tentativa):

    tabela            gerada por            uma linha por
    solucoes.csv      02_pylint.py          tentativa (o humano tem só a tentativa 1)
    avisos.csv        02_pylint.py          aviso do Pylint
    paradigmas.csv    04_paradigma.py       tentativa com código válido
    exercicios.csv    05_consolidar.py      exercício
    analise.csv       05_consolidar.py      tentativa, com smells e paradigma juntos
    pareado.csv       05_consolidar.py      exercício × modelo (humano e modelo lado a lado)

O manifesto (dados/tabelas/manifesto.json) registra, para cada tabela e cada fonte, quando
e com quais parâmetros ela foi gerada. As etapas seguintes conferem o manifesto e param
com uma instrução se alguma tabela estiver desatualizada (ex.: min_pontos mudou no
config/analise.yaml, ou o classificador foi editado depois da última execução).
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

import config

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
TABELAS = DADOS / "tabelas"
CODIGOS = DADOS / "codigos"
VALIDACAO = DADOS / "validacao"
RELATORIOS = RAIZ / "relatorios"
EXERCISM = DADOS / "exercism.jsonl"
PYLINTRC = RAIZ / ".pylintrc"
ANALISE_YAML = RAIZ / "config" / "analise.yaml"
MANIFESTO = TABELAS / "manifesto.json"

NAO_MODELOS = {"_cache", "_antigo", "codigos", "tabelas", "validacao"}

COLUNAS = {
    "solucoes": ["fonte", "slug", "tentativa", "status", "aceita", "ultima", "tem_codigo",
                 "erro_sintaxe", "sloc"],
    "avisos": ["fonte", "slug", "tentativa", "categoria", "codigo", "simbolo", "linha",
               "mensagem", "herdado_esqueleto"],
    "paradigmas": ["fonte", "slug", "tentativa", "classes_novas",
                   "pontos_func_d", "pontos_proc_d", "pontos_oo_d", "total_pontos_d", "rotulo_d", "filtrado_d",
                   "pontos_func_c", "pontos_proc_c", "pontos_oo_c", "total_pontos_c", "rotulo_c", "filtrado_c",
                   "rotulo_dyer_original"],
    "exercicios": ["slug", "dificuldade", "tipo_esqueleto", "sloc_esqueleto"],
}
CHAVE = ["fonte", "slug", "tentativa"]


# ------------------------------------------------------------------ configuração
def analise():
    return yaml.safe_load(ANALISE_YAML.read_text(encoding="utf-8"))


def hash_arquivos(*caminhos):
    """Hash curto do conteúdo de arquivos (detecta classificador ou .pylintrc editados)."""
    h = hashlib.sha256()
    for c in caminhos:
        h.update(Path(c).read_bytes() if Path(c).exists() else b"")
    return h.hexdigest()[:12]


def exercicios():
    """Exercícios cuja solução de referência passa nos testes (os 129 do estudo)."""
    todos = [json.loads(l) for l in EXERCISM.read_text(encoding="utf-8").splitlines()]
    return [e for e in todos if e["referencia_passa"]]


def commit_exercism():
    return exercicios()[0]["commit_exercism"]


# ------------------------------------------------------------------ fontes
def modelos_disponiveis():
    return sorted(p.name for p in DADOS.iterdir()
                  if p.is_dir() and p.name not in NAO_MODELOS and any(p.glob("*/resultado.json")))


def resolver_fontes(nomes):
    """Traduz os argumentos em nomes de fonte; sem argumentos, usa config/analise.yaml."""
    nomes = nomes or analise()["fontes"]
    perfis = config.carregar().get("modelos", {}) if config.ARQUIVO.exists() else {}
    fontes = []
    for nome in nomes:
        if nome == "referencia":
            fontes.append(nome)
        elif nome in perfis:
            fontes.append(config.pasta_do_modelo(perfis[nome]["modelo"]))
        elif (DADOS / nome).is_dir() and nome not in NAO_MODELOS:
            fontes.append(nome)
        else:
            sys.exit(f"Fonte '{nome}' não encontrada. Opções: referencia, "
                     f"{', '.join([*perfis, *modelos_disponiveis()])}")
    return list(dict.fromkeys(fontes))


def tentativas(fonte, exercicios_):
    """Gera um dict por tentativa: ex, tentativa, status, aceita, ultima, codigo.

    Referência: uma tentativa, aceita. Modelos: todas as tentativas salvas pela etapa 3;
    exercícios ainda sem resultado.json (coleta incompleta) ficam de fora.
    """
    for ex in exercicios_:
        if fonte == "referencia":
            yield {"ex": ex, "tentativa": 1, "status": "passou", "aceita": True, "ultima": True,
                   "codigo": ex["solucao_referencia"]}
            continue
        pasta = DADOS / fonte / ex["slug"]
        res = pasta / "resultado.json"
        if not res.exists():
            continue
        n_total = json.loads(res.read_text(encoding="utf-8"))["tentativas"]
        for n in range(1, n_total + 1):
            t = json.loads((pasta / f"tentativa_{n}.json").read_text(encoding="utf-8"))
            yield {"ex": ex, "tentativa": n, "status": t["status"], "aceita": t["status"] == "passou",
                   "ultima": n == n_total, "codigo": t.get("codigo") or ""}


# ------------------------------------------------------------------ manifesto
def _manifesto():
    return json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {}


def _registrar(nome, script, fontes, parametros):
    m = _manifesto()
    t = m.setdefault(nome, {"script": script, "fontes": {}})
    t["script"] = script
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    for f in fontes:
        t["fontes"][f] = {"gerado_em": agora, "parametros": parametros}
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")


def manifesto():
    return _manifesto()


# ------------------------------------------------------------------ leitura e escrita
def caminho(nome):
    return TABELAS / f"{nome}.csv"


def salvar(nome, df, script, fontes=None, parametros=None, substituir=True):
    """Grava a tabela e registra as `fontes` no manifesto. Com substituir=True, troca só as
    linhas dessas fontes e mantém as outras (assim cada fonte pode ser processada
    separadamente); com False, regrava a tabela inteira."""
    if nome in COLUNAS:
        faltam = set(COLUNAS[nome]) - set(df.columns)
        if faltam:
            raise ValueError(f"{nome}: faltam as colunas {sorted(faltam)}")
        df = df[COLUNAS[nome]]
    if substituir and fontes is not None and caminho(nome).exists():
        antigo = pd.read_csv(caminho(nome))
        df = pd.concat([antigo[~antigo["fonte"].isin(fontes)], df], ignore_index=True)
    if "fonte" in df.columns:
        df = df.sort_values([c for c in CHAVE if c in df.columns], kind="stable")
    TABELAS.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho(nome), index=False, encoding="utf-8")
    _registrar(nome, script, fontes or (sorted(df["fonte"].unique()) if "fonte" in df.columns else ["todas"]),
               parametros or {})
    return df


def ler(nome, fontes=None, exigir=None):
    """Lê a tabela e confere no manifesto se ela existe para as fontes pedidas e se foi
    gerada com os parâmetros em `exigir`. Encerra com a instrução de correção se não."""
    m = _manifesto().get(nome)
    script = {"solucoes": "02_pylint.py", "avisos": "02_pylint.py", "paradigmas": "04_paradigma.py"}.get(
        nome, "05_consolidar.py")
    fontes_txt = " ".join(fontes or [])
    if not caminho(nome).exists() or m is None:
        sys.exit(f"Falta dados/tabelas/{nome}.csv. Rode: python src/{script} {fontes_txt}")
    for f in fontes or []:
        reg = m["fontes"].get(f)
        if reg is None:
            sys.exit(f"dados/tabelas/{nome}.csv não tem a fonte '{f}'. Rode: python src/{script} {f}")
        for chave, valor in (exigir or {}).items():
            if reg["parametros"].get(chave) != valor:
                sys.exit(f"dados/tabelas/{nome}.csv ({f}) foi gerada com {chave} = "
                         f"{reg['parametros'].get(chave)!r}, mas o valor atual é {valor!r}. "
                         f"Rode de novo: python src/{script} {fontes_txt}")
    df = pd.read_csv(caminho(nome))
    if fontes is not None and "fonte" in df.columns:
        df = df[df["fonte"].isin(fontes)]
    return df


# ------------------------------------------------------------------ relatórios
def tabela_md(df, casas=2):
    def fmt(v):
        if isinstance(v, float):
            if pd.isna(v):
                return "–"
            return str(int(v)) if v.is_integer() else f"{v:.{casas}f}".replace(".", ",")
        return str(v)
    colunas = list(df.columns)
    linhas = ["| " + " | ".join(map(str, colunas)) + " |", "|" + "|".join("---" for _ in colunas) + "|"]
    for row in df.itertuples(index=False):
        linhas.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(linhas)
