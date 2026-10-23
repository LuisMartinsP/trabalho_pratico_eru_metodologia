"""Classificação de estilo (funcional, procedural, OO) adaptada para soluções curtas.

Baseada na regra de Dyer e Chauhan (2022), reimplementada fielmente em
src/paradigma_dyer.py. A regra original foi feita para arquivos de projetos reais;
em soluções de exercício ela classifica quase tudo como procedural (ver
docs/regra_dyer_explicada.md). Esta versão aplica as adaptações abaixo, definidas
ANTES de comparar com outras formas de classificação (ver docs/decisoes_metodologicas.md).

Adaptações (A1-A11), em relação a paradigma_dyer.py:
  A1  Analisa só o código ACRESCENTADO ao esqueleto: corpos das funções/métodos do
      esqueleto e as definições novas. A casca do esqueleto (def/class/assinaturas) é imposta.
  A2  Chamadas comuns (len, sum, outras funções) são neutras. Contam como funcional:
      recursão (a função chamar a si mesma) e chamar um parâmetro (ordem superior).
  A3  Métodos que modificam coleções (append, extend, pop, insert, remove, update...)
      contam como procedural, não como OO.
  A4  Laços for/while contam como procedural (no original, for contava como funcional).
  A5  in / not in são neutros (no original, funcional).
  A6  Funções embutidas são neutras (caso particular de A2).
  A7  Primeira atribuição a um nome é neutra; reatribuição e mutação
      (x += 1, x = x + 1, a[i] = v, obj.x = v) contam como procedural.
  A8  OO só para estrutura acrescentada: classe nova (+1), herança (+1) e cada método
      de classe nova (+1). Usar self dentro de classe do esqueleto é neutro.
  A9  Procedural e imperativo são uma categoria só (procedural).
  A10 Rótulo: o estilo com pelo menos 2/3 dos pontos; senão "misto"; sem pontos, "neutro".
  A11 try/except/raise/with são neutros (no original, OO).
Mantido do original: lambda, compreensões, geradores, yield, decorators,
map/filter/zip/enumerate/reduce/sorted/iter/any/all, functools/itertools e classe
iterável contam como funcional; cada comando dá no máximo 1 ponto por estilo.

Uso:
    from paradigma_adaptado import classificar
    classificar(codigo_solucao, codigo_esqueleto)
      -> {"paradigma": "funcional", "func": 6, "proc": 0, "oo": 0}
"""
import ast

FUNCIONAIS = {"map", "filter", "enumerate", "zip", "reduce", "sorted", "iter", "any", "all", "send"}
MUTADORES = {"append", "extend", "insert", "pop", "remove", "clear", "update", "add", "discard",
             "setdefault", "sort", "reverse", "popleft", "appendleft", "extendleft", "push"}
ESTILOS = ("func", "proc", "oo")


class Escopo:
    """Informação da função em análise: nome (para recursão), parâmetros (ordem superior)
    e nomes já atribuídos (para distinguir atribuição nova de reatribuição)."""

    def __init__(self, nome=None, parametros=(), metodo_de=None):
        self.nome = nome
        self.parametros = set(parametros)
        self.atribuidos = set(parametros)
        self.metodo_de = metodo_de  # nome do método, para recursão via self.metodo()


class Classificador:
    def __init__(self, funcionais=None):
        self.funcionais = set(FUNCIONAIS) | (funcionais or set())
        self.pontos = {"func": 0, "proc": 0, "oo": 0}

    # ---------------------------------------------------------- expressões
    def expr(self, e, esc):
        """Pontos de uma expressão (cada estilo no máximo 1, como no original)."""
        p = set()
        for n in ast.walk(e):
            if isinstance(n, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
                              ast.Yield, ast.YieldFrom)):
                p.add("func")
            elif isinstance(n, ast.Call):
                f = n.func
                if isinstance(f, ast.Name):
                    if f.id in self.funcionais:
                        p.add("func")
                    elif esc and (f.id == esc.nome or f.id in esc.parametros):
                        p.add("func")  # A2: recursão ou ordem superior
                elif isinstance(f, ast.Attribute):
                    if isinstance(f.value, ast.Name) and f.value.id in ("functools", "itertools"):
                        p.add("func")
                    elif f.attr in MUTADORES:
                        p.add("proc")  # A3
                    elif (esc and esc.metodo_de and isinstance(f.value, ast.Name)
                          and f.value.id == "self" and f.attr == esc.metodo_de):
                        p.add("func")  # A2: recursão de método
        return p

    # ------------------------------------------------------------ comandos
    def comando(self, s, esc):
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.funcao(s, metodo_de=None)
            return
        if isinstance(s, ast.ClassDef):
            self.classe_nova(s)
            return
        p = set()
        if isinstance(s, (ast.For, ast.AsyncFor, ast.While)):
            p.add("proc")  # A4
            p |= self.expr(s.iter if isinstance(s, (ast.For, ast.AsyncFor)) else s.test, esc)
            if isinstance(s, (ast.For, ast.AsyncFor)):
                self._marcar_atribuidos(s.target, esc)
            self._somar(p)
            for filho in s.body + s.orelse:
                self.comando(filho, esc)
            return
        if isinstance(s, (ast.If,)):
            self._somar(self.expr(s.test, esc))
            for filho in s.body + s.orelse:
                self.comando(filho, esc)
            return
        if isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try), ast.With, ast.AsyncWith)):
            if isinstance(s, (ast.With, ast.AsyncWith)):  # A11: neutro, só o conteúdo conta
                for item in s.items:
                    self._somar(self.expr(item.context_expr, esc))
            filhos = list(s.body) + list(getattr(s, "orelse", [])) + list(getattr(s, "finalbody", []))
            for h in getattr(s, "handlers", []):
                filhos += h.body
            for filho in filhos:
                self.comando(filho, esc)
            return
        if isinstance(s, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            alvos = s.targets if isinstance(s, ast.Assign) else [s.target]
            if s.value is not None:
                p |= self.expr(s.value, esc)
            if isinstance(s, ast.AugAssign):
                p.add("proc")  # A7: x += ...
            for a in alvos:
                if isinstance(a, (ast.Subscript, ast.Attribute)):
                    if not (isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name)
                            and a.value.id == "self" and esc and esc.metodo_de == "__init__"):
                        p.add("proc")  # A7: a[i] = v, obj.x = v (inicializar self.x no __init__ é neutro)
                elif esc and any(n.id in esc.atribuidos for n in ast.walk(a) if isinstance(n, ast.Name)):
                    p.add("proc")  # A7: reatribuição
                self._marcar_atribuidos(a, esc)
            self._somar(p)
            return
        # Expr, Return, Raise, Assert, Delete, Global... (A11 para raise): só o conteúdo
        for n in ast.iter_child_nodes(s):
            if isinstance(n, ast.expr):
                p |= self.expr(n, esc)
        self._somar(p)

    def _marcar_atribuidos(self, alvo, esc):
        if esc:
            esc.atribuidos |= {n.id for n in ast.walk(alvo) if isinstance(n, ast.Name)}

    def _somar(self, p):
        for estilo in p:
            self.pontos[estilo] += 1

    # ------------------------------------------------- funções e classes
    def funcao(self, f, metodo_de=None, corpo=None):
        if f.decorator_list:
            self.pontos["func"] += 1 if not metodo_de else 0  # decorators de função contam funcional
        args = f.args.posonlyargs + f.args.args + f.args.kwonlyargs
        nomes = [a.arg for a in args] + [a.arg for a in (f.args.vararg, f.args.kwarg) if a]
        esc = Escopo(nome=None if metodo_de else f.name, parametros=[n for n in nomes if n != "self"],
                     metodo_de=metodo_de)
        for s in (corpo if corpo is not None else f.body):
            self.comando(s, esc)

    def classe_nova(self, c):
        """A8: classe criada por quem resolveu."""
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


def classificar(solucao, esqueleto=""):
    arv = ast.parse(solucao)
    esq = _defs(ast.parse(esqueleto).body) if esqueleto else {}
    funcionais = set()
    for n in arv.body:
        if isinstance(n, ast.ImportFrom) and n.module in ("functools", "itertools"):
            funcionais |= {a.asname or a.name for a in n.names}
    cl = Classificador(funcionais)

    for n in arv.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            continue
        base = esq.get(getattr(n, "name", None))
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and isinstance(base, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cl.funcao(n)  # A1: função do esqueleto -> só o corpo conta (a casca não pontua)
        elif isinstance(n, ast.ClassDef) and isinstance(base, ast.ClassDef):
            metodos_esq = {m.name for m in base.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for s in n.body:  # A1/A8: classe do esqueleto -> só o conteúdo dos métodos
                if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if s.name not in metodos_esq:
                        cl.pontos["oo"] += 1  # método novo numa classe do esqueleto
                    cl.funcao(s, metodo_de=s.name)
                elif isinstance(s, ast.ClassDef):
                    cl.classe_nova(s)
                else:
                    cl.comando(s, None)
        else:
            cl.comando(n, Escopo())  # definição nova ou comando solto

    pts = cl.pontos
    total = sum(pts.values())
    if total == 0:
        rotulo = "neutro"
    else:
        estilo, valor = max(pts.items(), key=lambda kv: kv[1])
        nomes = {"func": "funcional", "proc": "procedural", "oo": "oo"}
        rotulo = nomes[estilo] if valor >= 2 * total / 3 else "misto"
    return {"paradigma": rotulo, **pts}
