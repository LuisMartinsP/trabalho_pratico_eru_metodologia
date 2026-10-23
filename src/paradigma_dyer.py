"""Tradução fiel, para Python, da regra de Dyer e Chauhan (2022).

Origem: boa/py-classify.boa, do pacote de replicação de
    Dyer, R.; Chauhan, J. "An Exploratory Study on the Predominant Programming
    Paradigms in Python Code". ESEC/FSE 2022. doi:10.5281/zenodo.6975558 (CC BY 4.0)

O original é escrito na linguagem Boa e só roda na infraestrutura Boa. Aqui a
mesma lógica é aplicada à árvore sintática do Python (módulo `ast`). Cada trecho
traz a referência às linhas do arquivo original. Esta versão NÃO tem nenhuma
adaptação: é para conferência e para reportar a regra original.

Ideia geral: cada pedaço do código soma pontos em quatro paradigmas
(funcional, OO, procedural, imperativo); o arquivo recebe o paradigma com
mais pontos (empate = "misto").

Uso:
    from paradigma_dyer import classificar
    classificar(codigo)  ->  {"paradigma": "procedural", "func": 1, "oo": 0, "proc": 2, "imp": 0, "stmts": 2}
"""
import ast
from dataclasses import dataclass, field

# py-classify.boa, linhas 41-55: funções consideradas "funcionais" quando chamadas sem receptor
FUNCIONAIS = {"map", "filter", "enumerate", "zip", "reduce", "sorted", "iter", "any", "all", "send"}


@dataclass
class Contagem:
    """py-classify.boa, linha 3: type Counts = { func, oo, proc, imp, stmts }."""
    func: int = 0
    oo: int = 0
    proc: int = 0
    imp: int = 0
    stmts: int = 0

    def __add__(self, o):  # linhas 71-74: addCounts
        return Contagem(self.func + o.func, self.oo + o.oo, self.proc + o.proc,
                        self.imp + o.imp, self.stmts + o.stmts)

    def limitada(self):
        """Linhas 57-69: clampCounts. Cada paradigma vale no máximo 1; se algum
        paradigma "de verdade" (func, oo, proc) apareceu, o imperativo é zerado."""
        c = Contagem(int(self.func > 0), int(self.oo > 0), int(self.proc > 0), int(self.imp > 0), self.stmts)
        if c.func or c.oo or c.proc:
            c.imp = 0
        return c


@dataclass
class Contexto:
    classes: set = field(default_factory=set)   # linhas 466-469: nomes de classes do projeto
    modulos: set = field(default_factory=set)   # linhas 424-435: módulos importados ("namespaces")
    funcionais: set = field(default_factory=lambda: set(FUNCIONAIS))


def _filhos_expr(e):
    return [n for n in ast.iter_child_nodes(e) if isinstance(n, ast.expr)]


# --------------------------------------------------------------- expressões
def classificar_expr(e, ctx):
    """Linhas 80-157: classifyExpr."""
    c = Contagem()
    if isinstance(e, (ast.Yield, ast.YieldFrom, ast.GeneratorExp)):
        # linhas 84-90: YIELD, GENERATOR -> +1 funcional
        c.func += 1
        filhos = _filhos_expr(e)
    elif isinstance(e, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in e.ops):
        # linhas 84-90: IN, NOT_IN -> +1 funcional
        c.func += 1
        filhos = _filhos_expr(e)
    elif isinstance(e, (ast.Lambda, ast.ListComp, ast.SetComp, ast.DictComp)):
        # linhas 128-134: LAMBDA, ARRAY_COMPREHENSION -> +1 funcional
        c.func += 1
        filhos = _filhos_expr(e)
    elif isinstance(e, ast.Call):
        # linhas 92-119: METHODCALL
        f = e.func
        if isinstance(f, ast.Name):  # chamada sem receptor: f(...)
            if f.id in ctx.funcionais:
                c.func += 1          # linhas 94-95: map/filter/... -> funcional
            elif f.id in ctx.classes:
                c.oo += 1            # linhas 104-110: nome de classe conhecida (instanciação) -> OO
            else:
                c.proc += 1          # linhas 111-112: qualquer outra função -> procedural
            filhos = []
        elif isinstance(f, ast.Attribute):  # chamada com receptor: x.metodo(...)
            receptor = f.value.id if isinstance(f.value, ast.Name) else None
            if receptor in ("functools", "itertools"):
                c.func += 1          # linhas 96-97
            elif receptor in ctx.modulos:
                c.proc += 1          # linhas 99-100: função de módulo importado (math.sqrt) -> procedural
            else:
                c.oo += 1            # linhas 101-102: método de objeto (lista.append) -> OO
            # linhas 115-118: o Boa só percorre os ARGUMENTOS da chamada; o objeto antes do
            # ponto (o receptor) não é analisado. Ex.: em KMeans(...).fit(x), KMeans(...) não conta
            # (conferido com o teste oficial analyze_kmeans).
            filhos = []
        else:
            c.imp += 1
            filhos = [f]
        filhos += list(e.args) + [k.value for k in e.keywords]   # linhas 115-118: argumentos
    elif isinstance(e, ast.Attribute):
        # linhas 136-145: VARACCESS com receptor: self.x -> OO; outro.x -> imperativo
        if isinstance(e.value, ast.Name) and e.value.id == "self":
            c.oo += 1
        else:
            c.imp += 1
        filhos = [e.value]
    else:
        # linhas 147-153: qualquer outra expressão (variável, número, operação) -> imperativo
        c.imp += 1
        filhos = _filhos_expr(e)
    for filho in filhos:
        c = c + classificar_expr(filho, ctx)
    return c.limitada()  # linha 156


def _exprs_do_comando(s):
    return [n for n in ast.iter_child_nodes(s) if isinstance(n, ast.expr)]


def _bloco(comandos, ctx, em_classe=False, em_controle=True):
    """Classifica uma sequência de comandos. em_controle=True para corpos de if/for/while/try/with."""
    c = Contagem()
    for s in comandos:
        c = c + classificar_comando(s, ctx, em_classe, em_controle)
    return c


# ----------------------------------------------------------------- comandos
def classificar_comando(s, ctx, em_classe=False, em_controle=False):
    """Linhas 159-321: classifyStmt. Todo comando começa com stmts=1."""
    if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # Só métodos DIRETOS da classe contam como OO (tratados em classificar_classe).
        # Uma função definida dentro de outra função, mesmo dentro de um método,
        # é procedural (conferido com o teste oficial class-with-nested-proc).
        return classificar_funcao(s, ctx, em_classe=False)
    if isinstance(s, ast.ClassDef):
        return classificar_classe(s, ctx)
    if isinstance(s, (ast.Import, ast.ImportFrom)):
        return Contagem()  # linhas 253-254: imports não contam aqui
    if isinstance(s, (ast.Pass, ast.Break, ast.Continue)) and em_controle:
        # Dentro de if/for/while/try/with, a AST do Boa não traz pass/break/continue como
        # comando (testes oficiais pass-python e break-python). Direto no corpo de função ou
        # classe, eles contam normalmente (testes class, class-with-methods e method).
        return Contagem()

    c = Contagem(stmts=1)

    # linhas 163-174: TRY, CATCH, RAISE, FINALLY, WITH -> OO = 1, imperativo = 0
    if isinstance(s, (ast.Try, getattr(ast, "TryStar", ast.Try), ast.Raise, ast.With, ast.AsyncWith)):
        for e in _exprs_do_comando(s):
            c = c + classificar_expr(e, ctx)
        if isinstance(s, (ast.With, ast.AsyncWith)):
            for item in s.items:
                c = c + classificar_expr(item.context_expr, ctx)
        c.oo, c.imp = 1, 0
        corpo = list(getattr(s, "body", []))
        for h in getattr(s, "handlers", []):  # cada "except" é um CATCH
            ch = Contagem(stmts=1, oo=1)
            if h.type is not None:
                ch = ch + classificar_expr(h.type, ctx)
            ch.oo, ch.imp = 1, 0
            c = c + ch + _bloco(h.body, ctx, em_classe)
        corpo += list(getattr(s, "orelse", []))
        if getattr(s, "finalbody", None):  # FINALLY
            c = c + Contagem(stmts=1, oo=1) + _bloco(s.finalbody, ctx, em_classe)
        return c + _bloco(corpo, ctx, em_classe)

    # linhas 176-191: FOREACH (o for do Python) -> funcional = 1, imperativo = 0;
    # se tiver mais de um "filho" (comandos do corpo, mais o bloco else, se houver), +1 imperativo
    # (conferido com os testes oficiais for, for-else e break-python).
    if isinstance(s, (ast.For, ast.AsyncFor)):
        c = c + classificar_expr(s.iter, ctx)
        c.func, c.imp = 1, 0
        c = c + _bloco(s.body, ctx, em_classe)
        if s.orelse:
            c = c + _bloco(s.orelse, ctx, em_classe)
        if len(s.body) + (1 if s.orelse else 0) > 1:
            c.imp += 1
            c.stmts += 1
        return c

    # linhas 217-223: RETURN -> soma a expressão, imperativo = 0
    if isinstance(s, ast.Return):
        if s.value is not None:
            c = c + classificar_expr(s.value, ctx)
        c.imp = 0
        return c

    # linhas 225-238: IF, WHILE -> soma condição e corpo; um bloco "else" soma +1 imperativo.
    # No Boa, o "elif" é um IF aninhado (não um bloco), então não soma o +1
    # (conferido com o teste oficial if-elif). Em Python, o elif aparece como um If
    # sozinho no orelse, na mesma coluna do if de cima.
    if isinstance(s, (ast.If, ast.While)):
        c = c + classificar_expr(s.test, ctx)
        c = c + _bloco(s.body, ctx, em_classe)
        if s.orelse:
            c = c + _bloco(s.orelse, ctx, em_classe)
            eh_elif = (isinstance(s, ast.If) and len(s.orelse) == 1 and isinstance(s.orelse[0], ast.If)
                       and s.orelse[0].col_offset == s.col_offset)
            if not eh_elif:
                c.imp += 1
                c.stmts += 1
        return c

    # linhas 240-250: ASSERT, DEL -> soma e limita
    if isinstance(s, (ast.Assert, ast.Delete)):
        for e in _exprs_do_comando(s):
            c = c + classificar_expr(e, ctx)
        return c.limitada()

    # linhas 252-277: EXPRESSION (chamadas soltas e atribuições); docstrings não contam.
    # No Boa, uma atribuição é UMA expressão (ASSIGN), que cai no caso padrão (imperativo).
    if isinstance(s, (ast.Expr, ast.Assign, ast.AugAssign, ast.AnnAssign)):
        if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str):
            return Contagem(stmts=1)
        partes = Contagem()
        for e in _exprs_do_comando(s):
            partes = partes + classificar_expr(e, ctx)
        if not isinstance(s, ast.Expr):
            partes = partes + Contagem(imp=1)  # o próprio ASSIGN
        return c + partes.limitada()

    # linhas 279-281: GLOBAL -> +1 imperativo
    if isinstance(s, (ast.Global, ast.Nonlocal)):
        c.imp += 1
        return c

    # linhas 283-317: qualquer outro comando (pass, break, continue...) -> +1 imperativo
    c.imp += 1
    for e in _exprs_do_comando(s):
        c = c + classificar_expr(e, ctx)
    return c + _bloco([n for n in ast.iter_child_nodes(s) if isinstance(n, ast.stmt)], ctx, em_classe)


# ------------------------------------------------------ funções e classes
def _usado_como_funcao(nome, funcao, ctx):
    """Linhas 325-348: usedAsFunction. Conta comandos que chamam um PARÂMETRO como
    função (função de ordem superior) e que ainda não tinham ponto funcional."""
    total, usado = 0, False
    for s in ast.walk(funcao):
        if not isinstance(s, ast.stmt) or s is funcao:
            continue
        chama = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == nome
                    for e in _exprs_do_comando(s) for n in ast.walk(e))
        if chama:
            usado = True
            if classificar_comando(s, ctx).func == 0:
                total += 1
    return total, usado


def classificar_funcao(f, ctx, em_classe):
    """Linhas 350-375: classifyMethod."""
    c = Contagem(stmts=1)
    for _ in f.decorator_list:      # linhas 353-356: cada decorator +1 funcional
        c.func += 1
        c.stmts += 1
    c = c + _bloco(f.body, ctx, em_classe, em_controle=False)
    # linhas 363-366: TODOS os comandos da função viram pontos OO (se for método)
    # ou procedurais (se for função solta). É o que domina em soluções pequenas.
    if em_classe:
        c.oo = c.stmts
    else:
        c.proc = c.stmts
    algum = False                   # linhas 368-372: parâmetros usados como função
    for a in f.args.posonlyargs + f.args.args + f.args.kwonlyargs:
        total, usado = _usado_como_funcao(a.arg, f, ctx)
        c.func += total
        algum = algum or usado
    if algum:
        c.func += 1
    return c


def classificar_classe(cls, ctx):
    """Linhas 389-418: classifyDecl. A classe já começa com +1 OO."""
    c = Contagem(oo=1, stmts=1)
    for _ in cls.decorator_list:
        c.func += 1
        c.stmts += 1
    metodos = set()
    for s in cls.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metodos.add(s.name)
            m = classificar_funcao(s, ctx, em_classe=True)
            m.oo = max(m.oo, m.stmts)      # linhas 403-407
            c = c + m
        elif isinstance(s, ast.ClassDef):
            c = c + classificar_classe(s, ctx)  # linhas 409-412: classes aninhadas
        else:
            sc = classificar_comando(s, ctx, em_classe=True, em_controle=False)
            sc.oo = max(sc.oo, sc.stmts)   # linhas 397-401
            c = c + sc
    if {"__iter__", "__next__"} <= metodos:  # linhas 377-387 e 414-415: classe iterável
        c.func += 3
    return c


# ------------------------------------------------------------------ rótulo
def rotular(c):
    """Linhas 15-39: classifyCounts. Vence o maior; empate no topo ou tudo zero = misto."""
    valores = {"funcional": c.func, "oo": c.oo, "procedural": c.proc, "imperativo": c.imp}
    maximo = max(valores.values())
    if maximo == 0:
        return "misto"
    topo = [k for k, v in valores.items() if v == maximo]
    return topo[0] if len(topo) == 1 else "misto"


def classificar(codigo):
    """Linhas 420-453 (classifyNamespace) e 458-483 (visita ao arquivo)."""
    arvore = ast.parse(codigo)
    ctx = Contexto(classes={n.name for n in ast.walk(arvore) if isinstance(n, ast.ClassDef)})
    imports = 0
    for n in arvore.body:  # linhas 424-435: registra módulos e funções de functools/itertools
        if isinstance(n, ast.Import):
            imports += 1
            for a in n.names:
                ctx.modulos.add(a.asname or a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            imports += 1
            if n.module in ("functools", "itertools"):
                ctx.funcionais.update(a.asname or a.name for a in n.names)
            elif n.module:
                ctx.modulos.add(n.module.split(".")[0])
    c = Contagem(stmts=imports) + _bloco(arvore.body, ctx, em_controle=False)
    return {"paradigma": rotular(c), "func": c.func, "oo": c.oo, "proc": c.proc, "imp": c.imp, "stmts": c.stmts}
