# A regra de Dyer e Chauhan (2022), explicada

Explicação, em português, do arquivo `boa/py-classify.boa` do repositório
`python-paradigms` (Dyer e Chauhan, ESEC/FSE 2022, CC BY 4.0). A tradução fiel
para Python está em `src/paradigma_dyer.py`, com as mesmas referências de linha.

## O que é o arquivo `.boa`

Boa é uma linguagem de consulta para minerar milhões de repositórios do GitHub
de uma vez. A consulta roda nos servidores do Boa, não no computador de quem a
escreve. O arquivo é texto comum e pode ser lido em qualquer editor.

No artigo, essa consulta classificou cerca de 100 mil projetos Python. Os
autores validaram a classificação comparando-a com a de três avaliadores
humanos em 102 arquivos e obtiveram 82% de concordância.

## A ideia em uma frase

Cada pedaço do código **soma pontos** em quatro paradigmas (**funcional**,
**OO**, **procedural** e **imperativo**), e o arquivo recebe o paradigma que
fizer **mais pontos**. Empate no topo, ou nenhum ponto, vira **misto**.

## Como os pontos são dados

### 1. Expressões (linhas 80–157)

| Expressão | Exemplo | Ponto |
|---|---|---|
| gerador, `yield` | `(x for x in xs)` | funcional |
| `in` / `not in` | `if x in lista` | funcional |
| `lambda`, compreensão | `[x*2 for x in xs]` | funcional |
| chamada a `map`, `filter`, `zip`, `enumerate`, `reduce`, `sorted`, `iter`, `any`, `all` | `map(f, xs)` | funcional |
| chamada a algo de `functools`/`itertools` | `itertools.chain(...)` | funcional |
| chamada a uma classe do arquivo | `Conta()` | OO |
| chamada a outra função qualquer | `len(x)`, `minha_funcao(x)` | **procedural** |
| chamada a função de módulo importado | `math.sqrt(x)` | procedural |
| chamada de método de objeto | `lista.append(x)`, `s.upper()` | **OO** |
| acesso a `self.x` | `self.saldo` | OO |
| todo o resto (variável, número, conta) | `a + b` | imperativo |

**Limite (linhas 57–69):** uma expressão inteira dá **no máximo 1 ponto por
paradigma**. Se ela tiver algum ponto funcional, OO ou procedural, o ponto
imperativo é zerado.

### 2. Comandos (linhas 159–321)

| Comando | Ponto |
|---|---|
| `try`, `except`, `raise`, `finally`, `with` | **OO** (e zera o imperativo) |
| laço `for` | **funcional** (e zera o imperativo); +1 imperativo se o corpo tiver mais de um comando |
| `return` | soma a expressão e zera o imperativo |
| `if`, `while` | soma a condição e o corpo; cada `else`/`elif` soma +1 imperativo |
| atribuição (`x = ...`) | imperativo, mais o que a expressão tiver |
| chamada solta (`f(x)`) | o que a expressão tiver |
| `global`, `pass`, `break`, `continue` | imperativo |

### 3. Funções (linhas 350–375)

**Este é o ponto mais importante para o nosso estudo.** Depois de somar os
comandos de uma função, a regra substitui:

- se a função está **dentro de uma classe** (é um método): o placar OO passa a
  ser o **número de comandos** da função;
- se é uma função **solta**: o placar procedural passa a ser o **número de
  comandos** da função.

Ou seja, **todo comando dentro de um `def` vale um ponto procedural** (ou OO, se
for método). Em projetos grandes isso mede "o código está organizado em
funções ou em classes?". Numa solução de exercício, que é quase só funções, esse
placar quase sempre vence.

Também na função:
- cada **decorator** soma +1 funcional (linhas 353–356);
- se um **parâmetro é chamado como função** (função de ordem superior), soma
  funcional (linhas 325–348 e 368–372).

### 4. Classes (linhas 389–418)

- a classe começa com +1 OO;
- cada método e cada comando da classe contribuem pelo menos o número de
  comandos em OO;
- se a classe tem `__iter__` e `__next__` (é iterável), soma +3 funcional.

### 5. Rótulo final (linhas 15–39)

Ganha o paradigma com mais pontos. Empate no topo, ou nenhum ponto, é "misto".

## Exemplo: `list-ops`, solução humana

```python
def map(function, list):
    return [function(element) for element in list]
```

- compreensão → 1 funcional; chamada `function(element)` → 1 procedural
  (o limite deixa 1 de cada);
- `function` é um parâmetro chamado como função → +1 funcional;
- mas a função tem 2 comandos (o `def` e o `return`) → **procedural = 2**.

Somando as 8 funções do arquivo: **procedural 22 × funcional 10 → "procedural"**,
embora o código seja claramente funcional.

## Por que a regra funciona no artigo e não aqui

A regra foi validada em **arquivos de projetos reais**, que são grandes,
misturam muitos comandos soltos, classes e funções, e onde "organizado em
funções" de fato distingue procedural de OO e de imperativo. Em **soluções de
exercício**, que têm de uma a poucas funções, três decisões dominam o
resultado:

1. todo comando dentro de função vale procedural (seção 3);
2. qualquer chamada a função vale procedural (seção 1), e código funcional é
   feito justamente de chamadas, inclusive recursivas;
3. `lista.append(...)` vale OO e `for` vale funcional, o que confunde o estilo
   procedural com OO e com funcional.

Na prática, nas 129 soluções de referência do Exercism, a regra original dá
**88 de 89 soluções de função como "procedural"** e **nenhuma como funcional**.
Isso é coerente com o próprio artigo, que encontrou quase nenhum projeto
funcional, e mostra que a regra é muito exigente com o estilo funcional quando
aplicada a código curto.
