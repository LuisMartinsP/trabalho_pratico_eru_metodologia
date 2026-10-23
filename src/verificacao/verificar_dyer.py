"""Confere se a tradução em Python (src/paradigma_dyer.py) dá o mesmo resultado que a
consulta original em Boa, usando o conjunto de testes oficial dos autores.

Os autores mantêm o repositório github.com/psybers/py-classify-tests, usado pelo
script boa/test-classify.sh do pacote de replicação. O nome de cada arquivo de teste
traz o placar que a consulta Boa deve produzir:

    <nome>-<funcional>-<oo>-<procedural>-<imperativo>-<comandos>.py

Este script clona esse repositório, roda a tradução em cada arquivo e compara os cinco
números. Arquivos que não são Python 3 válido (alguns testes são Python 2) são listados
à parte, porque o Python 3 não consegue lê-los.

Uso (a partir da raiz do projeto):
    python src/verificacao/verificar_dyer.py               # clona em dados/_cache/py-classify-tests
    python src/verificacao/verificar_dyer.py <pasta>       # usa uma cópia já baixada dos testes
"""
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
from paradigma_dyer import classificar  # noqa: E402

REPO = "https://github.com/psybers/py-classify-tests.git"
PASTA = RAIZ / "dados" / "_cache" / "py-classify-tests"


def main():
    pasta = Path(sys.argv[1]) if len(sys.argv) > 1 else PASTA
    if not any(pasta.glob("*.py")):
        if pasta.exists():
            sys.exit(f"A pasta {pasta} existe mas não tem os testes (clone incompleto?). "
                     "Apague-a e rode de novo.")
        pasta.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--depth", "1", REPO, str(pasta)], check=True)
    commit = subprocess.run(["git", "-C", str(pasta), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip() or "desconhecido"

    iguais, diferentes, py2, sem_gabarito = [], [], [], []
    for arquivo in sorted(pasta.glob("*.py")):
        m = re.match(r"(.+?)-(\d+)-(\d+)-(\d+)-(\d+)-(\d+)\.py$", arquivo.name)
        if not m:
            sem_gabarito.append(arquivo.name)
            continue
        esperado = tuple(map(int, m.groups()[1:]))
        try:
            r = classificar(arquivo.read_text(encoding="utf-8"))
        except SyntaxError:
            py2.append(arquivo.name)
            continue
        obtido = (r["func"], r["oo"], r["proc"], r["imp"], r["stmts"])
        (iguais if obtido == esperado else diferentes).append((arquivo.name, esperado, obtido))

    validos = len(iguais) + len(diferentes)
    print(f"Testes oficiais (commit {commit[:10]}): {validos + len(py2)} com gabarito")
    print(f"  Python 3 válido: {validos} · iguais ao Boa: {len(iguais)} · diferentes: {len(diferentes)}")
    print(f"  não são Python 3 válido (não comparáveis): {len(py2)}")
    print(f"  sem gabarito no nome: {len(sem_gabarito)}")
    print("\nFormato: (funcional, OO, procedural, imperativo, comandos)")
    for nome, e, o in diferentes:
        print(f"  DIFERENTE  {nome:40s} esperado {e}  obtido {o}")
    for nome in py2:
        print(f"  não comparável  {nome}")


if __name__ == "__main__":
    main()
