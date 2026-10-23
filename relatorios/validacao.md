# Validação humana do classificador de paradigma

## 1. Concordância entre avaliadores

Só há respostas de um avaliador; o kappa entre humanos não pode ser calculado.

## 2. Acerto da ferramenta (estratos aleatórios)

Referência: um único avaliador (sem medida de concordância entre humanos).

- **Acerto geral ponderado pelos estratos: 77% [IC 95%: 62–90]**
  (bootstrap estratificado; estima o acerto na população de soluções aceitas)
- Acerto sem ponderação: 70% [57–81] (n = 54) (IC de Wilson)
- Só nos rótulos determinados pelo filtro de pontos (os usados na análise):
  63% [47–77] (n = 38)
- Kappa ferramenta × humano: 0,62 (substancial)

Por estrato:

| estrato | n | acerto | na população |
|---|---|---|---|
| gpt-5-mini / funcional | 6 | 83% [44–97] (n = 6) | 12 |
| gpt-5-mini / misto | 6 | 67% [30–90] (n = 6) | 10 |
| gpt-5-mini / neutro | 6 | 83% [44–97] (n = 6) | 14 |
| gpt-5-mini / procedural | 6 | 83% [44–97] (n = 6) | 85 |
| referencia / funcional | 6 | 100% [61–100] (n = 6) | 36 |
| referencia / misto | 6 | 50% [19–81] (n = 6) | 18 |
| referencia / neutro | 6 | 83% [44–97] (n = 6) | 15 |
| referencia / oo | 6 | 17% [3–56] (n = 6) | 6 |
| referencia / procedural | 6 | 67% [30–90] (n = 6) | 54 |

Matriz de confusão (linhas: ferramenta; colunas: humano):

| ferramenta \ humano | oo | funcional | procedural | misto | neutro |
|---|---|---|---|---|---|
| oo | 1 | 1 | 3 | 1 | 0 |
| funcional | 0 | 11 | 0 | 1 | 0 |
| procedural | 1 | 1 | 9 | 0 | 1 |
| misto | 0 | 3 | 2 | 7 | 0 |
| neutro | 0 | 1 | 1 | 0 | 10 |

## 3. Casos difíceis (à parte)

Acerto: 60% [31–83] (n = 10). Não entra no acerto geral.

| id | fonte | slug | rotulo_ferramenta | humano | total_pontos |
|---|---|---|---|---|---|
| V010 | referencia | sum-of-multiples | funcional | neutro | 6 |
| V014 | referencia | proverb | misto | funcional | 4 |
| V052 | gpt-5-mini | protein-translation | procedural | misto | 5 |
| V059 | referencia | state-of-tic-tac-toe | funcional | procedural | 16 |
