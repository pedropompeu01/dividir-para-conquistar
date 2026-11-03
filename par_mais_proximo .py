# Etapa 2 - Par de pontos mais próximos
# Uso: python par_mais_proximo.py            (modo interativo)
#      python par_mais_proximo.py --simples  (lê "n x1 y1 ... xn yn" e imprime "distancia i j")

import math
import sys
import time
from operator import itemgetter

LIMIAR = 16  # até esse tamanho a D&C usa força bruta (escolhido nas medições)
INFINITO = (math.inf, -1, -1)


# O(n^2): compara todos os pares (com a distância ao quadrado, sem raiz)
def forca_bruta(pontos):
    n = len(pontos)
    melhor_d2, melhor_i, melhor_j = math.inf, -1, -1
    for i in range(n - 1):
        xi, yi = pontos[i]
        for j in range(i + 1, n):
            xj, yj = pontos[j]
            dx = xi - xj
            dy = yi - yj
            d2 = dx * dx + dy * dy
            if d2 < melhor_d2:  # só troca se for menor (desempate: menor par i, j)
                melhor_d2, melhor_i, melhor_j = d2, i, j
    return (math.sqrt(melhor_d2), melhor_i, melhor_j)


# O(n log n): ordena por x e por y uma vez e faz T(n) = 2T(n/2) + O(n)
def divisao_conquista(pontos, limiar=LIMIAR):
    marcados = [(x, y, i) for i, (x, y) in enumerate(pontos)]
    px = sorted(marcados)
    coincidentes = _par_coincidente(px)  # pontos repetidos: distância 0
    if coincidentes is not None:
        return (0.0, coincidentes[0], coincidentes[1])
    py = sorted(marcados, key=itemgetter(1))
    lado_esquerdo = [False] * len(pontos)
    d2, i, j = _dc(px, py, limiar, lado_esquerdo)
    return (math.sqrt(d2), i, j)


# pontos iguais ficam vizinhos em px; retorna o menor par (i, j) ou None
def _par_coincidente(px):
    melhor = None
    for k in range(len(px) - 1):
        a, b = px[k], px[k + 1]
        if a[0] == b[0] and a[1] == b[1]:
            inicio_de_grupo = k == 0 or px[k - 1][0] != a[0] or px[k - 1][1] != a[1]
            if inicio_de_grupo and (melhor is None or (a[2], b[2]) < melhor):
                melhor = (a[2], b[2])
    return melhor


def _dc(px, py, limiar, lado_esquerdo):
    n = len(px)
    if n <= limiar:
        return _forca_bruta_base(px)
    # divide pela mediana de x
    meio = n // 2
    x_meio = px[meio - 1][0]
    esquerda_x, direita_x = px[:meio], px[meio:]
    for p in esquerda_x:
        lado_esquerdo[p[2]] = True
    for p in direita_x:
        lado_esquerdo[p[2]] = False
    # separa py sem precisar ordenar de novo
    esquerda_y = [p for p in py if lado_esquerdo[p[2]]]
    direita_y = [p for p in py if not lado_esquerdo[p[2]]]
    melhor = min(_dc(esquerda_x, esquerda_y, limiar, lado_esquerdo),
                 _dc(direita_x, direita_y, limiar, lado_esquerdo))
    # faixa de largura 2*delta em volta da linha (<= para não perder empates)
    delta2 = melhor[0]
    faixa = [p for p in py if (p[0] - x_meio) * (p[0] - x_meio) <= delta2]
    return _verificar_faixa(faixa, melhor)


# cada ponto da faixa só precisa ser comparado com os 7 seguintes em y
def _verificar_faixa(faixa, melhor):
    m = len(faixa)
    for a in range(m - 1):
        xa, ya, ia = faixa[a]
        for b in range(a + 1, min(a + 8, m)):
            xb, yb, ib = faixa[b]
            dy = yb - ya
            if dy * dy > melhor[0]:
                break
            dx = xb - xa
            d2 = dx * dx + dy * dy
            if d2 <= melhor[0]:
                candidato = (d2, ia, ib) if ia < ib else (d2, ib, ia)
                if candidato < melhor:
                    melhor = candidato
    return melhor


# caso base: pontos no formato (x, y, índice)
def _forca_bruta_base(pts):
    melhor = INFINITO
    n = len(pts)
    for a in range(n - 1):
        xa, ya, ia = pts[a]
        for b in range(a + 1, n):
            xb, yb, ib = pts[b]
            dx = xa - xb
            dy = ya - yb
            d2 = dx * dx + dy * dy
            if d2 <= melhor[0]:
                candidato = (d2, ia, ib) if ia < ib else (d2, ib, ia)
                if candidato < melhor:
                    melhor = candidato
    return melhor


ALGORITMOS = {
    "1": ("Força bruta", "O(n²)", forca_bruta),
    "2": ("Divisão e conquista", "O(n log n)", divisao_conquista),
}


# int quando der (conta exata), senão float; nan e inf não valem
def numero(texto):
    try:
        return int(texto)
    except ValueError:
        valor = float(texto)
        if not math.isfinite(valor):
            raise ValueError(texto)
        return valor


def ler_n():
    while True:
        try:
            n = int(input("Insira a quantidade de estações (n >= 2): "))
            if n >= 2:
                return n
        except ValueError:
            pass
        print("  Valor inválido: digite um número inteiro maior ou igual a 2.")


def ler_estacoes(n):
    print(f"Insira as coordenadas x e y das {n} estações (separadas por espaço; use ponto "
          f"para decimais)\npara calcular o par de estações mais próximas:")
    pontos = []
    while len(pontos) < n:
        try:
            x, y = map(numero, input(f"  Estação {len(pontos) + 1}: ").split())
            pontos.append((x, y))
        except ValueError:
            print("  Valor inválido: digite dois números, por exemplo: 2.5 3")
    return pontos


def escolher_algoritmos():
    print("\nEscolha o algoritmo:")
    for codigo, (nome, ordem, _) in ALGORITMOS.items():
        print(f"  {codigo} - {nome} {ordem}")
    print("  3 - Os dois (compara os resultados e os tempos)")
    while True:
        try:
            opcao = input("Insira o número da opção [Enter = 3]: ").strip() or "3"
        except EOFError:
            opcao = "3"
        if opcao == "3":
            return list(ALGORITMOS)
        if opcao in ALGORITMOS:
            return [opcao]
        print("  Opção inválida.")


def calcular_e_mostrar(pontos, codigo):
    nome, ordem, funcao = ALGORITMOS[codigo]
    inicio = time.perf_counter()
    distancia, i, j = funcao(pontos)
    tempo = time.perf_counter() - inicio
    (xi, yi), (xj, yj) = pontos[i], pontos[j]
    print(f"\n{nome} {ordem}:")
    print(f"  O cálculo do par de estações mais próximas deu a estação {i + 1} ({xi}, {yi})")
    print(f"  e a estação {j + 1} ({xj}, {yj}), com distância "
          f"raiz(({xi} - {xj})² + ({yi} - {yj})²) = {distancia:.6f}")
    print(f"  Tempo de execução: {tempo * 1000:.3f} ms")
    return (distancia, i, j)


# modo para testes automáticos: imprime só "distancia i j"
def modo_simples():
    try:
        textos = sys.stdin.read().split()
        n = int(textos[0])
        if n < 2 or len(textos) < 2 * n + 1:
            raise ValueError
        valores = [numero(t) for t in textos[1:2 * n + 1]]
    except (ValueError, IndexError):
        print("Erro: a entrada deve ser n (>= 2) seguido de n pares de coordenadas x y.",
              file=sys.stderr)
        return 1
    pontos = list(zip(valores[0::2], valores[1::2]))
    distancia, i, j = divisao_conquista(pontos)
    base = 0 if "--base0" in sys.argv else 1  # --base0: índices a partir de 0
    print(f"{distancia:.6f} {i + base} {j + base}")
    return 0


def main():
    if "--simples" in sys.argv:
        return modo_simples()
    print("=== ETAPA 2 - PAR DE PONTOS MAIS PRÓXIMOS ===")
    try:
        pontos = ler_estacoes(ler_n())
    except EOFError:
        print("\nA entrada terminou antes de todos os dados serem lidos.", file=sys.stderr)
        return 1
    resultados = [calcular_e_mostrar(pontos, codigo) for codigo in escolher_algoritmos()]
    if len(resultados) > 1 and len(set(resultados)) == 1:
        print("\nOs dois algoritmos chegaram ao mesmo resultado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
