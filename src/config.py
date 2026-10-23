"""Leitura de config/modelos.yaml, compartilhada pelos scripts."""
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVO = RAIZ / "config" / "modelos.yaml"


def carregar():
    return yaml.safe_load(ARQUIVO.read_text(encoding="utf-8"))


def perfil(nome):
    """Devolve a configuração do perfil (com o protocolo embutido) ou encerra com a lista de perfis."""
    cfg = carregar()
    modelos = cfg.get("modelos", {})
    if nome not in modelos:
        sys.exit(f"Perfil '{nome}' não existe em {ARQUIVO.name}. Perfis disponíveis: {', '.join(modelos)}")
    return {"perfil": nome, **cfg.get("protocolo", {}), **modelos[nome]}


def pasta_do_modelo(nome_modelo):
    """Nome da pasta em dados/ para um modelo (o nome da API, sem barras)."""
    return nome_modelo.replace("/", "_")
