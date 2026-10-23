"""Etapa 3: gera as soluções com a LLM escolhida e valida cada uma nos testes.

Uso (a partir da raiz do projeto, com o .venv ativado):
    python src/03_gerar.py <perfil>                 ex.: python src/03_gerar.py gemini-flash
    python src/03_gerar.py <perfil> --limite 5      só os 5 primeiros exercícios (teste rápido)

Os perfis (provedor, modelo, temperatura, limite por minuto) e o protocolo
(máximo de tentativas, tamanho do lote) ficam em config/modelos.yaml.
As chaves de API ficam no .env.

Fluxo (simula um programador que quer código correto):
1. Cada exercício recebe enunciado + esqueleto, e a LLM devolve o módulo completo.
2. Logo após cada resposta, os testes do Exercism rodam no código recebido.
3. Quem falhou volta para a fila e entra num lote seguinte com um pedido de
   correção (a saída dos testes vai junto), até max_tentativas.
   Os lotes processam primeiro as 1ªs tentativas de todos e depois as correções.

Não há instrução de paradigma no prompt: o paradigma surge da tarefa e da LLM.

Erros técnicos (rede, limite por minuto, servidor) NÃO contam como tentativa:
são repetidos com espera crescente. Se a cota/os créditos acabarem, o script
para sem perder nada e, na próxima execução, continua de onde parou (o estado
de cada exercício é lido dos arquivos já salvos).

Saídas:
    dados/<modelo>/<exercicio>/tentativa_<n>.json   cada tentativa (prompt, resposta,
                                                    código, status e saída dos testes)
    dados/<modelo>/<exercicio>/resultado.json       resumo, escrito quando o exercício termina
"""
import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import provedores  # noqa: E402
from provedores import PARAR, CotaEsgotada  # noqa: E402
from testes_exercism import rodar_testes  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "dados" / "exercism.jsonl"

PROMPT_INICIAL = """You are given a programming exercise. Implement the solution in Python.

## Instructions

{enunciado}

## Starting code (`{arquivo}`)

```python
{esqueleto}
```

Return the complete contents of `{arquivo}` in a single ```python code block.
Keep the names and signatures from the starting code, because the tests import them.
Do not include tests or explanations."""

PROMPT_SEM_CODIGO = """Your answer did not contain a ```python code block.

Return the complete contents of `{arquivo}` in a single ```python code block.
Do not include tests or explanations."""

PROMPT_CORRECAO = """Your code did not pass the tests. Test output:

```
{saida}
```

Fix the code and return the complete contents of `{arquivo}` in a single ```python code block.
Do not include tests or explanations."""


def extrair_codigo(texto):
    """Pega o primeiro bloco ```python``` da resposta (ou um bloco ``` sem linguagem)."""
    blocos = re.findall(r"```(?:python|py)\s*\n(.*?)```", texto, flags=re.DOTALL | re.IGNORECASE)
    if not blocos:
        blocos = re.findall(r"```\s*\n(.*?)```", texto, flags=re.DOTALL)
    return blocos[0].strip() + "\n" if blocos else None


def mensagem(papel, texto):
    return {"role": papel, "parts": [{"text": texto}]}


class Gerador:
    def __init__(self, cfg):
        self.cfg = cfg
        self.saida = RAIZ / "dados" / config.pasta_do_modelo(cfg["modelo"])
        self.provedor = provedores.carregar(cfg["provedor"])
        self.cliente = None

    # ---------------------------------------------------- estado em disco

    def tentativas_salvas(self, pasta):
        salvas, n = [], 1
        while (pasta / f"tentativa_{n}.json").exists():
            salvas.append(json.loads((pasta / f"tentativa_{n}.json").read_text(encoding="utf-8")))
            n += 1
        return salvas

    def finalizar(self, ex, pasta, salvas):
        resultado = {
            "slug": ex["slug"], "perfil": self.cfg["perfil"], "modelo": self.cfg["modelo"],
            "tipo_esqueleto": ex["tipo_esqueleto"],
            "status_final": salvas[-1]["status"], "tentativas": len(salvas),
            "passou_na_primeira": salvas[0]["status"] == "passou",
            "status_por_tentativa": [s["status"] for s in salvas],
        }
        (pasta / "resultado.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2),
                                              encoding="utf-8")

    def pendente(self, ex):
        pasta = self.saida / ex["slug"]
        salvas = self.tentativas_salvas(pasta)
        if salvas and (salvas[-1]["status"] == "passou" or len(salvas) >= self.cfg["max_tentativas"]):
            if not (pasta / "resultado.json").exists():
                self.finalizar(ex, pasta, salvas)
            return False
        return True

    # ------------------------------------------------------------ geração

    def montar_conversa(self, ex, salvas):
        prompt = PROMPT_INICIAL.format(enunciado=ex["enunciado"].strip(),
                                       esqueleto=ex["esqueleto"].strip(),
                                       arquivo=ex["arquivo_solucao"])
        conversa = [mensagem("user", prompt)]
        for s in salvas:
            conversa.append(mensagem("model", s["resposta"]))
            if s["status"] == "sem_codigo":
                correcao = PROMPT_SEM_CODIGO.format(arquivo=ex["arquivo_solucao"])
            else:
                correcao = PROMPT_CORRECAO.format(saida=s["saida_testes"], arquivo=ex["arquivo_solucao"])
            conversa.append(mensagem("user", correcao))
        return conversa

    def executar_tentativa(self, ex):
        """Faz UMA tentativa para o exercício: chama a LLM, testa, salva. Devolve (status, n)."""
        pasta = self.saida / ex["slug"]
        pasta.mkdir(parents=True, exist_ok=True)
        salvas = self.tentativas_salvas(pasta)
        n = len(salvas) + 1
        conversa = self.montar_conversa(ex, salvas)

        inicio = time.time()
        texto = self.provedor.chamar(self.cliente, conversa, ex, self.cfg)
        codigo = extrair_codigo(texto)
        if codigo is None:
            status, saida = "sem_codigo", "No code block found in the response."
        else:
            status, saida = rodar_testes(ex["slug"], codigo, ex["arquivo_solucao"], ex["arquivos_teste"])

        registro = {
            "slug": ex["slug"], "tentativa": n, "perfil": self.cfg["perfil"],
            "provedor": self.cfg["provedor"], "modelo": self.cfg["modelo"],
            "temperatura": self.cfg.get("temperatura"),
            "data_hora": datetime.now(timezone.utc).isoformat(),
            "segundos": round(time.time() - inicio, 2),
            "prompt": conversa[-1]["parts"][0]["text"],
            "resposta": texto, "codigo": codigo,
            "status": status, "saida_testes": saida,
        }
        (pasta / f"tentativa_{n}.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
        salvas.append(registro)
        if status == "passou" or n >= self.cfg["max_tentativas"]:
            self.finalizar(ex, pasta, salvas)
        return status, n

    def rodar(self, exercicios):
        cfg = self.cfg
        lote_max, max_t = cfg["tamanho_lote"], cfg["max_tentativas"]
        fila = [ex for ex in exercicios if self.pendente(ex)]
        rpm = cfg.get("requisicoes_por_minuto")
        print(f"Perfil: {cfg['perfil']} · {cfg['provedor']}/{cfg['modelo']} · "
              f"temperatura: {cfg.get('temperatura') if cfg.get('temperatura') is not None else 'padrão'} · "
              f"máx. tentativas: {max_t} · lote: {lote_max} · "
              f"limite: {f'{rpm:g} req/min' if rpm else 'sem limite'}")
        print(f"Exercícios: {len(exercicios)} · concluídos: {len(exercicios) - len(fila)} · "
              f"pendentes: {len(fila)}")
        if not fila:
            print(f"\nNada a fazer. Resultados em {self.saida}")
            return
        self.cliente = self.provedor.criar_cliente(cfg)

        n_lote = 0
        while fila:
            lote, fila = fila[:lote_max], fila[lote_max:]
            n_lote += 1
            print(f"\nLote {n_lote}: {len(lote)} chamadas · restam na fila: {len(fila)}")
            interromper = None
            with ThreadPoolExecutor(max_workers=lote_max) as executor:
                futuros = [(executor.submit(self.executar_tentativa, ex), ex) for ex in lote]
                for futuro, ex in futuros:
                    try:
                        status, n = futuro.result()
                    except CotaEsgotada as erro:
                        interromper = interromper or erro
                        print(f"  {ex['slug']:30s} interrompido ({str(erro)[:150]})")
                        continue
                    except Exception as erro:  # erro inesperado: para tudo sem perder o que foi salvo
                        PARAR.set()
                        interromper = interromper or erro
                        print(f"  {ex['slug']:30s} erro: {type(erro).__name__}: {str(erro)[:150]}")
                        continue
                    if status != "passou" and n < max_t:
                        fila.append(ex)  # volta para a fila: a correção entra num lote seguinte
                        destino = "volta para a fila"
                    else:
                        destino = "concluído"
                    print(f"  {ex['slug']:30s} tentativa {n}: {status:12s} → {destino}")
            if interromper:
                print("\nExecução interrompida. O progresso está salvo; rode de novo para continuar.")
                sys.exit(1)
        print(f"\nConcluído. Resultados em {self.saida}")


def main():
    perfis = list(config.carregar().get("modelos", {}))
    parser = argparse.ArgumentParser(description="Gera soluções do Exercism com uma LLM.")
    parser.add_argument("perfil", choices=perfis, help="perfil definido em config/modelos.yaml")
    parser.add_argument("--limite", type=int, default=None,
                        help="processa só os N primeiros exercícios (para testes rápidos)")
    args = parser.parse_args()

    load_dotenv(RAIZ / ".env")
    exercicios = [json.loads(l) for l in ENTRADA.read_text(encoding="utf-8").splitlines()]
    exercicios = [e for e in exercicios if e["referencia_passa"]]
    if args.limite:
        exercicios = exercicios[:args.limite]
    Gerador(config.perfil(args.perfil)).rodar(exercicios)


if __name__ == "__main__":
    main()
