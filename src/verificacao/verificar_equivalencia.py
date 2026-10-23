"""Verifica a regra por operação (src/paradigma_operacoes.py) com pares equivalentes.

Cada par resolve a mesma tarefa em estilo funcional e em estilo procedural. A regra está
correta para o par quando o placar funcional da forma funcional é igual ao placar
procedural da forma procedural (e cada forma não tem pontos do outro estilo).
Os pares em LIMITACOES são casos conhecidos que não empatam; eles são impressos para
registro, mas não reprovam a verificação.

Uso: python src/verificacao/verificar_equivalencia.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paradigma_adaptado  # noqa: E402
import paradigma_operacoes  # noqa: E402

D = "def f(xs, p):\n"  # g é uma função comum (não parâmetro): chamá-la é neutro

PARES = {
    "mapear": (
        D + "    return [g(x) for x in xs]\n",
        D + "    r = []\n    for x in xs:\n        r.append(g(x))\n    return r\n"),
    "mapear com map": (
        D + "    return list(map(g, xs))\n",
        D + "    r = []\n    for x in xs:\n        r.append(g(x))\n    return r\n"),
    "map com lambda": (
        D + "    return list(map(lambda x: x * 2, xs))\n",
        D + "    r = []\n    for x in xs:\n        r.append(x * 2)\n    return r\n"),
    "filtrar": (
        D + "    return [x for x in xs if x > 0]\n",
        D + "    r = []\n    for x in xs:\n        if x > 0:\n            r.append(x)\n    return r\n"),
    "filtrar com filter": (
        D + "    return list(filter(lambda x: x > 0, xs))\n",
        D + "    r = []\n    for x in xs:\n        if x > 0:\n            r.append(x)\n    return r\n"),
    "mapear e filtrar": (
        D + "    return [x * 2 for x in xs if x > 0]\n",
        D + "    r = []\n    for x in xs:\n        if x > 0:\n            r.append(x * 2)\n    return r\n"),
    "somar": (
        D + "    return sum(x * 2 for x in xs)\n",
        D + "    t = 0\n    for x in xs:\n        t += x * 2\n    return t\n"),
    "contar com filtro": (
        D + "    return sum(1 for x in xs if x > 0)\n",
        D + "    t = 0\n    for x in xs:\n        if x > 0:\n            t += 1\n    return t\n"),
    "existe (any)": (
        D + "    return any(x > 0 for x in xs)\n",
        D + "    for x in xs:\n        if x > 0:\n            return True\n    return False\n"),
    "todos (all)": (
        D + "    return all(x > 0 for x in xs)\n",
        D + "    for x in xs:\n        if x <= 0:\n            return False\n    return True\n"),
    "juntar texto": (
        D + "    return ''.join(c.upper() for c in xs)\n",
        D + "    s = ''\n    for c in xs:\n        s += c.upper()\n    return s\n"),
    "montar dicionário": (
        D + "    return {x: g(x) for x in xs}\n",
        D + "    d = {}\n    for x in xs:\n        d[x] = g(x)\n    return d\n"),
    "aninhado": (
        D + "    return [[c * 2 for c in linha] for linha in xs]\n",
        D + "    r = []\n    for linha in xs:\n        nova = []\n        for c in linha:\n"
            "            nova.append(c * 2)\n        r.append(nova)\n    return r\n"),
    "duas fontes": (
        D + "    return [(a, b) for a in xs for b in p]\n",
        D + "    r = []\n    for a in xs:\n        for b in p:\n            r.append((a, b))\n    return r\n"),
    "reduzir": (
        "from functools import reduce\n" + D + "    return reduce(lambda a, x: a * x, xs, 1)\n",
        D + "    a = 1\n    for x in xs:\n        a = a * x\n    return a\n"),
    "com enumerate": (
        D + "    return [i * x for i, x in enumerate(xs)]\n",
        D + "    r = []\n    for i, x in enumerate(xs):\n        r.append(i * x)\n    return r\n"),
}

LIMITACOES = {
    "máximo": (
        D + "    return max(g(x) for x in xs)\n",
        D + "    m = None\n    for x in xs:\n        v = g(x)\n        if m is None or v > m:\n            m = v\n    return m\n"),
    "recursão × laço": (
        "def f(n):\n    return 1 if n <= 1 else n * f(n - 1)\n",
        "def f(n):\n    r = 1\n    while n > 1:\n        r *= n\n        n -= 1\n    return r\n"),
}


def placar(mod, codigo):
    r = mod.classificar(codigo)
    return r["func"], r["proc"]


def main():
    falhas = 0
    print(f"{'par':22s} | {'adaptada (C): func × proc':27s} | {'operação (D): func × proc':27s} | D empata?")
    for grupo, pares in (("", PARES), ("limitação conhecida: ", LIMITACOES)):
        for nome, (funcional, procedural) in pares.items():
            ca, pa_ = placar(paradigma_adaptado, funcional), placar(paradigma_adaptado, procedural)
            co, po = placar(paradigma_operacoes, funcional), placar(paradigma_operacoes, procedural)
            ok = co[0] == po[1] and co[1] == 0 and po[0] == 0
            if not ok and not grupo:
                falhas += 1
            print(f"{grupo + nome:22s} | {str(ca):>12s} × {str(pa_):12s} | {str(co):>12s} × {str(po):12s} | "
                  f"{'sim' if ok else 'NÃO'}")
    print(f"\n{len(PARES) - falhas}/{len(PARES)} pares empatam na regra por operação.")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
