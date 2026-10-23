"""Etapa 2: roda o Pylint em todas as tentativas de cada fonte e grava as tabelas de smells.

Fontes:
    referencia   soluções de referência do Exercism (linha de base humana; tentativa 1)
    <modelo>     pasta dados/<modelo>/ gerada pela etapa 3 (todas as tentativas salvas)

Saídas (ver src/tabelas.py):
    dados/tabelas/solucoes.csv   uma linha por tentativa: status, aceita, sloc, erro de sintaxe
    dados/tabelas/avisos.csv     uma linha por aviso, com herdado_esqueleto
    dados/codigos/<fonte>/<slug>/t<n>/<arquivo>.py   o código analisado
    dados/codigos/_esqueleto/<slug>/<arquivo>.py     o esqueleto, analisado à parte
Cada fonte substitui só as próprias linhas nas tabelas; as outras fontes são mantidas.

Avisos herdados do esqueleto: o esqueleto do Exercism também é analisado. Um aviso da
solução é marcado como herdado quando o esqueleto puro gera um aviso com o mesmo símbolo e a
mesma mensagem (pareados um a um). Ex.: os `redefined-builtin` de list-ops vêm dos nomes
`map`, `filter`... que o esqueleto (e os testes) impõem. Não contam como herdados os avisos
que o esqueleto só tem por estar vazio (`unused-argument`, `unnecessary-pass`): se a solução
ainda os tiver, a responsabilidade é de quem resolveu.

Execução: um único processo do Pylint por fonte (bem mais rápido que um por arquivo), com o
`.pylintrc` do projeto. As verificações entre arquivos (duplicate-code, cyclic-import) ficam
desligadas, porque cada solução é independente; com elas desligadas o resultado é o mesmo de
rodar arquivo por arquivo.

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/02_pylint.py                         # fontes de config/analise.yaml
    python src/02_pylint.py referencia gpt-mini     # fontes específicas (perfil ou pasta)
    python src/02_pylint.py gpt-mini --jobs 1       # se o modo paralelo der problema
"""
import argparse
import ast
import collections
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
from radon.raw import analyze

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tabelas as T  # noqa: E402

NAO_HERDAVEIS = {"unused-argument", "unnecessary-pass"}
DESLIGADAS = "duplicate-code,cyclic-import"


def versao_pylint():
    saida = subprocess.run([sys.executable, "-m", "pylint", "--version"], capture_output=True, text=True).stdout
    return saida.splitlines()[0] if saida else "desconhecida"


def rodar_pylint(pasta, jobs):
    """Roda o Pylint numa pasta inteira e devolve {arquivo (Path absoluto): [avisos]}."""
    comando = [sys.executable, "-m", "pylint", "--output-format=json", "--score=n", "--recursive=y",
               f"--disable={DESLIGADAS}", f"--jobs={jobs}"]
    if T.PYLINTRC.exists():
        comando.append(f"--rcfile={T.PYLINTRC}")
    comando.append(str(pasta))
    r = subprocess.run(comando, capture_output=True, text=True, cwd=T.RAIZ)
    # o Pylint sai com código != 0 quando encontra avisos; isso é esperado
    try:
        msgs = json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        sys.exit(f"O Pylint não devolveu JSON válido. Erro:\n{r.stderr[-2000:]}")
    por_arquivo = collections.defaultdict(list)
    for m in msgs:
        p = Path(m["path"])
        por_arquivo[(p if p.is_absolute() else T.RAIZ / p).resolve()].append(m)
    return por_arquivo


def sloc(codigo):
    try:
        return analyze(codigo).sloc
    except Exception:  # noqa: BLE001  (código com erro de sintaxe)
        return None


def compila(codigo):
    try:
        ast.parse(codigo)
        return True
    except SyntaxError:
        return False


def avisos_do_esqueleto(exercicios, jobs):
    pasta = T.CODIGOS / "_esqueleto"
    shutil.rmtree(pasta, ignore_errors=True)
    for ex in exercicios:
        arq = pasta / ex["slug"] / ex["arquivo_solucao"]
        arq.parent.mkdir(parents=True, exist_ok=True)
        arq.write_text(ex["esqueleto"], encoding="utf-8")
    msgs = rodar_pylint(pasta, jobs)
    return {ex["slug"]: collections.Counter(
                (m["symbol"], m["message"])
                for m in msgs.get((pasta / ex["slug"] / ex["arquivo_solucao"]).resolve(), [])
                if m["symbol"] not in NAO_HERDAVEIS)
            for ex in exercicios}


def analisar_fonte(fonte, exercicios, esqueleto, jobs):
    pasta = T.CODIGOS / fonte
    shutil.rmtree(pasta, ignore_errors=True)
    linhas, arquivos = [], {}
    for t in T.tentativas(fonte, exercicios):
        ex, codigo = t["ex"], t["codigo"]
        linha = {"fonte": fonte, "slug": ex["slug"], "tentativa": t["tentativa"], "status": t["status"],
                 "aceita": t["aceita"], "ultima": t["ultima"], "tem_codigo": bool(codigo.strip()),
                 "erro_sintaxe": False, "sloc": None}
        if linha["tem_codigo"]:
            arq = pasta / ex["slug"] / f"t{t['tentativa']}" / ex["arquivo_solucao"]
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_text(codigo, encoding="utf-8")
            arquivos[(ex["slug"], t["tentativa"])] = arq.resolve()
            linha["erro_sintaxe"] = not compila(codigo)
            linha["sloc"] = sloc(codigo)
        linhas.append(linha)
    if not linhas:
        return None, None
    print(f"[{fonte}] {len(linhas)} tentativa(s) de {len({l['slug'] for l in linhas})} exercício(s); rodando o Pylint...")
    msgs = rodar_pylint(pasta, jobs)

    avisos = []
    for (slug, n), arq in arquivos.items():
        restantes = esqueleto[slug].copy()
        for m in msgs.get(arq, []):
            k = (m["symbol"], m["message"])
            herdado = restantes[k] > 0
            if herdado:
                restantes[k] -= 1
            avisos.append({"fonte": fonte, "slug": slug, "tentativa": n, "categoria": m["type"],
                           "codigo": m["message-id"], "simbolo": m["symbol"], "linha": m["line"],
                           "mensagem": m["message"], "herdado_esqueleto": herdado})
    df_s = pd.DataFrame(linhas)
    df_a = pd.DataFrame(avisos, columns=T.COLUNAS["avisos"])
    aceitas = df_s[df_s["aceita"]]
    av_ac = df_a.merge(aceitas[["slug", "tentativa"]], on=["slug", "tentativa"])
    print(f"[{fonte}] aceitas: {len(aceitas)} · avisos nas aceitas: {len(av_ac)} "
          f"(herdados do esqueleto: {int(av_ac['herdado_esqueleto'].sum())}) · "
          f"avisos em todas as tentativas: {len(df_a)}")
    return df_s, df_a


def main():
    parser = argparse.ArgumentParser(description="Roda o Pylint em todas as tentativas e grava as tabelas de smells.")
    parser.add_argument("fontes", nargs="*", help="referencia, perfis de config/modelos.yaml ou pastas em dados/ "
                                                  "(sem argumentos: as fontes de config/analise.yaml)")
    parser.add_argument("--jobs", type=int, default=0, help="processos do Pylint (0 = todos os núcleos)")
    args = parser.parse_args()

    exercicios = T.exercicios()
    fontes = T.resolver_fontes(args.fontes)
    parametros = {"pylint": versao_pylint(), "pylintrc": T.hash_arquivos(T.PYLINTRC),
                  "exercism_commit": T.commit_exercism(), "nao_herdaveis": sorted(NAO_HERDAVEIS)}
    print(f"Fontes: {', '.join(fontes)} · {parametros['pylint']} · .pylintrc {parametros['pylintrc']}")

    esqueleto = avisos_do_esqueleto(exercicios, args.jobs)
    for fonte in fontes:
        df_s, df_a = analisar_fonte(fonte, exercicios, esqueleto, args.jobs)
        if df_s is None:
            print(f"[{fonte}] nenhuma tentativa encontrada; nada gravado")
            continue
        T.salvar("solucoes", df_s, "02_pylint.py", [fonte], parametros)
        T.salvar("avisos", df_a, "02_pylint.py", [fonte], parametros)
    print(f"\nTabelas em {T.TABELAS}")


if __name__ == "__main__":
    main()
