"""OBSOLETO: substituído por src/01_preparar_exercism.py.
Mantido para registro da metodologia (ver docs/decisoes_metodologicas.md, seção 5).

Baixa só os meta.json do FPBench (FPEval, Lang et al. 2026): enunciado, testes de
entrada e saída e templates por linguagem. As pastas de testes das outras
linguagens (~8,5 GB) são ignoradas.

Motivo do descarte: problemas de programação competitiva (LeetCode), que tendem
ao procedural, sem OO natural. As linguagens-alvo do benchmark não são Python,
o dataset não tem documentação e os enunciados não têm licença declarada.
"""
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="FPEvalRepoPublic/LeetCodeProblem",
    repo_type="dataset",
    allow_patterns="*/meta.json",
    local_dir="dados/fpeval",
)