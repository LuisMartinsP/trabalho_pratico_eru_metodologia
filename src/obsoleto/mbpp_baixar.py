"""OBSOLETO: substituído por src/01_preparar_exercism.py.
Mantido para registro da metodologia (ver docs/decisoes_metodologicas.md, seção 1).

Motivo: as 427 soluções de referência do MBPP não têm nenhuma classe e são
funções pequenas e sem estado. Forçar OO pelo prompt gera classes artificiais,
e a geração livre deixaria o grupo OO vazio.

Descrição original: baixa o MBPP (versão sanitized) e salva localmente em dados/.

Uso (a partir da raiz do projeto):
    python src/obsoleto/mbpp_baixar.py
"""
from pathlib import Path

from datasets import load_dataset, concatenate_datasets

RAIZ = Path(__file__).resolve().parents[2]  # src/obsoleto/ -> raiz do projeto
SAIDA = RAIZ / "dados" / "mbpp_sanitized.jsonl"


def main():
    print("Baixando MBPP sanitized do Hugging Face...")
    ds = load_dataset("google-research-datasets/mbpp", "sanitized")
    print(ds)

    todos = concatenate_datasets([ds[parte] for parte in ds])
    print(f"Total de problemas: {len(todos)}")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df = todos.to_pandas()
    df.to_json(SAIDA, orient="records", lines=True, force_ascii=False)
    print(f"Salvo em: {SAIDA}")


if __name__ == "__main__":
    main()
