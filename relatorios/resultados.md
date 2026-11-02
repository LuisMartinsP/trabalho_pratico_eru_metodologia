# Resultados: paradigma e code smells, humano × LLM

Gerado em 2026-11-02 16:32 a partir de dados/tabelas/ (ver manifesto.json).
Unidade: o exercício, com a solução humana (referência do Exercism) e a do modelo lado a
lado; só tentativas aceitas (que passaram nos testes). Associações observacionais.

## 0. Dados e parâmetros

- Regra de paradigma oficial: **D**; mínimo de pontos para rótulo
  determinado: **3**.
- Avisos herdados do esqueleto: **excluídos**
  na análise principal.
- Avisos de estilo ignorados na análise principal (Siddiq et al., 2022): `trailing-whitespace`, `missing-final-newline`, `trailing-newlines`, `invalid-name`.
  Entram na análise de sensibilidade da QP2.
- Intervalos entre colchetes: IC de 95% de Wilson.

| modelo | exercícios tentados | passou na 1ª | passou com correção | falhou | acerto final |
|---|---|---|---|---|---|
| gpt-5-mini | 129 | 81 | 40 | 8 | 94% [88–97] |
| gemini-2.5-flash | 129 | 91 | 29 | 9 | 93% [87–96] |

## 1. Descritivo dos smells

Só os 125 exercícios com solução aceita nas duas fontes. "avisos" são os usados na
análise (sem os herdados do esqueleto, se excluídos, e sem os avisos de estilo ignorados).

| fonte | soluções | sloc (soma) | sloc (mediana) | avisos | herdados (fora) | de estilo (fora) | avisos/100 sloc | densidade mediana | sem aviso | convention | refactor | warning | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| referencia | 125 | 3184 | 19 | 84 | 18 | 4 | 2,64 | 0 | 63% [54–71] | 17 | 52 | 12 | 3 |
| gpt-5-mini | 121 | 4012 | 24 | 116 | 26 | 7 | 2,89 | 0 | 65% [56–73] | 29 | 59 | 28 | 0 |
| gemini-2.5-flash | 120 | 3811 | 26 | 228 | 22 | 264 | 5,98 | 2,56 | 45% [36–54] | 135 | 67 | 26 | 0 |

Por tipo de esqueleto ("classe" inclui os esqueletos com classe e funções):

| grupo_esqueleto | fonte | soluções | avisos/100 sloc |
|---|---|---|---|
| classe | gemini-2.5-flash | 33 | 5,84 |
| classe | gpt-5-mini | 34 | 2,73 |
| classe | referencia | 36 | 1,44 |
| funcao | gemini-2.5-flash | 87 | 6,09 |
| funcao | gpt-5-mini | 87 | 3,02 |
| funcao | referencia | 89 | 3,57 |

### Avisos por símbolo

| simbolo | categoria | referencia (avisos) | referencia (soluções) | gemini-2.5-flash (avisos) | gemini-2.5-flash (soluções) | gpt-5-mini (avisos) | gpt-5-mini (soluções) |
|---|---|---|---|---|---|---|---|
| line-too-long | convention | 6 | 6 | 124 | 39 | 22 | 12 |
| no-else-return | refactor | 23 | 18 | 25 | 17 | 18 | 7 |
| too-many-branches | refactor | 2 | 2 | 12 | 11 | 12 | 12 |
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
| unused-variable | warning | 0 | 0 | 1 | 1 | 4 | 4 |
| unused-import | warning | 0 | 0 | 3 | 3 | 2 | 2 |
| consider-using-f-string | convention | 3 | 3 | 0 | 0 | 2 | 2 |
| consider-using-in | refactor | 1 | 1 | 1 | 1 | 3 | 2 |
| multiple-statements | convention | 4 | 1 | 0 | 0 | 0 | 0 |
| try-except-raise | warning | 0 | 0 | 0 | 0 | 4 | 3 |
| no-else-continue | refactor | 0 | 0 | 3 | 2 | 1 | 1 |
| global-variable-not-assigned | warning | 0 | 0 | 4 | 1 | 0 | 0 |
| f-string-without-interpolation | warning | 4 | 2 | 0 | 0 | 0 | 0 |
| consider-using-enumerate | convention | 0 | 0 | 3 | 2 | 0 | 0 |
| global-statement | warning | 0 | 0 | 2 | 2 | 1 | 1 |
| possibly-used-before-assignment | error | 3 | 3 | 0 | 0 | 0 | 0 |
| redefined-outer-name | warning | 2 | 2 | 0 | 0 | 1 | 1 |
| bad-indentation | warning | 2 | 1 | 0 | 0 | 0 | 0 |
| consider-using-generator | refactor | 2 | 1 | 0 | 0 | 0 | 0 |
| consider-using-max-builtin | refactor | 0 | 0 | 1 | 1 | 1 | 1 |
| import-outside-toplevel | convention | 0 | 0 | 0 | 0 | 2 | 2 |
| too-many-instance-attributes | refactor | 1 | 1 | 1 | 1 | 0 | 0 |
| no-else-break | refactor | 0 | 0 | 2 | 2 | 0 | 0 |
| duplicate-string-formatting-argument | warning | 0 | 0 | 0 | 0 | 1 | 1 |
| arguments-out-of-order | warning | 1 | 1 | 0 | 0 | 0 | 0 |
| dangerous-default-value | warning | 1 | 1 | 0 | 0 | 0 | 0 |
| consider-using-min-builtin | refactor | 0 | 0 | 0 | 0 | 1 | 1 |
| chained-comparison | refactor | 0 | 0 | 1 | 1 | 0 | 0 |
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

### Diversidade de paradigmas por fonte

Exercícios aceitos em todas as fontes (116), só rótulos determinados. Entropia de
Shannon dos rótulos: 0 = um único paradigma; máximo = log2(4) = 2 bits.

| fonte | soluções com rótulo determinado | oo | funcional | procedural | misto | entropia (bits) |
|---|---|---|---|---|---|---|
| humano | 90 | 5 | 26 | 41 | 18 | 1,73 |
| gpt-5-mini | 94 | 0 | 9 | 76 | 9 | 0,90 |
| gemini-2.5-flash | 89 | 2 | 2 | 80 | 5 | 0,62 |

### gpt-5-mini × gemini-2.5-flash

Exercícios aceitos nos dois modelos: 116; pares comparáveis (os dois com rótulo
determinado): **88** · mesmo paradigma: **80% [70–87]**.
Linhas: gpt-5-mini; colunas: gemini-2.5-flash.

| gpt-5-mini \ gemini-2.5-flash | oo | funcional | procedural | misto |
|---|---|---|---|---|
| oo | 0 | 0 | 0 | 0 |
| funcional | 0 | 1 | 4 | 1 |
| procedural | 2 | 0 | 68 | 3 |
| misto | 0 | 0 | 8 | 1 |

Proporção de procedurais: gpt-5-mini 83% [74–89] ·
gemini-2.5-flash 91% [83–95] · só gpt-5-mini: 5 · só gemini-2.5-flash: 12 ·
McNemar p = 0,143.

## 3. QP2: smells

### Humano × gpt-5-mini

| medida | pares | gpt-5-mini maior | empate | humano maior | mediana humano | mediana gpt-5-mini | Wilcoxon p | r |
|---|---|---|---|---|---|---|---|---|
| densidade (avisos usados / 100 sloc) | 121 | 28 | 59 | 34 | 0,00 | 0,00 | 0,492 | -0,10 |
| densidade com os avisos de estilo (sensibilidade) | 121 | 30 | 56 | 35 | 0,00 | 0,00 | 0,446 | -0,11 |
| densidade com todos os avisos, inclusive herdados (sensibilidade) | 121 | 31 | 51 | 39 | 0,00 | 0,00 | 0,494 | -0,09 |
| nº de avisos usados | 121 | 26 | 69 | 26 | 0,00 | 0,00 | 0,314 | 0,16 |
| sloc | 121 | 88 | 9 | 24 | 19,00 | 24,00 | <0,001 | 0,65 |

r = correlação rank-bisserial pareada (positiva: gpt-5-mini maior). Por categoria (densidade por
solução no teste; agregada na tabela):

| categoria | avisos humano | avisos gpt-5-mini | humano /100 sloc | gpt-5-mini /100 sloc | Wilcoxon p |
|---|---|---|---|---|---|
| convention | 17 | 29 | 0,56 | 0,72 | 0,904 |
| refactor | 52 | 59 | 1,72 | 1,47 | 0,026 |
| warning | 12 | 28 | 0,40 | 0,70 | 0,104 |
| error | 3 | 0 | 0,10 | 0,00 | – |

### Humano × gemini-2.5-flash

| medida | pares | gemini-2.5-flash maior | empate | humano maior | mediana humano | mediana gemini-2.5-flash | Wilcoxon p | r |
|---|---|---|---|---|---|---|---|---|
| densidade (avisos usados / 100 sloc) | 120 | 56 | 43 | 21 | 0,00 | 2,56 | <0,001 | 0,54 |
| densidade com os avisos de estilo (sensibilidade) | 120 | 83 | 26 | 11 | 0,00 | 7,14 | <0,001 | 0,86 |
| densidade com todos os avisos, inclusive herdados (sensibilidade) | 120 | 83 | 25 | 12 | 0,00 | 7,69 | <0,001 | 0,81 |
| nº de avisos usados | 120 | 51 | 52 | 17 | 0,00 | 1,00 | <0,001 | 0,64 |
| sloc | 120 | 86 | 7 | 27 | 19,00 | 26,00 | <0,001 | 0,63 |

r = correlação rank-bisserial pareada (positiva: gemini-2.5-flash maior). Por categoria (densidade por
solução no teste; agregada na tabela):

| categoria | avisos humano | avisos gemini-2.5-flash | humano /100 sloc | gemini-2.5-flash /100 sloc | Wilcoxon p |
|---|---|---|---|---|---|
| convention | 15 | 135 | 0,51 | 3,54 | <0,001 |
| refactor | 46 | 67 | 1,57 | 1,76 | 0,536 |
| warning | 11 | 26 | 0,37 | 0,68 | 0,860 |
| error | 3 | 0 | 0,10 | 0,00 | – |

## 4. QP2: smells por tipo

Exercícios aceitos em todas as fontes: 116. Avisos usados na análise, agrupados pelo tipo de
smell (src/catalogo_smells.py). Testes: Wilcoxon pareado na densidade do tipo por solução;
correção de Holm sobre todos os 22 testes com dados suficientes
(tipos × pares de fontes, inclusive os da QP3); r positivo = a segunda fonte maior. Tipos sem
nenhum aviso não aparecem; "–" = menos de 5 pares com diferença.

| tipo | humano (avisos) | gpt-5-mini (avisos) | gemini-2.5-flash (avisos) | humano /100 sloc | gpt-5-mini /100 sloc | gemini-2.5-flash /100 sloc |
|---|---|---|---|---|---|---|
| Formatação | 10 | 21 | 116 | 0,36 | 0,57 | 3,28 |
| Legibilidade | 36 | 19 | 29 | 1,30 | 0,51 | 0,82 |
| Idioma Python | 7 | 8 | 6 | 0,25 | 0,22 | 0,17 |
| Complexidade | 5 | 30 | 22 | 0,18 | 0,81 | 0,62 |
| Design / encapsulamento | 7 | 5 | 14 | 0,25 | 0,13 | 0,40 |
| Tratamento de erros | 0 | 12 | 2 | 0,00 | 0,32 | 0,06 |
| Código morto / inútil | 4 | 8 | 4 | 0,14 | 0,22 | 0,11 |
| Possível bug | 6 | 0 | 2 | 0,22 | 0,00 | 0,06 |

### humano × gpt-5-mini

| tipo | gpt-5-mini maior | humano maior | p | p (Holm) | r |
|---|---|---|---|---|---|
| Formatação | 9 | 7 | 1,000 | 1,000 | 0,00 |
| Legibilidade | 6 | 26 | <0,001 | 0,002 | -0,78 |
| Idioma Python | 7 | 6 | 0,893 | 1,000 | 0,05 |
| Complexidade | 14 | 2 | 0,002 | 0,032 | 0,84 |
| Design / encapsulamento | 3 | 4 | 0,375 | 1,000 | -0,43 |
| Tratamento de erros | 10 | 0 | 0,002 | 0,035 | 1,00 |
| Código morto / inútil | 8 | 2 | 0,322 | 1,000 | 0,38 |
| Possível bug | 0 | 6 | 0,031 | 0,438 | -1,00 |

### humano × gemini-2.5-flash

| tipo | gemini-2.5-flash maior | humano maior | p | p (Holm) | r |
|---|---|---|---|---|---|
| Formatação | 37 | 4 | <0,001 | <0,001 | 0,84 |
| Legibilidade | 17 | 22 | 0,222 | 1,000 | -0,22 |
| Idioma Python | 4 | 6 | 0,695 | 1,000 | 0,16 |
| Complexidade | 10 | 2 | 0,016 | 0,242 | 0,77 |
| Design / encapsulamento | 8 | 3 | 0,278 | 1,000 | 0,39 |
| Tratamento de erros | 1 | 0 | – | – | – |
| Código morto / inútil | 4 | 2 | 0,844 | 1,000 | 0,14 |
| Possível bug | 2 | 6 | 0,312 | 1,000 | -0,44 |

## 5. QP3: os modelos entre si

### Correção funcional

| modelo | exercícios | passou na 1ª | passou no final | precisou de correção |
|---|---|---|---|---|
| gemini-2.5-flash | 129 | 71% [62–78] | 93% [87–96] | 29 |
| gpt-5-mini | 129 | 63% [54–71] | 94% [88–97] | 40 |

Por dificuldade do exercício (Exercism, 1 a 10):

| dificuldade | exercícios | gemini-2.5-flash 1ª | gemini-2.5-flash final | gpt-5-mini 1ª | gpt-5-mini final |
|---|---|---|---|---|---|
| 1–2 (fácil) | 60 | 87% [76–93] | 98% [91–100] | 85% [74–92] | 98% [91–100] |
| 3–5 (média) | 55 | 62% [49–73] | 91% [80–96] | 49% [36–62] | 91% [80–96] |
| 6–10 (difícil) | 14 | 36% [16–61] | 79% [52–92] | 21% [8–48] | 86% [60–96] |

### gpt-5-mini × gemini-2.5-flash: acerto (McNemar exato, exercícios pareados)

| medida | os dois | só gpt-5-mini | só gemini-2.5-flash | nenhum | McNemar p |
|---|---|---|---|---|---|
| passou na 1ª tentativa | 74 | 7 | 17 | 31 | 0,064 |
| passou no final | 116 | 5 | 4 | 4 | 1,000 |

### gpt-5-mini × gemini-2.5-flash: smells (Wilcoxon pareado, 116 exercícios aceitos nos dois; r positivo = gemini-2.5-flash maior)

| medida | pares | gemini-2.5-flash maior | gpt-5-mini maior | mediana gpt-5-mini | mediana gemini-2.5-flash | Wilcoxon p | r |
|---|---|---|---|---|---|---|---|
| densidade (avisos usados / 100 sloc) | 116 | 55 | 15 | 0,00 | 2,25 | <0,001 | 0,68 |
| densidade com os avisos de estilo (sensibilidade) | 116 | 83 | 7 | 0,00 | 6,90 | <0,001 | 0,91 |
| sloc | 116 | 55 | 51 | 21,50 | 25,50 | 0,841 | -0,02 |

Por tipo de smell (exercícios aceitos em todas as fontes; Holm da seção 4):

| tipo | gemini-2.5-flash maior | gpt-5-mini maior | p | p (Holm) | r |
|---|---|---|---|---|---|
| Formatação | 36 | 4 | <0,001 | <0,001 | 0,86 |
| Legibilidade | 17 | 7 | 0,003 | 0,050 | 0,69 |
| Idioma Python | 5 | 6 | 1,000 | 1,000 | 0,00 |
| Complexidade | 6 | 10 | 0,433 | 1,000 | -0,24 |
| Design / encapsulamento | 7 | 2 | 0,039 | 0,508 | 0,78 |
| Tratamento de erros | 1 | 10 | 0,010 | 0,156 | -0,85 |
| Código morto / inútil | 4 | 7 | 0,520 | 1,000 | -0,24 |
| Possível bug | 2 | 0 | – | – | – |

## 6. QP4 (exploratória): divergência de paradigma, dificuldade e diferença de smells

### Humano × gpt-5-mini

Δ densidade = gpt-5-mini − humano, nos pares comparáveis.

| pares | n | Δ densidade mediana |
|---|---|---|
| mesmo paradigma | 46 | 0,00 |
| paradigmas diferentes | 43 | 0,00 |

Mann-Whitney p = 0,570 · delta de Cliff (diferentes × mesmo) = 0,07 (desprezível).

Transições (pares que divergiram):

| humano_paradigma | modelo_paradigma | n | delta_mediano |
|---|---|---|---|
| funcional | procedural | 18 | 0 |
| misto | procedural | 14 | 0 |
| oo | procedural | 5 | 1,78 |
| funcional | misto | 4 | 0 |
| procedural | misto | 2 | 0,57 |

Spearman entre Δ fração funcional e Δ densidade (pares com pelo menos 3 pontos nos dois):
rho = -0,02, p = 0,863, n = 89.

Spearman entre a dificuldade do exercício e Δ densidade (todos os 121 pares):
rho = 0,16, p = 0,087.

### Humano × gemini-2.5-flash

Δ densidade = gemini-2.5-flash − humano, nos pares comparáveis.

| pares | n | Δ densidade mediana |
|---|---|---|
| mesmo paradigma | 43 | 2,56 |
| paradigmas diferentes | 44 | 0,00 |

Mann-Whitney p = 0,096 · delta de Cliff (diferentes × mesmo) = -0,21 (pequeno).

Transições (pares que divergiram):

| humano_paradigma | modelo_paradigma | n | delta_mediano |
|---|---|---|---|
| funcional | procedural | 21 | 0 |
| misto | procedural | 14 | 0 |
| oo | procedural | 5 | 8,39 |
| funcional | misto | 2 | 11,72 |
| procedural | oo | 2 | 3,38 |

Spearman entre Δ fração funcional e Δ densidade (pares com pelo menos 3 pontos nos dois):
rho = 0,19, p = 0,072, n = 87.

Spearman entre a dificuldade do exercício e Δ densidade (todos os 120 pares):
rho = 0,37, p = <0,001.

### Smells por faixa de dificuldade

Exercícios aceitos em todas as fontes. Descritivo; a faixa difícil tem poucos exercícios.

| dificuldade | exercícios | humano: avisos/solução | humano: /100 sloc | gpt-5-mini: avisos/solução | gpt-5-mini: /100 sloc | gemini-2.5-flash: avisos/solução | gemini-2.5-flash: /100 sloc |
|---|---|---|---|---|---|---|---|
| 1–2 (fácil) | 58 | 0,40 | 2,92 | 0,31 | 1,71 | 0,64 | 3,49 |
| 3–5 (média) | 48 | 0,90 | 2,73 | 1,38 | 3,26 | 2,56 | 6,40 |
| 6–10 (difícil) | 10 | 0,90 | 2,20 | 1,90 | 3,03 | 3,50 | 6,35 |

## 7. Secundária: 1ª tentativa × tentativa aceita

### gpt-5-mini

Exercícios corrigidos com sucesso e com 1ª tentativa analisável (código válido): **40**.
Amostra pequena e selecionada pela própria falha; resultado secundário.

- Avisos: soma 61 na 1ª → 62 na aceita · aumentou em
  6, diminuiu em 6,
  igual em 28 · Wilcoxon p = 0,986
- Densidade mediana: 0,00 → 0,00 · Wilcoxon p = 0,934
- sloc (soma): 1830 → 1956
- Paradigma mudou da 1ª para a aceita em 4 de 40 exercícios

| simbolo | 1ª tentativa | aceita | dif |
|---|---|---|---|
| broad-exception-caught | 2 | 4 | 2 |
| too-many-branches | 6 | 8 | 2 |
| unused-variable | 3 | 1 | -2 |
| attribute-defined-outside-init | 1 | 0 | -1 |
| superfluous-parens | 2 | 3 | 1 |
| too-few-public-methods | 1 | 2 | 1 |
| consider-using-f-string | 2 | 1 | -1 |
| no-else-continue | 2 | 1 | -1 |
| unused-import | 0 | 1 | 1 |
| unused-argument | 1 | 0 | -1 |
| undefined-variable | 1 | 0 | -1 |
| too-many-locals | 2 | 3 | 1 |
| line-too-long | 9 | 9 | 0 |
| import-outside-toplevel | 1 | 1 | 0 |
| consider-using-min-builtin | 1 | 1 | 0 |
| consider-using-in | 2 | 2 | 0 |
| too-many-nested-blocks | 1 | 1 | 0 |
| no-else-return | 12 | 12 | 0 |
| protected-access | 1 | 1 | 0 |
| raise-missing-from | 2 | 2 | 0 |
| try-except-raise | 1 | 1 | 0 |
| too-many-statements | 4 | 4 | 0 |
| too-many-return-statements | 3 | 3 | 0 |
| unnecessary-pass | 1 | 1 | 0 |

### gemini-2.5-flash

Exercícios corrigidos com sucesso e com 1ª tentativa analisável (código válido): **29**.
Amostra pequena e selecionada pela própria falha; resultado secundário.

- Avisos: soma 106 na 1ª → 128 na aceita · aumentou em
  8, diminuiu em 4,
  igual em 17 · Wilcoxon p = 0,110
- Densidade mediana: 5,88 → 6,82 · Wilcoxon p = 0,304
- sloc (soma): 1462 → 1532
- Paradigma mudou da 1ª para a aceita em 3 de 29 exercícios

| simbolo | 1ª tentativa | aceita | dif |
|---|---|---|---|
| line-too-long | 51 | 75 | 24 |
| no-else-return | 10 | 6 | -4 |
| too-many-branches | 5 | 7 | 2 |
| too-few-public-methods | 3 | 4 | 1 |
| undefined-variable | 1 | 0 | -1 |
| unused-import | 1 | 2 | 1 |
| unused-variable | 2 | 1 | -1 |
| protected-access | 6 | 7 | 1 |
| too-many-return-statements | 2 | 1 | -1 |
| no-else-break | 1 | 1 | 0 |
| global-statement | 2 | 2 | 0 |
| global-variable-not-assigned | 4 | 4 | 0 |
| raise-missing-from | 2 | 2 | 0 |
| superfluous-parens | 6 | 6 | 0 |
| no-else-raise | 1 | 1 | 0 |
| no-else-continue | 3 | 3 | 0 |
| too-many-statements | 1 | 1 | 0 |
| too-many-locals | 3 | 3 | 0 |
| too-many-instance-attributes | 1 | 1 | 0 |
| unspecified-encoding | 1 | 1 | 0 |

### Trajetória tentativa a tentativa

Exercícios em que o modelo precisou de mais de uma tentativa; entram todas as tentativas com
código válido, aceitas ou não. Amostra selecionada pela falha; resultado secundário.


#### gpt-5-mini

Médias por tentativa (48 exercícios com mais de uma tentativa):

| tentativa | exercícios | avisos | sloc | densidade |
|---|---|---|---|---|
| 1 | 48 | 1,60 | 48,06 | 2,27 |
| 2 | 48 | 1,69 | 51,88 | 2,37 |
| 3 | 15 | 2,13 | 62,93 | 2,67 |

| passo | exercícios | subiu | caiu | igual | Wilcoxon p |
|---|---|---|---|---|---|
| 1ª → 2ª | 48 | 9 | 7 | 32 | 0,554 |
| 2ª → 3ª | 15 | 3 | 1 | 11 | – |

Avisos por tipo, 1ª tentativa × última tentativa (aceita ou não):

| tipo | 1ª tentativa | última tentativa | dif |
|---|---|---|---|
| Formatação | 13 | 15 | 2 |
| Legibilidade | 17 | 16 | -1 |
| Idioma Python | 5 | 4 | -1 |
| Complexidade | 21 | 27 | 6 |
| Design / encapsulamento | 5 | 7 | 2 |
| Tratamento de erros | 9 | 16 | 7 |
| Código morto / inútil | 5 | 3 | -2 |
| Possível bug | 2 | 0 | -2 |


#### gemini-2.5-flash

Médias por tentativa (38 exercícios com mais de uma tentativa):

| tentativa | exercícios | avisos | sloc | densidade |
|---|---|---|---|---|
| 1 | 38 | 3,32 | 52,45 | 6,65 |
| 2 | 38 | 3,82 | 55,16 | 7,34 |
| 3 | 16 | 4,81 | 65,62 | 7,39 |

| passo | exercícios | subiu | caiu | igual | Wilcoxon p |
|---|---|---|---|---|---|
| 1ª → 2ª | 38 | 10 | 5 | 23 | 0,118 |
| 2ª → 3ª | 16 | 6 | 2 | 8 | 0,359 |

Avisos por tipo, 1ª tentativa × última tentativa (aceita ou não):

| tipo | 1ª tentativa | última tentativa | dif |
|---|---|---|---|
| Formatação | 66 | 95 | 29 |
| Legibilidade | 18 | 13 | -5 |
| Idioma Python | 2 | 2 | 0 |
| Complexidade | 14 | 17 | 3 |
| Design / encapsulamento | 16 | 18 | 2 |
| Tratamento de erros | 4 | 5 | 1 |
| Código morto / inútil | 4 | 4 | 0 |
| Possível bug | 2 | 1 | -1 |

