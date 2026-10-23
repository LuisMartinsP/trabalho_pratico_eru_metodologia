"""Classificação de estilo por OPERAÇÃO (versão D), derivada de src/paradigma_adaptado.py.

Motivo (ver docs/decisoes_metodologicas.md, seção 11): na regra adaptada cada COMANDO
dá no máximo 1 ponto por estilo. O estilo funcional comprime várias operações num
comando só (uma compreensão itera, filtra e produz), enquanto o procedural espalha as
mesmas operações em vários comandos (for, if, append). Resultado: a mesma tarefa vale
1 ponto funcional ou 2-3 procedurais, e o rótulo "funcional" fica apoiado em 1-2 pontos.

Princípio desta versão: cada OPERAÇÃO vale 1 ponto, no estilo em que foi escrita, e os
pontos de um mesmo comando se somam (sem o limite de 1 por estilo). As operações são:

    operação           forma funcional                       forma procedural
    iterar             cláusula for de compreensão/gerador    laço for / while
    filtrar            cláusula if de compreensão/gerador     if dentro de um laço
    produzir/acumular  expressão produzida pela compreensão   append/add/..., x += ..., a[i] = v,
                                                              reatribuição de nome

Pontuação das construções funcionais nomeadas, pela mesma tabela:
    map(f, xs)        iterar + produzir             = 2
    filter(p, xs)     iterar + filtrar + produzir   = 3
    reduce(f, xs)     iterar + acumular             = 2
    lambda            +1 (função como valor), exceto quando é o argumento de map/filter/reduce,
                      onde já está contada como a operação de produzir/filtrar/acumular
    recursão, chamar um parâmetro (ordem superior), yield, decorator,
    outras funções de functools/itertools, classe iterável           +1 cada

Neutros (mudam em relação à regra adaptada): sum/min/max/any/all/sorted/enumerate/zip/iter
deixam de pontuar sozinhos. Eles só agregam ou auxiliam a iteração, que já é contada pelo
gerador ou pelo laço que os acompanha (ex.: `for i, x in enumerate(xs)` é um laço; `any(p(x)
for x in xs)` é um gerador). O operador ternário continua neutro nos dois estilos.

Mantido da regra adaptada (A1, A2, A3, A7, A8, A9, A11): só o código acrescentado ao esqueleto
é analisado; chamadas comuns são neutras; mutadores de coleção são procedurais; reatribuição
e mutação são procedurais (inicializar self.x no __init__ é neutro); OO só por estrutura
acrescentada; try/except/raise/with são neutros. O rótulo continua sendo o estilo com pelo
menos 2/3 dos pontos (funcional + procedural); OO é decidido por classes novas em 04_paradigma.py.

Limitações conhecidas (casos que NÃO empatam; ver src/verificacao/verificar_equivalencia.py):
    - min/max sobre um gerador (1 operação de seleção escondida no agregador) contra o laço
      com comparação e atualização;
    - recursão contra laço: a recursão vale 1 por chamada, o laço equivalente vale mais.

Uso:
    from paradigma_operacoes import classificar
    classificar(codigo_solucao, codigo_esqueleto)
      -> {"paradigma": "funcional", "func": 6, "proc": 0, "oo": 0}
"""
import ast

PESO_NOMEADAS = {"map": 2, "filter": 3, "reduce": 2}
MUTADORES = {"append", "extend", "insert", "pop", "remove", "clear", "update", "add", "discard",
             "setdefault", "sort", "reverse", "popleft", "appendleft", "extendleft", "push"}
COMPREENSOES = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)


class Escopo:
    def __init__(self, nome=None, parametros=(), metodo_de=None):
        self.nome = nome
        self.parametros = set(parametros)
        self.atribuidos = set(parametros)
        self.metodo_de = metodo_de


class Classificador:
    def __init__(self, importadas=None):
        # nomes importados de functools/itertools (from functools import reduce -> "reduce")
        self.importadas = importadas or set()
        self.pontos = {"func": 0, "proc": 0, "oo": 0}

    # ---------------------------------------------------------- expressões
    def _peso_nomeada(self, nome):
        if nome in PESO_NOMEADAS:
            return PESO_NOMEADAS[nome]
        return 1 if nome in self.importadas else 0

    def expr(self, e, esc):
        """Soma as operações de uma expressão: {"func": n, "proc": n}."""
        p = {"func": 0, "proc": 0}
        lambdas_contadas = set()  # lambdas que são o argumento de map/filter/reduce
        for n in ast.walk(e):
            if isinstance(n, ast.Call):
                f = n.func
                peso = 0
                if isinstance(f, ast.Name):
                    peso = self._peso_nomeada(f.id)
                    if not peso and esc and (f.id == esc.nome or f.id in esc.parametros):
                        peso = 1  # recursão ou ordem superior
                    if f.id in PESO_NOMEADAS or f.id in self.importadas:
                        nome_base = f.id
                    else:
                        nome_base = None
                elif isinstance(f, ast.Attribute):
                    nome_base = None
                    if isinstance(f.value, ast.Name) and f.value.id in ("functools", "itertools"):
                        peso = PESO_NOMEADAS.get(f.attr, 1)
                        nome_base = f.attr
                    elif f.attr in MUTADORES:
                        p["proc"] += 1
                    elif (esc and esc.metodo_de and isinstance(f.value, ast.Name)
                          and f.value.id == "self" and f.attr == esc.metodo_de):
                        peso = 1  # recursão de método
                else:
                    nome_base = None
                p["func"] += peso
                if nome_base in PESO_NOMEADAS:
                    lambdas_contadas |= {id(a) for a in n.args if isinstance(a, ast.Lambda)}
            elif isinstance(n, COMPREENSOES):
                # iterar (cada for) + filtrar (cada if) + produzir (1)
                p["func"] += len(n.generators) + sum(len(g.ifs) for g in n.generators) + 1
            elif isinstance(n, (ast.Yield, ast.YieldFrom)):
                p["func"] += 1
        p["func"] += sum(1 for n in ast.walk(e) if isinstance(n, ast.Lambda) and id(n) not in lambdas_contadas)
        return p

    # ------------------------------------------------------------ comandos
    def comando(self, s, esc, em_laco=False):
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.funcao(s, metodo_de=None)
            return
        if isinstance(s, ast.ClassDef):
            self.classe_nova(s)
            return
        if isinstance(s, (ast.For, ast.AsyncFor, ast.While)):
            self.pontos["proc"] += 1  # iterar
            self._somar(self.expr(s.iter if isinstance(s, (ast.For, ast.AsyncFor)) else s.test, esc))
            if isinstance(s, (ast.For, ast.AsyncFor)):
                self._marcar_atribuidos(s.target, esc)
            for filho in s.body + s.orelse:
                self.comando(filho, esc, em_laco=True)
            return
        if isinstance(s, ast.If):
            if em_laco:
                self.pontos["proc"] += 1  # filtrar dentro de um laço
            self._somar(self.expr(s.test, esc))
            for filho in s.body + s.orelse:
                self.comando(filho, esc, em_laco)
            return
        if isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try), ast.With, ast.AsyncWith)):
            if isinstance(s, (ast.With, ast.AsyncWith)):
                for item in s.items:
                    self._somar(self.expr(item.context_expr, esc))
            filhos = list(s.body) + list(getattr(s, "orelse", [])) + list(getattr(s, "finalbody", []))
            for h in getattr(s, "handlers", []):
                filhos += h.body
            for filho in filhos:
                self.comando(filho, esc, em_laco)
            return
        if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            alvos = s.targets if isinstance(s, ast.Assign) else [s.target]
            if s.value is not None:
                self._somar(self.expr(s.value, esc))
            muta = isinstance(s, ast.AugAssign)  # x += ...
            for a in alvos:
                if isinstance(a, (ast.Subscript, ast.Attribute)):
                    if not (isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name)
                            and a.value.id == "self" and esc and esc.metodo_de == "__init__"):
                        muta = True  # a[i] = v, obj.x = v
                elif esc and any(n.id in esc.atribuidos for n in ast.walk(a) if isinstance(n, ast.Name)):
                    muta = True  # reatribuição
                self._marcar_atribuidos(a, esc)
            if muta:
                self.pontos["proc"] += 1  # produzir/acumular por mutação (1 por comando)
            return
        for n in ast.iter_child_nodes(s):
            if isinstance(n, ast.expr):
                self._somar(self.expr(n, esc))

    def _marcar_atribuidos(self, alvo, esc):
        if esc:
            esc.atribuidos |= {n.id for n in ast.walk(alvo) if isinstance(n, ast.Name)}

    def _somar(self, p):
        for estilo, v in p.items():
            self.pontos[estilo] += v

    # ------------------------------------------------- funções e classes
    def funcao(self, f, metodo_de=None):
        if f.decorator_list and not metodo_de:
            self.pontos["func"] += 1
        args = f.args.posonlyargs + f.args.args + f.args.kwonlyargs
        nomes = [a.arg for a in args] + [a.arg for a in (f.args.vararg, f.args.kwarg) if a]
        esc = Escopo(nome=None if metodo_de else f.name, parametros=[n for n in nomes if n != "self"],
                     metodo_de=metodo_de)
        for s in f.body:
            self.comando(s, esc)

    def classe_nova(self, c):
        self.pontos["oo"] += 1 + (1 if c.bases else 0)
        metodos = set()
        for s in c.body:
            if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metodos.add(s.name)
                self.pontos["oo"] += 1
                self.funcao(s, metodo_de=s.name)
            elif isinstance(s, ast.ClassDef):
                self.classe_nova(s)
            else:
                self.comando(s, None)
        if {"__iter__", "__next__"} <= metodos:
            self.pontos["func"] += 1


def _defs(corpo):
    return {n.name: n for n in corpo if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def rotulo(func, proc):
    total = func + proc
    if total == 0:
        return "neutro"
    if func >= 2 * total / 3:
        return "funcional"
    if proc >= 2 * total / 3:
        return "procedural"
    return "misto"


def classificar(solucao, esqueleto=""):
    arv = ast.parse(solucao)
    esq = _defs(ast.parse(esqueleto).body) if esqueleto else {}
    importadas = set()
    for n in arv.body:
        if isinstance(n, ast.ImportFrom) and n.module in ("functools", "itertools"):
            importadas |= {a.asname or a.name for a in n.names}
    cl = Classificador(importadas)

    for n in arv.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        base = esq.get(getattr(n, "name", None))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and isinstance(base, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cl.funcao(n)
        elif isinstance(n, ast.ClassDef) and isinstance(base, ast.ClassDef):
            metodos_esq = {m.name for m in base.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for s in n.body:
                if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if s.name not in metodos_esq:
                        cl.pontos["oo"] += 1
                    cl.funcao(s, metodo_de=s.name)
                elif isinstance(s, ast.ClassDef):
                    cl.classe_nova(s)
                else:
                    cl.comando(s, None)
        else:
            cl.comando(n, Escopo())

    pts = cl.pontos
    return {"paradigma": rotulo(pts["func"], pts["proc"]), **pts}
