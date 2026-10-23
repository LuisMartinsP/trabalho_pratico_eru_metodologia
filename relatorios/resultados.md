# Resultados: paradigma e code smells, humano × LLM

Gerado em 2026-10-23 16:58 a partir de dados/tabelas/ (ver manifesto.json).
Unidade: o exercício, com a solução humana (referência do Exercism) e a do modelo lado a
lado; só tentativas aceitas (que passaram nos testes). Associações observacionais.

## 0. Dados e parâmetros

- Regra de paradigma oficial: **D**; mínimo de pontos para rótulo
  determinado: **3**.
- Avisos herdados do esqueleto: **excluídos**
  na análise principal.
- Intervalos entre colchetes: IC de 95% de Wilson.

| modelo | exercícios tentados | passou na 1ª | passou com correção | falhou | acerto final |
|---|---|---|---|---|---|
| gpt-5-mini | 129 | 81 | 40 | 8 | 94% [88–97] |

## 1. Descritivo dos smells

Só os 121 exercícios com solução aceita nas duas fontes. "avisos" são os usados na
análise (sem os herdados do esqueleto, se excluídos).

| fonte | soluções | sloc (soma) | sloc (mediana) | avisos | herdados (fora) | avisos/100 sloc | densidade mediana | sem aviso | convention | refactor | warning | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | 121 | 4012 | 24 | 123 | 26 | 3,07 | 0 | 64% [55–72] | 36 | 59 | 28 | 0 |
| referencia | 121 | 3022 | 19 | 88 | 18 | 2,91 | 0 | 61% [52–69] | 21 | 52 | 12 | 3 |

Por tipo de esqueleto ("classe" inclui os esqueletos com classe e funções):

| grupo_esqueleto | fonte | soluções | avisos/100 sloc |
|---|---|---|---|
| classe | gpt-5-mini | 34 | 2,96 |
| classe | referencia | 34 | 1,70 |
| funcao | gpt-5-mini | 87 | 3,15 |
| funcao | referencia | 87 | 3,82 |

### Avisos por símbolo

| simbolo | categoria | referencia (avisos) | referencia (soluções) | gpt-5-mini (avisos) | gpt-5-mini (soluções) |
|---|---|---|---|---|---|
| no-else-return | refactor | 23 | 18 | 18 | 7 |
| line-too-long | convention | 6 | 6 | 22 | 12 |
| too-many-branches | refactor | 2 | 2 | 12 | 12 |
| no-else-raise | refactor | 12 | 9 | 0 | 0 |
| too-many-locals | refactor | 3 | 2 | 8 | 8 |
| too-few-public-methods | refactor | 5 | 5 | 2 | 2 |
| invalid-name | convention | 0 | 0 | 7 | 5 |
| raise-missing-from | warning | 0 | 0 | 7 | 6 |
| superfluous-parens | convention | 3 | 2 | 3 | 2 |
| consider-using-f-string | convention | 3 | 3 | 2 | 2 |
| broad-exception-caught | warning | 0 | 0 | 5 | 4 |
| too-many-statements | refactor | 0 | 0 | 5 | 5 |
| too-many-return-statements | refactor | 1 | 1 | 4 | 4 |
| try-except-raise | warning | 0 | 0 | 4 | 3 |
| f-string-without-interpolation | warning | 4 | 2 | 0 | 0 |
| multiple-statements | convention | 4 | 1 | 0 | 0 |
| unused-variable | warning | 0 | 0 | 4 | 4 |
| consider-using-in | refactor | 1 | 1 | 3 | 2 |
| redefined-outer-name | warning | 2 | 2 | 1 | 1 |
| protected-access | warning | 1 | 1 | 2 | 2 |
| too-many-nested-blocks | refactor | 0 | 0 | 3 | 3 |
| possibly-used-before-assignment | error | 3 | 3 | 0 | 0 |
| unused-import | warning | 0 | 0 | 2 | 2 |
| consider-using-generator | refactor | 2 | 1 | 0 | 0 |
| bad-indentation | warning | 2 | 1 | 0 | 0 |
| import-outside-toplevel | convention | 0 | 0 | 2 | 2 |
| missing-final-newline | convention | 2 | 2 | 0 | 0 |
| trailing-whitespace | convention | 2 | 1 | 0 | 0 |
| duplicate-string-formatting-argument | warning | 0 | 0 | 1 | 1 |
| consider-using-max-builtin | refactor | 0 | 0 | 1 | 1 |
| arguments-out-of-order | warning | 1 | 1 | 0 | 0 |
| dangerous-default-value | warning | 1 | 1 | 0 | 0 |
| consider-using-min-builtin | refactor | 0 | 0 | 1 | 1 |
| no-else-continue | refactor | 0 | 0 | 1 | 1 |
| global-statement | warning | 0 | 0 | 1 | 1 |
| too-many-instance-attributes | refactor | 1 | 1 | 0 | 0 |
| undefined-loop-variable | warning | 1 | 1 | 0 | 0 |
| unnecessary-comprehension | refactor | 0 | 0 | 1 | 1 |
| unnecessary-pass | warning | 0 | 0 | 1 | 1 |
| unnecessary-dunder-call | convention | 1 | 1 | 0 | 0 |
| use-dict-literal | refactor | 1 | 1 | 0 | 0 |
| use-yield-from | refactor | 1 | 1 | 0 | 0 |

## 2. QP1: escolha de paradigma

### Humano × gpt-5-mini

Distribuição dos rótulos nos 121 exercícios pareados:

| paradigma | humano | gpt-5-mini |
|---|---|---|
| oo | 5 | 0 |
| funcional | 27 | 9 |
| procedural | 45 | 80 |
| misto | 18 | 10 |
| neutro | 15 | 14 |
| indeterminado | 11 | 8 |

Pares comparáveis (os dois com rótulo determinado): **89** · mesmo paradigma:
**52% [41–62]**. Linhas: humano; colunas: gpt-5-mini.

| humano \ gpt-5-mini | oo | funcional | procedural | misto |
|---|---|---|---|---|
| oo | 0 | 0 | 5 | 0 |
| funcional | 0 | 2 | 18 | 4 |
| procedural | 0 | 0 | 40 | 2 |
| misto | 0 | 0 | 14 | 4 |

Proporção de soluções procedurais (McNemar exato nos pares discordantes) e sensibilidade
à regra e ao filtro:

| regra | pares | procedural humano | procedural gpt-5-mini | só humano | só gpt-5-mini | McNemar p |
|---|---|---|---|---|---|---|
| D (oficial), filtrada | 89 | 47% [37–57] | 87% [78–92] | 2 | 37 | <0,001 |
| C, filtrada | 75 | 64% [53–74] | 92% [84–96] | 4 | 25 | <0,001 |
| D, sem filtro | 103 | 45% [35–54] | 80% [71–86] | 3 | 39 | <0,001 |

Fração funcional, pares com pelo menos 3 pontos nos dois (Wilcoxon pareado, gpt-5-mini − humano):
n = 89 (63 sem empate) · mediana da diferença = -0,11 ·
p = <0,001 · r rank-bisserial = -0,79.

Por tipo de esqueleto (pares comparáveis):

| esqueleto | pares | procedural humano | procedural gpt-5-mini |
|---|---|---|---|
| classe | 27 | 56% [37–72] | 78% [59–89] |
| funcao | 62 | 44% [32–56] | 90% [80–95] |

## 3. QP2: smells

### Humano × gpt-5-mini

| medida | pares | gpt-5-mini maior | empate | humano maior | mediana humano | mediana gpt-5-mini | Wilcoxon p | r |
|---|---|---|---|---|---|---|---|---|
| densidade (avisos próprios / 100 sloc) | 121 | 30 | 56 | 35 | 0,00 | 0,00 | 0,446 | -0,11 |
| densidade com herdados (sensibilidade) | 121 | 31 | 51 | 39 | 0,00 | 0,00 | 0,494 | -0,09 |
| nº de avisos próprios | 121 | 28 | 65 | 28 | 0,00 | 0,00 | 0,401 | 0,13 |
| sloc | 121 | 88 | 9 | 24 | 19,00 | 24,00 | <0,001 | 0,65 |

r = correlação rank-bisserial pareada (positiva: gpt-5-mini maior). Por categoria (densidade por
solução no teste; agregada na tabela):

| categoria | avisos humano | avisos gpt-5-mini | humano /100 sloc | gpt-5-mini /100 sloc | Wilcoxon p |
|---|---|---|---|---|---|
| convention | 21 | 36 | 0,69 | 0,90 | 0,910 |
| refactor | 52 | 59 | 1,72 | 1,47 | 0,026 |
| warning | 12 | 28 | 0,40 | 0,70 | 0,104 |
| error | 3 | 0 | 0,10 | 0,00 | – |

## 4. QP3 (exploratória): divergência de paradigma × diferença de smells

### Humano × gpt-5-mini

Δ densidade = gpt-5-mini − humano, nos pares comparáveis.

| pares | n | Δ densidade mediana |
|---|---|---|
| mesmo paradigma | 46 | 0,00 |
| paradigmas diferentes | 43 | 0,00 |

Mann-Whitney p = 0,416 · delta de Cliff (diferentes × mesmo) = 0,10 (desprezível).

Transições (pares que divergiram):

| humano_paradigma | modelo_paradigma | n | delta_mediano |
|---|---|---|---|
| funcional | procedural | 18 | 0 |
| misto | procedural | 14 | 0 |
| oo | procedural | 5 | 1,78 |
| funcional | misto | 4 | 0 |
| procedural | misto | 2 | 1,64 |

Spearman entre Δ fração funcional e Δ densidade (pares com pelo menos 3 pontos nos dois):
rho = -0,04, p = 0,707, n = 89.

## 5. Secundária: 1ª tentativa × tentativa aceita

### gpt-5-mini

Exercícios corrigidos com sucesso e com 1ª tentativa analisável (código válido): **40**.
Amostra pequena e selecionada pela própria falha; resultado secundário.

- Avisos: soma 66 na 1ª → 67 na aceita · aumentou em
  6, diminuiu em 6,
  igual em 28 · Wilcoxon p = 0,986
- Densidade mediana: 0,00 → 0,00 · Wilcoxon p = 0,980
- sloc (soma): 1830 → 1956
- Paradigma mudou da 1ª para a aceita em 4 de 40 exercícios

| simbolo | 1ª tentativa | aceita | dif |
|---|---|---|---|
| broad-exception-caught | 2 | 4 | 2 |
| unused-variable | 3 | 1 | -2 |
| too-many-branches | 6 | 8 | 2 |
| attribute-defined-outside-init | 1 | 0 | -1 |
| consider-using-f-string | 2 | 1 | -1 |
| superfluous-parens | 2 | 3 | 1 |
| too-few-public-methods | 1 | 2 | 1 |
| no-else-continue | 2 | 1 | -1 |
| unused-import | 0 | 1 | 1 |
| undefined-variable | 1 | 0 | -1 |
| unused-argument | 1 | 0 | -1 |
| too-many-locals | 2 | 3 | 1 |
| line-too-long | 9 | 9 | 0 |
| consider-using-in | 2 | 2 | 0 |
| invalid-name | 5 | 5 | 0 |
| import-outside-toplevel | 1 | 1 | 0 |
| consider-using-min-builtin | 1 | 1 | 0 |
| too-many-nested-blocks | 1 | 1 | 0 |
| no-else-return | 12 | 12 | 0 |
| protected-access | 1 | 1 | 0 |
| raise-missing-from | 2 | 2 | 0 |
| try-except-raise | 1 | 1 | 0 |
| too-many-statements | 4 | 4 | 0 |
| too-many-return-statements | 3 | 3 | 0 |
| unnecessary-pass | 1 | 1 | 0 |

