# Registro de decisões metodológicas

Histórico das bases e abordagens avaliadas antes da escolha final, com os
motivos de cada descarte. Serve de base para as seções de Materiais e Métodos
e de Ameaças à Validade do artigo.

## Pergunta de pesquisa

Como a escolha da LLM e o paradigma de programação impactam a variabilidade
de *code smells* no código Python gerado?

---

## 1. MBPP *sanitized* (OBSOLETO)

- **Fonte:** Austin et al. (2021), `google-research-datasets/mbpp`, configuração
  `sanitized`, licença CC BY 4.0. São 427 problemas com enunciado, solução de
  referência e 3 testes `assert`.
- **Script:** `src/obsoleto/mbpp_baixar.py`
- **Por que foi considerada:** é um benchmark padrão, com testes automáticos e
  problemas curtos e neutros.
- **Problemas encontrados:**
  - Nas 427 soluções de referência há **0 classes**, e 69% não usam nenhum
    recurso funcional (lambda, compreensões, `map`/`filter`...). Os problemas
    são funções pequenas e sem estado.
  - **Forçar o paradigma pelo prompt** (mesmo problema em OO, funcional e
    procedural) gera OO artificial: a classe só embrulha a lógica procedural.
    O Pylint acusaria smells como `too-few-public-methods` por causa do desenho
    experimental, não da qualidade do código.
  - **Geração livre + detecção de paradigma** deixaria o grupo OO praticamente
    vazio.
- **Problema técnico:** o `Dataset.to_json` da biblioteca `datasets` travava no
  Jupyter (Windows). A solução foi usar pandas e trocar o notebook por scripts.

## 2. Paradigma imposto pelo prompt sobre as mesmas tarefas (DESCARTADO)

- **Vantagem:** controle experimental, porque o problema fica fixo e só o
  paradigma muda.
- **Motivo do descarte:** pedir um paradigma inadequado ao problema não reflete
  o uso real e confunde "paradigma" com "paradigma forçado". A decisão foi
  usar tarefas em que o paradigma surge da própria tarefa.
- **Consequência:** a comparação entre paradigmas passa a ser **descritiva**,
  não causal, porque as tarefas de cada grupo são diferentes. Isso vai para
  Ameaças à Validade.

## 3. Busca por base já rotulada por paradigma (NÃO ENCONTRADA)

- Nenhuma base em Python com problemas separados por paradigma e com testes.
- Existem só bases de um paradigma: OOP Benchmark (Wang et al., 2024, 431
  problemas OO) e ClassEval (100 tarefas de classe), além de FPEval (funcional,
  mas em Haskell, OCaml e Scala).

## 4. ClassEval (NÃO ADOTADA, possível trabalho futuro)

- 100 tarefas de geração de classes em Python, com testes (ICSE 2024).
- **Limitação:** a tarefa já fornece o esqueleto da classe, então o paradigma
  vem imposto. Além disso, a base cobre só OO.

## 5. FPEval / FPBench (OBSOLETO)

- **Fonte:** Lang et al. (2026), `FPEvalRepoPublic/LeetCodeProblem` no Hugging
  Face. O repositório de código é Apache 2.0, e o dataset não declara licença.
  São 721 tarefas do LeetCode.
- **Script:** `src/obsoleto/fpeval_baixar.py`, que baixa só os `meta.json`.
  Cada um traz o enunciado, os testes públicos e privados (pares de entrada e
  saída) e templates por linguagem, incluindo Python. As pastas de testes das
  outras linguagens somam cerca de 8,5 GB e não são necessárias.
- **Motivos do descarte:**
  - São problemas de **programação competitiva**, algorítmicos, que tendem ao
    procedural. O OO não apareceria naturalmente.
  - As linguagens-alvo do benchmark são Haskell, OCaml, Scala e Java, não
    Python.
  - O dataset não tem documentação (sem *dataset card*, e o visualizador do
    Hugging Face dá erro).
  - Os enunciados vêm do LeetCode e não têm licença declarada.
  - Não verificado: se o template Python é `class Solution:` (padrão do
    LeetCode), o que inflaria a detecção de OO.

## 6. Critério de detecção de paradigma (ADAPTADO)

- **Fonte:** Dyer e Chauhan (2022), ESEC/FSE, com pacote de replicação
  `10.5281/zenodo.6975558`, licença CC BY 4.0.
- O classificador original é escrito em **Boa** e roda só na infraestrutura
  deles, não em arquivos locais. A ideia é reaproveitar o **mapeamento de
  recursos para paradigmas** (`boa/py-classify.boa`).
- **Viés identificado:** todo comando dentro de um `def` de nível superior conta
  como procedural. Em soluções pequenas, isso faz código funcional ser
  classificado como procedural. É preciso adaptar a regra (por exemplo, usar
  presença ou densidade de recursos em vez de "maior soma").

---

## 7. Base adotada: Exercism, trilha de Python

- **Fonte:** https://github.com/exercism/python (licença MIT).
- **Script:** `src/01_preparar_exercism.py`
- **Versão de referência:** commit `6105f6d9d3ef66ce3d5c8f529d2882af3d76b706`
  (30/09/2026). O script registra o commit usado em cada execução.
- **Composição:** 129 exercícios práticos ativos (11 obsoletos excluídos).
  - 34 com esqueleto de **classe**;
  - 6 com **classe e funções**;
  - 89 só com **funções**.
  - Cerca de 31% das tarefas têm OO de forma natural.
- **Cada exercício tem:** enunciado (`instructions.md` +
  `instructions.append.md`), esqueleto, testes `unittest` e solução de
  referência.
- **Validação:** todas as 129 soluções de referência passaram nos testes.
- **Limitações conhecidas:**
  - Os testes exigem os nomes do esqueleto (classe, métodos, funções), então a
    LLM precisa receber o esqueleto. Isso fixa a interface e, nos exercícios de
    classe, o paradigma.
  - O grupo OO tem cerca de 40 tarefas, uma amostra pequena.
  - Os grupos procedural e funcional só aparecem depois da detecção de
    paradigma no código gerado, e o funcional tende a ser o menor.
  - **Contaminação:** o Exercism é público e muito usado, então os modelos
    provavelmente viram essas soluções no treino.

---

## 8. Protocolo de geração (`src/03_gerar.py`)

- **Prompt:** enunciado + esqueleto do Exercism, pedindo o módulo completo num
  único bloco de código. O prompt é em inglês, a língua dos enunciados, e não
  traz instrução de paradigma.
- **Uma geração por exercício, com correção:** simula um programador que quer
  código correto. Se o código falha nos testes, a saída dos testes volta para a
  LLM com um pedido de correção, até `MAX_TENTATIVAS` (padrão 3). Todas as
  tentativas são salvas, e o número de tentativas é registrado.
  - **Alternativa descartada:** 5 gerações independentes por exercício, que
    mediria a variabilidade dentro do mesmo prompt, mas multiplicaria o custo
    de API por 5. Fica como possível extensão num subconjunto de exercícios.
  - **Consequência:** sem repetições, a "variabilidade" medida passa a ser
    entre LLMs e entre exercícios, não entre execuções do mesmo prompt.
  - **Para a análise:** guardar os smells da 1ª tentativa e da tentativa
    aceita. A correção pode mudar o perfil de smells.
- **Organização em lotes:** cada lote faz até `TAMANHO_LOTE` chamadas em
  paralelo. Quem falha nos testes volta para o fim da fila, e a correção entra
  num lote seguinte. Assim, as 1ªs tentativas de todos os exercícios vêm antes
  das correções.
- **Estrutura de saída:** `dados/<modelo>/<exercicio>/tentativa_<n>.json`, mais
  um `resultado.json` por exercício.
- **Erros técnicos** (rede, limite de taxa, servidor) não contam como
  tentativa: são repetidos com espera crescente. Se a cota acabar, a execução
  para e retoma de onde parou na próxima vez.
- **Correção guiada pelo Pylint:** considerada e não adotada, porque mudaria o
  objeto medido (os smells deixariam de ser os da geração). Fica como trabalho
  futuro.

---

## 9. Classificação de paradigma

- **Regra original:** Dyer e Chauhan (2022), consulta `boa/py-classify.boa` do
  pacote de replicação (CC BY 4.0). Reimplementada em Python em
  `src/paradigma_dyer.py`; a explicação está em `docs/regra_dyer_explicada.md`.
- **Verificação da reimplementação:** conjunto de testes oficial dos autores
  (`psybers/py-classify-tests`, commit `16f45e9223`), em que o nome de cada arquivo
  traz o placar esperado do Boa. Resultado: **79/79 casos em Python 3 idênticos**;
  9 casos são Python 2 ou inválidos e não são comparáveis. Script:
  `src/verificacao/verificar_dyer.py`. A primeira versão acertava 72/88; os testes
  revelaram cinco detalhes de representação (pass/break/continue, elif, for-else,
  função aninhada em método, receptor de chamada de método), corrigidos.
- **Cobertura:** 68 de 250 soluções (27%) usam construções sem caso de teste
  oficial (operador ternário em 37, `continue` em 27, conjuntos, compreensão de
  conjunto, `with`, `nonlocal`), tratadas pelas regras gerais da consulta.
- **Limitação da regra original para este estudo:** nas 129 soluções de
  referência, 88 de 89 soluções de função saem "procedural" e nenhuma "funcional".
  Todo comando dentro de função conta como procedural, e qualquer chamada de
  função também.
- **Regra adaptada:** `src/paradigma_adaptado.py`, com as adaptações A1–A11
  descritas no cabeçalho do arquivo. Aplica-se só ao código acrescentado ao
  esqueleto. Definida antes de comparar com outros classificadores, e **não
  deve ser reajustada** depois de ver resultados.
- **Exemplo de sanidade:** `list-ops` humano → funcional (6×0); GPT → procedural
  (21×4), o mesmo julgamento dado pelo Gemini consultado manualmente.

## 10. Rótulo de paradigma: versões A, B e C (C ADOTADA; PONTOS SUBSTITUÍDOS PELA VERSÃO D, SEÇÕES 11 E 12)

A regra adaptada (seção 9) produz pontos funcionais, procedurais e OO. Foram
testadas três formas de transformar esses pontos em um rótulo (opção `--versao a|b|c` de
uma versão anterior de `src/04_paradigma.py`; a versão atual mantém só o critério da C).

- **Versão A (DESCARTADA):** OO, funcional e procedural disputam o mesmo placar
  (2/3). O OO quase nunca vence, porque o código dentro dos próprios métodos soma
  pontos procedurais/funcionais; muitas soluções com classes caíram em "misto".
  Resultado: referência com 1 OO; GPT com 3.
- **Versão B (DESCARTADA):** OO se o esqueleto do exercício é uma classe ou se a
  solução criou classes novas. O rótulo passa a vir do *exercício*, não da
  solução, e humano e IA ficam OO por construção em todos os exercícios com
  esqueleto de classe, o que não informa nada sobre a escolha de paradigma. Resultado: referência 41
  OO; GPT 34.
- **Versão C (ADOTADA):** OO só quando a solução **acrescenta classes** além das
  do esqueleto; caso contrário, funcional / procedural / misto / neutro pelos
  pontos funcionais e procedurais (2/3; zero pontos = neutro). O tipo de
  esqueleto (classe × função) vira um agrupamento separado nos relatórios.
- **Teste com IAs (consulta manual, sem rótulo "misto"):** foram enviados o
  esqueleto e a solução de `robot-simulator` (cria a classe `Compass`) e de `luhn`
  (classe exigida pelo esqueleto, corpo com laço e acumuladores). As IAs
  classificaram `robot-simulator` como OO e `luhn` como "procedural com uma casca
  de classe". A versão C concorda nos dois; a B rotula `luhn` como OO. Foi um teste de sanidade com 2 exemplos, não uma validação.
- **Resultado da versão C:**

  | fonte | oo | funcional | procedural | misto | neutro | total |
  |---|---|---|---|---|---|---|
  | referência | 6 | 38 | 60 | 11 | 14 | 129 |
  | gpt-5-mini | 0 | 10 | 86 | 12 | 13 | 121 |

  Mesmo paradigma em 66 dos 121 exercícios em comum (55%). O GPT não criou
  nenhuma classe nova em nenhum exercício; as 6 soluções OO humanas são
  `robot-simulator`, `rectangles`, `simple-linked-list`, `ledger`, `bowling` e
  `react`.
- **Limitação:** com 6 soluções OO, o OO não sustenta comparação estatística
  isolada; ele é reportado descritivamente, e a comparação principal fica entre
  funcional e procedural, com o tipo de esqueleto como segundo agrupamento.
- **Regra fixada** antes do cruzamento com os *smells*; não deve ser reajustada
  depois de ver esse cruzamento.

## 11. Contagem por operação: versão D (ADOTADA, ver seção 12)

- **Problema de medição encontrado na regra adaptada:** cada *comando* dá no máximo
  1 ponto por estilo. O estilo funcional comprime várias operações num comando só
  (`[g(x) for x in xs if x > 0]` itera, filtra e produz), e o procedural espalha as
  mesmas operações em vários comandos (`for`, `if`, `append`). A mesma tarefa valia
  1 ponto funcional ou 2-3 procedurais. Consequências: 22 de 38 rótulos "funcional"
  humanos e 9 de 10 do GPT se apoiavam em até 2 pontos, e exigindo no mínimo 3 pontos
  o funcional do GPT caía de 10 para 1.
- **Quando foi decidido:** depois de ver a distribuição de paradigmas humano × GPT da
  versão C e **antes** de qualquer cruzamento com os *smells* (`05_cruzamento.py` ainda
  não tinha sido executado). O motivo é a assimetria de medição, não o resultado.
- **Regra (`src/paradigma_operacoes.py`):** cada operação (iterar, filtrar,
  produzir/acumular) vale 1 ponto no estilo em que foi escrita, somando dentro do
  comando. `map` = 2, `filter` = 3, `reduce` = 2; lambda como argumento deles não conta
  de novo; `sum/min/max/any/all/sorted/enumerate/zip/iter` ficam neutros (o gerador ou o
  laço que os acompanha já conta a iteração); `if` dentro de laço conta como filtrar.
  O resto é igual à regra adaptada, e o rótulo segue a versão C (OO por classes novas;
  2/3 dos pontos).
- **Verificação:** `src/verificacao/verificar_equivalencia.py`, com 16 pares funcional ×
  procedural equivalentes, escritos antes de rodar a regra nos dados. Versão D: 16/16
  empatam; versão C: nenhum. Limitações registradas (não empatam): `max/min` sobre
  gerador × laço com comparação, e recursão × laço.
- **Resultado (121 exercícios em comum):**

  | versão | humano func / proc | GPT func / proc | concordância |
  |---|---|---|---|
  | C | 38 / 59 | 10 / 86 | 71/121 |
  | D | 35 / 53 | 12 / 85 | 73/121 |
  | C, mínimo de 3 pontos | 16 / 56 | 1 / 80 | 60/89 |
  | D, mínimo de 3 pontos | 27 / 50 | 9 / 80 | 62/104 |

  A distribuição quase não muda, mas os rótulos ficam mais estáveis: rótulos que mudam
  com ±1 ponto caem de 52 para 31 (humano) e de 40 para 30 (GPT); "funcional" com até
  2 pontos cai de 22/38 para 8/36 (humano) e de 9/10 para 3/12 (GPT). Mudaram de rótulo
  de C para D: 14 soluções humanas e 15 do GPT, quase todas entre misto e
  funcional/procedural.

## 12. Protocolo de análise (ADOTADO)

Fixado antes de rodar o cruzamento entre paradigma e *smells*. Os parâmetros ficam em
`config/analise.yaml` e são registrados no manifesto de cada tabela.

- **Escopo desta rodada:** só o gpt-5-mini contra a referência humana. Outros modelos
  entram depois, pelo mesmo pipeline (o Gemini tem só uma coleta parcial e fica de fora).
  As conclusões valem para esse modelo, não para "LLMs" em geral.
- **Paradigma:**
  - regra oficial **D** (seção 11); a C é mantida em todas as tabelas para a análise de
    sensibilidade;
  - **filtro de pontos:** soluções com menos de **3** pontos (funcionais + procedurais)
    recebem o rótulo **indeterminado** e saem da comparação de paradigma. Com 1-2 pontos o
    rótulo depende de uma ou duas construções e muda com ±1 ponto. **Neutro** (0 pontos) e
    indeterminado ficam separados; OO não passa pelo filtro, porque é decidido por classes
    novas. A análise sem filtro também é reportada, como sensibilidade.
- **Avisos herdados do esqueleto:** o Pylint também roda no esqueleto puro de cada
  exercício; um aviso da solução é marcado como herdado quando o esqueleto gera um aviso
  com o mesmo símbolo e a mesma mensagem (pareados um a um). Não contam como herdados
  `unused-argument` e `unnecessary-pass`, que o esqueleto só tem por estar vazio. A análise
  principal **exclui** os herdados (coerente com a A1 da classificação de paradigma: nenhum
  dos dois escolheu esses avisos); a análise com eles é reportada como sensibilidade.
  Verificação prévia (121 exercícios em comum): herdados 18 no humano e 26 no GPT;
  densidade humano 3,51 → 2,91 e GPT 3,71 → 3,07 por 100 sloc ao excluí-los. Ou seja, o
  esqueleto não favorecia a LLM.
- **Avisos de formatação** (`trailing-whitespace`, `line-too-long`...) continuam na
  análise; os resultados são reportados também por categoria do Pylint, para que o efeito
  deles fique visível sem excluir nada depois de ver os dados.
- **Execução do Pylint:** um processo por fonte (`--recursive=y`), com `duplicate-code` e
  `cyclic-import` desligados, porque cada solução é independente. Conferido: dá os mesmos
  110 avisos da execução arquivo por arquivo nas soluções de referência.
- **Organização dos dados:** tabelas em formato longo em `dados/tabelas/`, com a chave
  `(fonte, slug, tentativa)` e um manifesto com data e parâmetros (README).
- **Análises (`src/06_cruzamento.py`):** unidade = exercício, com humano e modelo
  pareados, só tentativas aceitas.
  - QP1 (paradigma): matriz humano × modelo; McNemar exato para a proporção de soluções
    procedurais; Wilcoxon pareado na fração funcional; sensibilidade com a regra C e sem
    filtro; recorte por tipo de esqueleto.
  - QP2 (*smells*): Wilcoxon pareado na densidade (efeito: correlação rank-bisserial
    pareada), no número de avisos e no sloc; perfil por categoria e por símbolo.
  - QP3 (exploratória): diferença de densidade nos pares que divergiram × concordaram no
    paradigma (Mann-Whitney, delta de Cliff); Spearman entre Δ fração funcional e Δ densidade.
  - Secundária: 1ª tentativa × aceita nos exercícios corrigidos pelo modelo (amostra
    pequena e selecionada pela falha).
  - O modelo binomial negativo da versão anterior saiu: com cerca de 100 pares e um só
    modelo, a comparação pareada responde às perguntas com menos suposições.
- **Validação humana do classificador (`src/07_validacao.py`):** amostra às cegas,
  estratificada por fonte × rótulo (6 por estrato), mais 10 casos difíceis (perto do
  limiar de 2/3 ou de pares divergentes) reportados à parte. Dois avaliadores com as
  definições de `instrucoes.md`; concordância entre eles por kappa de Cohen; acerto da
  ferramenta contra o consenso, ponderado pelo tamanho dos estratos (IC por bootstrap) e
  sem ponderação (IC de Wilson), e só nos rótulos determinados pelo filtro. Referência de
  comparação: Dyer e Chauhan validaram a regra original com 82% de concordância em 102
  arquivos.
