"""Catálogo de tipos de smell: cada símbolo do Pylint pertence a um tipo.

Usado por 08_tipos_smells.py (tabelas por tipo) e 09_banco.py (tabela `simbolos` do banco).
Para mudar um símbolo de tipo, edite aqui e rode as duas etapas de novo.
"""

# tipo -> {símbolo: descrição}. Símbolo novo nos dados e ausente daqui interrompe o script,
# para que nenhum aviso fique sem tipo.
TIPOS = {
    "Formatação": {
        "trailing-whitespace": "espaços no fim da linha (inclui linha vazia com indentação)",
        "line-too-long": "linha com mais de 100 caracteres",
        "missing-final-newline": "arquivo sem quebra de linha no final",
        "superfluous-parens": "parênteses desnecessários após palavra-chave (if (x):, return (x))",
        "bad-indentation": "indentação que não é múltipla de 4 espaços",
    },
    "Legibilidade": {
        "multiple-statements": "dois comandos na mesma linha (if x: return y, ou ;)",
        "no-else-return": "else desnecessário depois de if que termina em return",
        "no-else-raise": "else desnecessário depois de if que termina em raise",
        "no-else-continue": "else desnecessário depois de if que termina em continue",
        "no-else-break": "else desnecessário depois de if que termina em break",
        "redefined-outer-name": "nome local que esconde um nome de escopo externo",
        "import-outside-toplevel": "import dentro de função",
        "redefined-builtin": "nome que sobrescreve um embutido do Python (list, id, input...)",
    },
    "Convenção de nomes": {
        "invalid-name": "nome fora do padrão PEP 8 (snake_case, CONSTANTE, PascalCase)",
    },
    "Idioma Python": {
        "consider-using-f-string": "usa % ou .format() em vez de f-string",
        "consider-using-enumerate": "for i in range(len(x)) usando x[i]",
        "unnecessary-dunder-call": "chama x.__metodo__() em vez da forma embutida (len(x) etc.)",
        "consider-using-in": "x == a or x == b em vez de x in (a, b)",
        "consider-using-max-builtin": "if x > m: m = x em vez de m = max(m, x)",
        "consider-using-min-builtin": "if x < m: m = x em vez de m = min(m, x)",
        "consider-using-generator": "lista criada à toa dentro de any/all/sum/max/min",
        "chained-comparison": "a < b and b < c em vez de a < b < c",
        "unnecessary-comprehension": "[x for x in y] em vez de list(y)",
        "use-dict-literal": "dict() em vez de {}",
        "use-yield-from": "for x in g: yield x em vez de yield from g",
        "unnecessary-lambda-assignment": "lambda atribuída a variável em vez de def",
        "redundant-u-string-prefix": "prefixo u em string, desnecessário no Python 3",
    },
    "Complexidade": {
        "too-many-branches": "função com mais de 12 ramificações",
        "too-many-statements": "função com mais de 50 comandos",
        "too-many-locals": "função com mais de 15 variáveis locais",
        "too-many-return-statements": "função com mais de 6 return",
        "too-many-nested-blocks": "mais de 5 níveis de aninhamento",
    },
    "Design / encapsulamento": {
        "too-many-instance-attributes": "classe com mais de 7 atributos",
        "too-few-public-methods": "classe com menos de 2 métodos públicos",
        "protected-access": "acesso a _atributo de outro objeto",
        "global-statement": "uso de global",
        "global-variable-not-assigned": "declara global sem atribuir à variável",
    },
    "Tratamento de erros": {
        "raise-missing-from": "raise dentro de except sem 'from e' (perde a causa original)",
        "broad-exception-caught": "except Exception genérico",
        "try-except-raise": "except que só relança o erro",
    },
    "Código morto / inútil": {
        "unused-variable": "variável atribuída e nunca usada",
        "unused-import": "import não usado",
        "unused-argument": "argumento não usado",
        "unnecessary-pass": "pass sobrando",
        "f-string-without-interpolation": "f-string sem nenhum {}",
        "duplicate-string-formatting-argument": "mesmo argumento repetido na formatação",
    },
    "Possível bug": {
        "dangerous-default-value": "argumento padrão mutável (def f(x=[]))",
        "possibly-used-before-assignment": "variável pode estar indefinida em algum caminho",
        "undefined-loop-variable": "usa a variável do for depois do laço",
        "arguments-out-of-order": "argumentos em ordem que parece trocada",
        "inconsistent-return-statements": "alguns caminhos retornam valor e outros None implícito",
        "unspecified-encoding": "open() sem encoding",
        "undefined-variable": "variável não definida",
        "not-callable": "chamada de algo que não é função",
        "attribute-defined-outside-init": "atributo criado fora do __init__",
    },
}
ORDEM_TIPOS = list(TIPOS)
TIPO_DE = {s: t for t, simbolos in TIPOS.items() for s in simbolos}
DESCRICAO = {s: d for simbolos in TIPOS.values() for s, d in simbolos.items()}
