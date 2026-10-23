# trabalho_pratico_eru_metodologia
Pipeline de análise de Code Smells em diferentes paradigmas, utilizando linguagem python e análise de desempenho por LLM.

## Base de dados

As tarefas vêm da trilha de Python do [Exercism](https://github.com/exercism/python), sob licença MIT.

Também foram avaliadas, e depois descartadas, o MBPP (Austin et al., 2021, CC BY 4.0) e o FPEval/FPBench (Lang et al., 2026). Os scripts dessas tentativas estão em `src/obsoleto/`, e os motivos estão em `docs/decisoes_metodologicas.md`.

## Configuração

- `config/modelos.yaml`: perfis das LLMs e protocolo de geração (chaves de API no `.env`).
- `config/analise.yaml`: fontes analisadas, regra de paradigma oficial, mínimo de pontos, exclusão dos avisos herdados do esqueleto e parâmetros da amostra de validação.

## Etapas

1. `python src/01_preparar_exercism.py`: clona o Exercism e gera `dados/exercism.jsonl`.
2. `python src/02_pylint.py [fontes]`: roda o Pylint em **todas as tentativas** de cada fonte e grava `dados/tabelas/solucoes.csv` e `dados/tabelas/avisos.csv`; marca os avisos herdados do esqueleto.
3. `python src/03_gerar.py <perfil>` (ex.: `gpt-mini`; use `--limite 5` para testar): gera as soluções com a LLM do perfil, valida com os testes e pede correção em caso de falha.
4. `python src/04_paradigma.py [fontes]`: classifica o paradigma de cada tentativa com as regras D (oficial, por operação) e C (por comando, para sensibilidade) e grava `dados/tabelas/paradigmas.csv`, com o rótulo "indeterminado" abaixo do mínimo de pontos.
5. `python src/05_consolidar.py [fontes]`: junta tudo em `dados/tabelas/analise.csv` (uma linha por tentativa) e `dados/tabelas/pareado.csv` (humano e modelo lado a lado, por exercício).
6. `python src/06_cruzamento.py`: testes das perguntas de pesquisa e `relatorios/resultados.md`.
7. `python src/07_validacao.py amostra` / `avaliar`: sorteia a amostra às cegas para a validação humana do classificador (`dados/validacao/`) e, depois das respostas, gera `relatorios/validacao.md`.

Sem argumentos, as etapas 2, 4 e 5 usam as fontes de `config/analise.yaml`. A etapa 3 vem antes da 2 quando há um modelo novo; as etapas 2 e 4 podem rodar uma fonte por vez (cada uma substitui só as próprias linhas das tabelas).

Sequência completa, a partir das soluções já geradas:

```
python src/02_pylint.py
python src/04_paradigma.py
python src/05_consolidar.py
python src/06_cruzamento.py
```

Verificações do classificador: `python src/verificacao/verificar_dyer.py` (reimplementação da regra original) e `python src/verificacao/verificar_equivalencia.py` (pares funcional × procedural equivalentes na regra D).

## Tabelas (`dados/tabelas/`)

Todas em formato longo, com a chave `(fonte, slug, tentativa)`; o humano tem só a tentativa 1. `manifesto.json` registra quando e com quais parâmetros cada tabela foi gerada; as etapas seguintes param com uma instrução se alguma estiver desatualizada.

| tabela | uma linha por | principais colunas |
|---|---|---|
| `solucoes.csv` | tentativa | status, aceita, erro_sintaxe, sloc |
| `avisos.csv` | aviso do Pylint | simbolo, categoria, linha, herdado_esqueleto |
| `paradigmas.csv` | tentativa com código válido | pontos e rótulo das regras D e C, rótulo filtrado, classes novas |
| `exercicios.csv` | exercício | dificuldade, tipo_esqueleto, sloc_esqueleto |
| `analise.csv` | tentativa | tudo junto: avisos, densidade, paradigma, fração funcional |
| `pareado.csv` | exercício × modelo | colunas `humano_*`, `modelo_*` e as diferenças |

O código analisado fica em `dados/codigos/<fonte>/<slug>/t<n>/`.
