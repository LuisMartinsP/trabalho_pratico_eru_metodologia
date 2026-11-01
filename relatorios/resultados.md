# Resultados: paradigma e code smells, humano × LLM

Gerado em 2026-11-01 10:35 a partir de dados/tabelas/ (ver manifesto.json).
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
| gemini-2.5-flash | 129 | 91 | 29 | 9 | 93% [87–96] |
| gpt-5-mini | 129 | 81 | 40 | 8 | 94% [88–97] |

## 1. Descritivo dos smells

Só os 125 exercícios com solução aceita nas duas fontes. "avisos" são os usados na
análise (sem os herdados do esqueleto, se excluídos).

| fonte | soluções | sloc (soma) | sloc (mediana) | avisos | herdados (fora) | avisos/100 sloc | densidade mediana | sem aviso | convention | refactor | warning | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gemini-2.5-flash | 120 | 3811 | 26 | 492 | 22 | 12,91 | 7,14 | 26% [19–34] | 399 | 67 | 26 | 0 |
| gpt-5-mini | 121 | 4012 | 24 | 123 | 26 | 3,07 | 0 | 64% [55–72] | 36 | 59 | 28 | 0 |
| referencia | 125 | 3184 | 19 | 88 | 18 | 2,76 | 0 | 62% [54–70] | 21 | 52 | 12 | 3 |

Por tipo de esqueleto ("classe" inclui os esqueletos com classe e funções):

| grupo_esqueleto | fonte | soluções | avisos/100 sloc |
|---|---|---|---|
| classe | gemini-2.5-flash | 33 | 11,19 |
| classe | gpt-5-mini | 34 | 2,96 |
| classe | referencia | 36 | 1,58 |
| funcao | gemini-2.5-flash | 87 | 14,19 |
| funcao | gpt-5-mini | 87 | 3,15 |
| funcao | referencia | 89 | 3,68 |

### Avisos por símbolo

| simbolo | categoria | referencia (avisos) | referencia (soluções) | gemini-2.5-flash (avisos) | gemini-2.5-flash (soluções) | gpt-5-mini (avisos) | gpt-5-mini (soluções) |
|---|---|---|---|---|---|---|---|
| trailing-whitespace | convention | 2 | 1 | 247 | 60 | 0 | 0 |
| line-too-long | convention | 6 | 6 | 124 | 39 | 22 | 12 |
| no-else-return | refactor | 23 | 18 | 25 | 17 | 18 | 7 |
| too-many-branches | refactor | 2 | 2 | 12 | 11 | 12 | 12 |
| invalid-name | convention | 0 | 0 | 17 | 10 | 7 | 5 |
| protected-access | warning | 1 | 1 | 13 | 4 | 2 | 2 |
| too-many-locals | refactor | 3 | 2 | 4 | 4 | 8 | 8 |
| superfluous-parens | convention | 3 | 2 | 8 | 6 | 3 | 2 |
| no-else-raise | refactor | 12 | 9 | 1 | 1 | 0 | 0 |
| too-few-public-methods | refactor | 5 | 5 | 5 | 5 | 2 | 2 |
| too-many-nested-blocks | refactor | 0 | 0 | 7 | 3 | 3 | 3 |
| raise-missing-from | warning | 0 | 0 | 2 | 1 | 7 | 6 |
| too-many-return-statements | refactor | 1 | 1 | 2 | 2 | 4 | 4 |
| too-many-statements | refactor | 0 | 0 | 1 | 1 | 5 | 5 |
| broad-exception-caught | warning | 0 | 0 | 0 | 0 | 5 | 4 |
| consider-using-f-string | convention | 3 | 3 | 0 | 0 | 2 | 2 |
| unused-variable | warning | 0 | 0 | 1 | 1 | 4 | 4 |
| consider-using-in | refactor | 1 | 1 | 1 | 1 | 3 | 2 |
| unused-import | warning | 0 | 0 | 3 | 3 | 2 | 2 |
| multiple-statements | convention | 4 | 1 | 0 | 0 | 0 | 0 |
| global-variable-not-assigned | warning | 0 | 0 | 4 | 1 | 0 | 0 |
| no-else-continue | refactor | 0 | 0 | 3 | 2 | 1 | 1 |
| try-except-raise | warning | 0 | 0 | 0 | 0 | 4 | 3 |
| f-string-without-interpolation | warning | 4 | 2 | 0 | 0 | 0 | 0 |
| redefined-outer-name | warning | 2 | 2 | 0 | 0 | 1 | 1 |
| consider-using-enumerate | convention | 0 | 0 | 3 | 2 | 0 | 0 |
| global-statement | warning | 0 | 0 | 2 | 2 | 1 | 1 |
| possibly-used-before-assignment | error | 3 | 3 | 0 | 0 | 0 | 0 |
| bad-indentation | warning | 2 | 1 | 0 | 0 | 0 | 0 |
| consider-using-generator | refactor | 2 | 1 | 0 | 0 | 0 | 0 |
| consider-using-max-builtin | refactor | 0 | 0 | 1 | 1 | 1 | 1 |
| import-outside-toplevel | convention | 0 | 0 | 0 | 0 | 2 | 2 |
| missing-final-newline | convention | 2 | 2 | 0 | 0 | 0 | 0 |
| too-many-instance-attributes | refactor | 1 | 1 | 1 | 1 | 0 | 0 |
| no-else-break | refactor | 0 | 0 | 2 | 2 | 0 | 0 |
| dangerous-default-value | warning | 1 | 1 | 0 | 0 | 0 | 0 |
| chained-comparison | refactor | 0 | 0 | 1 | 1 | 0 | 0 |
| consider-using-min-builtin | refactor | 0 | 0 | 0 | 0 | 1 | 1 |
| duplicate-string-formatting-argument | warning | 0 | 0 | 0 | 0 | 1 | 1 |
| arguments-out-of-order | warning | 1 | 1 | 0 | 0 | 0 | 0 |
| inconsistent-return-statements | refactor | 0 | 0 | 1 | 1 | 0 | 0 |
| undefined-loop-variable | warning | 1 | 1 | 0 | 0 | 0 | 0 |
| unnecessary-comprehension | refactor | 0 | 0 | 0 | 0 | 1 | 1 |
| unnecessary-dunder-call | convention | 1 | 1 | 0 | 0 | 0 | 0 |
| unspecified-encoding | warning | 0 | 0 | 1 | 1 | 0 | 0 |
| unnecessary-pass | warning | 0 | 0 | 0 | 0 | 1 | 1 |
| use-dict-literal | refactor | 1 | 1 | 0 | 0 | 0 | 0 |
| use-yield-from | refactor | 1 | 1 | 0 | 0 | 0 | 0 |

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

### Humano × gemini-2.5-flash

Distribuição dos rótulos nos 120 exercícios pareados:

| paradigma | humano | gemini-2.5-flash |
|---|---|---|
| oo | 6 | 3 |
| funcional | 27 | 2 |
| procedural | 43 | 82 |
| misto | 18 | 6 |
| neutro | 15 | 19 |
| indeterminado | 11 | 8 |

Pares comparáveis (os dois com rótulo determinado): **87** · mesmo paradigma:
**49% [39–60]**. Linhas: humano; colunas: gemini-2.5-flash.

| humano \ gemini-2.5-flash | oo | funcional | procedural | misto |
|---|---|---|---|---|
| oo | 1 | 0 | 5 | 0 |
| funcional | 0 | 1 | 21 | 2 |
| procedural | 2 | 0 | 37 | 0 |
| misto | 0 | 0 | 14 | 4 |

Proporção de soluções procedurais (McNemar exato nos pares discordantes) e sensibilidade
à regra e ao filtro:

| regra | pares | procedural humano | procedural gemini-2.5-flash | só humano | só gemini-2.5-flash | McNemar p |
|---|---|---|---|---|---|---|
| D (oficial), filtrada | 87 | 45% [35–55] | 89% [80–94] | 2 | 40 | <0,001 |
| C, filtrada | 73 | 60% [49–71] | 88% [78–93] | 2 | 22 | <0,001 |
| D, sem filtro | 99 | 42% [33–52] | 89% [81–94] | 2 | 48 | <0,001 |

Fração funcional, pares com pelo menos 3 pontos nos dois (Wilcoxon pareado, gemini-2.5-flash − humano):
n = 87 (66 sem empate) · mediana da diferença = -0,15 ·
p = <0,001 · r rank-bisserial = -0,87.

Por tipo de esqueleto (pares comparáveis):

| esqueleto | pares | procedural humano | procedural gemini-2.5-flash |
|---|---|---|---|
| classe | 26 | 50% [32–68] | 81% [62–91] |
| funcao | 61 | 43% [31–55] | 92% [82–96] |

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

### Humano × gemini-2.5-flash

| medida | pares | gemini-2.5-flash maior | empate | humano maior | mediana humano | mediana gemini-2.5-flash | Wilcoxon p | r |
|---|---|---|---|---|---|---|---|---|
| densidade (avisos próprios / 100 sloc) | 120 | 83 | 26 | 11 | 0,00 | 7,14 | <0,001 | 0,86 |
| densidade com herdados (sensibilidade) | 120 | 83 | 25 | 12 | 0,00 | 7,69 | <0,001 | 0,81 |
| nº de avisos próprios | 120 | 77 | 33 | 10 | 0,00 | 2,00 | <0,001 | 0,91 |
| sloc | 120 | 86 | 7 | 27 | 19,00 | 26,00 | <0,001 | 0,63 |

r = correlação rank-bisserial pareada (positiva: gemini-2.5-flash maior). Por categoria (densidade por
solução no teste; agregada na tabela):

| categoria | avisos humano | avisos gemini-2.5-flash | humano /100 sloc | gemini-2.5-flash /100 sloc | Wilcoxon p |
|---|---|---|---|---|---|
| convention | 19 | 399 | 0,65 | 10,47 | <0,001 |
| refactor | 46 | 67 | 1,57 | 1,76 | 0,536 |
| warning | 11 | 26 | 0,37 | 0,68 | 0,860 |
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

### Humano × gemini-2.5-flash

Δ densidade = gemini-2.5-flash − humano, nos pares comparáveis.

| pares | n | Δ densidade mediana |
|---|---|---|
| mesmo paradigma | 43 | 7,69 |
| paradigmas diferentes | 44 | 4,81 |

Mann-Whitney p = 0,383 · delta de Cliff (diferentes × mesmo) = -0,11 (desprezível).

Transições (pares que divergiram):

| humano_paradigma | modelo_paradigma | n | delta_mediano |
|---|---|---|---|
| funcional | procedural | 21 | 4 |
| misto | procedural | 14 | 7,29 |
| oo | procedural | 5 | 20,10 |
| funcional | misto | 2 | 18,54 |
| procedural | oo | 2 | 3,83 |

Spearman entre Δ fração funcional e Δ densidade (pares com pelo menos 3 pontos nos dois):
rho = 0,09, p = 0,383, n = 87.

## 5. Secundária: 1ª tentativa × tentativa aceita

### gemini-2.5-flash

Exercícios corrigidos com sucesso e com 1ª tentativa analisável (código válido): **29**.
Amostra pequena e selecionada pela própria falha; resultado secundário.

- Avisos: soma 216 na 1ª → 253 na aceita · aumentou em
  15, diminuiu em 2,
  igual em 12 · Wilcoxon p = 0,004
- Densidade mediana: 13,13 → 14,52 · Wilcoxon p = 0,063
- sloc (soma): 1462 → 1532
- Paradigma mudou da 1ª para a aceita em 3 de 29 exercícios

| simbolo | 1ª tentativa | aceita | dif |
|---|---|---|---|
| line-too-long | 51 | 75 | 24 |
| trailing-whitespace | 100 | 115 | 15 |
| no-else-return | 10 | 6 | -4 |
| too-many-branches | 5 | 7 | 2 |
| too-few-public-methods | 3 | 4 | 1 |
| undefined-variable | 1 | 0 | -1 |
| unused-variable | 2 | 1 | -1 |
| unused-import | 1 | 2 | 1 |
| too-many-return-statements | 2 | 1 | -1 |
| protected-access | 6 | 7 | 1 |
| global-statement | 2 | 2 | 0 |
| no-else-break | 1 | 1 | 0 |
| invalid-name | 10 | 10 | 0 |
| global-variable-not-assigned | 4 | 4 | 0 |
| no-else-continue | 3 | 3 | 0 |
| superfluous-parens | 6 | 6 | 0 |
| no-else-raise | 1 | 1 | 0 |
| raise-missing-from | 2 | 2 | 0 |
| too-many-instance-attributes | 1 | 1 | 0 |
| too-many-locals | 3 | 3 | 0 |
| too-many-statements | 1 | 1 | 0 |
| unspecified-encoding | 1 | 1 | 0 |

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

