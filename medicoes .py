# Etapa 3 - medição dos tempos (gera medicoes.csv, uma linha por execução)
# Uso: python medicoes.py           (2 a 3 minutos; substitui medicoes.csv)
#      python medicoes.py --rapido  (só para testar; grava medicoes_rapido.csv)
# Cada tamanho roda 10 vezes; a mesma instância vai para todos os algoritmos.

import csv
import functools
import gc
import os
import platform
import random
import sys
import time

import par_mais_proximo as pm
import subarranjo_maximo as sm

RAPIDO = "--rapido" in sys.argv
REPETICOES = 5 if RAPIDO else 10
TAMANHOS = [100, 200, 400] if RAPIDO else [100, 200, 400, 800, 1600, 3200, 6400]
EXTRAS = [800, 1600] if RAPIDO else [12800, 25600, 51200, 102400, 204800]  # sem força bruta
PEQUENOS = [2, 4, 8, 16] if RAPIDO else [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
LIMIARES = [2, 4, 8, 16] if RAPIDO else [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]
FAIXAS = [(300, 600)] if RAPIDO else [(1000, 2000), (4000, 8000), (16000, 32000)]

ALGORITMOS = {
    1: [("forca_bruta", sm.forca_bruta), ("divisao_conquista", sm.divisao_conquista),
        ("kadane", sm.kadane), ("divisao_conquista_linear", sm.divisao_conquista_linear)],
    2: [("forca_bruta", pm.forca_bruta), ("divisao_conquista", pm.divisao_conquista)],
}
COLUNAS = ["experimento", "etapa", "algoritmo", "n", "limiar", "faixa", "execucao",
           "instancias", "semente", "tempo_s"]


# etapa 1: inteiros em [-100, 100]; etapa 2: pontos em [0, 1000)
def gerar(etapa, n, semente):
    g = random.Random(semente)
    if etapa == 1:
        return [g.randint(-100, 100) for _ in range(n)]
    return [(g.random() * 1000.0, g.random() * 1000.0) for _ in range(n)]


# tempo médio por chamada, com o coletor de lixo desligado
def medir(funcao, instancias):
    gc.collect()
    gc.disable()
    inicio = time.perf_counter_ns()
    for instancia in instancias:
        resultado = funcao(instancia)
    tempo = (time.perf_counter_ns() - inicio) / 1e9 / len(instancias)
    gc.enable()
    return tempo, resultado


def linha(experimento, etapa, algoritmo, n, execucao, semente, tempo, limiar="", faixa="",
          instancias=1):
    return dict(experimento=experimento, etapa=etapa, algoritmo=algoritmo, n=n, limiar=limiar,
                faixa=faixa, execucao=execucao, instancias=instancias, semente=semente,
                tempo_s=f"{tempo:.12f}")


def experimento_tempos(etapa):
    linhas = []
    print(f"\n[Etapa {etapa}] tempo médio (ms) de {REPETICOES} execuções:")
    for n in TAMANHOS + EXTRAS:
        algoritmos = [a for a in ALGORITMOS[etapa] if n in TAMANHOS or a[0] != "forca_bruta"]
        soma = {nome: 0.0 for nome, _ in algoritmos}
        for execucao in range(1, REPETICOES + 1):
            semente = etapa * 10_000_000 + n * 1000 + execucao
            instancia = gerar(etapa, n, semente)
            ordem = list(algoritmos)
            random.Random(semente).shuffle(ordem)
            resultados = set()
            for nome, funcao in ordem:
                tempo, resultado = medir(funcao, [instancia])
                resultados.add(resultado)
                soma[nome] += tempo
                limiar = pm.LIMIAR if (etapa == 2 and nome == "divisao_conquista") else ""
                linhas.append(linha("tempos", etapa, nome, n, execucao, semente, tempo, limiar))
            assert len(resultados) == 1, f"resultados diferentes (n={n})"
        print(f"  n = {n:>6}: " + "  ".join(f"{nome} {t / REPETICOES * 1000:.3f}"
                                            for nome, t in soma.items()))
    return linhas


# n pequeno: mede lotes de instâncias, porque cada chamada leva microssegundos
def experimento_cruzamento():
    linhas = []
    print("\n[Tamanhos pequenos] tempo por instância (µs):")
    variantes = {1: [(nome, funcao, "") for nome, funcao in ALGORITMOS[1]],
                 2: [("forca_bruta", pm.forca_bruta, ""),
                     ("divisao_conquista", functools.partial(pm.divisao_conquista, limiar=3), 3),
                     ("divisao_conquista", pm.divisao_conquista, pm.LIMIAR)]}
    for etapa, lista in variantes.items():
        for n in PEQUENOS:
            lote = max(50, 6000 // n)
            soma = [0.0] * len(lista)
            for execucao in range(1, REPETICOES + 1):
                semente = (etapa + 2) * 10_000_000 + n * 100_000 + execucao * 1000
                instancias = [gerar(etapa, n, semente + k) for k in range(lote)]
                ordem = list(range(len(lista)))
                random.Random(semente).shuffle(ordem)
                for k in ordem:
                    nome, funcao, limiar = lista[k]
                    tempo, _ = medir(funcao, instancias)
                    soma[k] += tempo
                    linhas.append(linha("cruzamento", etapa, nome, n, execucao, semente, tempo,
                                        limiar, instancias=lote))
            print(f"  Etapa {etapa}, n = {n:>3}: "
                  + "  ".join(f"{s / REPETICOES * 1e6:.2f}" for s in soma))
    return linhas


# n é sorteado na faixa: com n fixo, limiares diferentes podem dar a mesma recursão
def experimento_limiar():
    linhas = []
    print("\n[Limiar da Etapa 2] tempo relativo ao melhor limiar de cada execução:")
    for minimo, maximo in FAIXAS:
        relativo = {limiar: 0.0 for limiar in LIMIARES}
        for execucao in range(1, REPETICOES + 1):
            semente = 50_000_000 + minimo * 100 + execucao
            g = random.Random(semente)
            n = g.randint(minimo, maximo)
            pontos = gerar(2, n, semente)
            ordem = list(LIMIARES)
            g.shuffle(ordem)
            tempos = {}
            for limiar in ordem:
                tempos[limiar], _ = medir(functools.partial(pm.divisao_conquista, limiar=limiar),
                                          [pontos])
            for limiar in LIMIARES:
                relativo[limiar] += tempos[limiar] / min(tempos.values()) / REPETICOES
                linhas.append(linha("limiar", 2, "divisao_conquista", n, execucao, semente,
                                    tempos[limiar], limiar, f"{minimo}-{maximo}"))
        print(f"  n entre {minimo} e {maximo}: "
              + "  ".join(f"L={limiar}: {r:.2f}" for limiar, r in relativo.items()))
    return linhas


def main():
    print(f"Máquina: {platform.processor() or platform.machine()}, {os.cpu_count()} núcleos, "
          f"{platform.platform()}, Python {platform.python_version()}")
    for etapa, algoritmos in ALGORITMOS.items():  # aquecimento
        for _, funcao in algoritmos:
            funcao(gerar(etapa, 500, 1))
    linhas = experimento_limiar() + experimento_tempos(1) + experimento_tempos(2)
    linhas += experimento_cruzamento()
    arquivo = "medicoes_rapido.csv" if RAPIDO else "medicoes.csv"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), arquivo), "w",
              encoding="utf-8", newline="") as saida:
        escritor = csv.DictWriter(saida, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"\nMedições salvas em {arquivo} ({len(linhas)} linhas).")


if __name__ == "__main__":
    main()
