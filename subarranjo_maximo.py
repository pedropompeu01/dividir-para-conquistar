# Etapa 1 - Subarranjo de soma máxima
# Uso: python subarranjo_maximo.py            (modo interativo)
#      python subarranjo_maximo.py --simples  (lê "n v1 ... vn" e imprime "soma inicio fim")

import sys
import time


# O(n^2): testa todos os intervalos, aproveitando a soma do anterior
def forca_bruta(v):
    n = len(v)
    melhor_soma, melhor_ini, melhor_fim = v[0], 0, 0
    for i in range(n):
        soma = 0
        for j in range(i, n):
            soma += v[j]
            if soma > melhor_soma:  # só troca se for maior (desempate: menor início e fim)
                melhor_soma, melhor_ini, melhor_fim = soma, i, j
    return (melhor_soma, melhor_ini, melhor_fim)


# O(n log n): T(n) = 2T(n/2) + O(n)
def divisao_conquista(v):
    return _dc(v, 0, len(v) - 1)


def _dc(v, ini, fim):
    if ini == fim:
        return (v[ini], ini, ini)
    meio = (ini + fim) // 2
    esquerda = _dc(v, ini, meio)
    direita = _dc(v, meio + 1, fim)
    cruzado = _cruza_o_meio(v, ini, meio, fim)
    return _melhor(_melhor(esquerda, cruzado), direita)


# melhor sufixo da esquerda + melhor prefixo da direita
def _cruza_o_meio(v, ini, meio, fim):
    soma = 0
    melhor_esq, inicio = v[meio], meio
    for i in range(meio, ini - 1, -1):
        soma += v[i]
        if soma >= melhor_esq:  # >= para ficar com o menor início
            melhor_esq, inicio = soma, i
    soma = 0
    melhor_dir, final = v[meio + 1], meio + 1
    for j in range(meio + 1, fim + 1):
        soma += v[j]
        if soma > melhor_dir:  # > para ficar com o menor fim
            melhor_dir, final = soma, j
    return (melhor_esq + melhor_dir, inicio, final)


# maior soma; no empate, menor início e depois menor fim
def _melhor(a, b):
    if a[0] != b[0]:
        return a if a[0] > b[0] else b
    return a if (a[1], a[2]) <= (b[1], b[2]) else b


# questão desafio, O(n): atual = maior soma que termina em j
def kadane(v):
    melhor_soma, melhor_ini, melhor_fim = v[0], 0, 0
    atual, atual_ini = v[0], 0
    for j in range(1, len(v)):
        if atual >= 0:
            atual += v[j]
        else:
            atual, atual_ini = v[j], j
        if atual > melhor_soma:
            melhor_soma, melhor_ini, melhor_fim = atual, atual_ini, j
    return (melhor_soma, melhor_ini, melhor_fim)


# questão desafio, O(n) por divisão e conquista: T(n) = 2T(n/2) + O(1)
def divisao_conquista_linear(v):
    return _dc_linear(v, 0, len(v) - 1)[5]


# retorna (total, prefixo, fim do prefixo, sufixo, início do sufixo, melhor)
def _dc_linear(v, ini, fim):
    if ini == fim:
        x = v[ini]
        return (x, x, ini, x, ini, (x, ini, ini))
    meio = (ini + fim) // 2
    te, pe, pfe, se, sie, me = _dc_linear(v, ini, meio)
    td, pd, pfd, sd, sid, md = _dc_linear(v, meio + 1, fim)
    if pe >= te + pd:
        prefixo, fim_prefixo = pe, pfe
    else:
        prefixo, fim_prefixo = te + pd, pfd
    if td + se >= sd:
        sufixo, ini_sufixo = td + se, sie
    else:
        sufixo, ini_sufixo = sd, sid
    cruzado = (se + pd, sie, pfd)
    melhor = _melhor(_melhor(me, cruzado), md)
    return (te + td, prefixo, fim_prefixo, sufixo, ini_sufixo, melhor)


ALGORITMOS = {
    "1": ("Força bruta", "O(n²)", forca_bruta),
    "2": ("Divisão e conquista", "O(n log n)", divisao_conquista),
    "3": ("Kadane (questão desafio)", "O(n)", kadane),
    "4": ("Divisão e conquista linear (questão desafio)", "O(n)", divisao_conquista_linear),
}


def ler_n():
    while True:
        try:
            n = int(input("Insira a quantidade de dias (n >= 1): "))
            if n >= 1:
                return n
        except ValueError:
            pass
        print("  Valor inválido: digite um número inteiro maior ou igual a 1.")


def ler_variacoes(n):
    valores = []
    mensagem = (f"Insira as {n} variações diárias (inteiros separados por espaço) "
                f"para calcular o subarranjo de soma máxima:\n> ")
    while len(valores) < n:
        for texto in input(mensagem).split():
            try:
                valores.append(int(texto))
            except ValueError:
                print(f"  '{texto}' não é um número inteiro e foi ignorado.")
        mensagem = f"Faltam {n - len(valores)} valor(es):\n> "
    return valores[:n]


def escolher_algoritmos():
    print("\nEscolha o algoritmo:")
    for codigo, (nome, ordem, _) in ALGORITMOS.items():
        print(f"  {codigo} - {nome} {ordem}")
    print("  5 - Todos (compara os resultados e os tempos)")
    while True:
        try:
            opcao = input("Insira o número da opção [Enter = 5]: ").strip() or "5"
        except EOFError:
            opcao = "5"
        if opcao == "5":
            return list(ALGORITMOS)
        if opcao in ALGORITMOS:
            return [opcao]
        print("  Opção inválida.")


def calcular_e_mostrar(v, codigo):
    nome, ordem, funcao = ALGORITMOS[codigo]
    inicio = time.perf_counter()
    soma, i, j = funcao(v)
    tempo = time.perf_counter() - inicio
    termos = [str(x) if x >= 0 else f"({x})" for x in v[i:j + 1]]
    conta = " + ".join(termos[:10]) + (" + ..." if len(termos) > 10 else "")
    print(f"\n{nome} {ordem}:")
    print(f"  O cálculo do subarranjo de soma máxima deu {soma} (maior ganho acumulado),")
    print(f"  do dia {i + 1} ao dia {j + 1}: {conta} = {soma}")
    print(f"  Tempo de execução: {tempo * 1000:.3f} ms")
    return (soma, i, j)


# modo para testes automáticos: imprime só "soma inicio fim"
def modo_simples():
    try:
        numeros = [int(texto) for texto in sys.stdin.read().split()]
        n = numeros[0]
        if n < 1 or len(numeros) < n + 1:
            raise ValueError
    except (ValueError, IndexError):
        print("Erro: a entrada deve ser n (>= 1) seguido de n números inteiros.", file=sys.stderr)
        return 1
    soma, i, j = divisao_conquista(numeros[1:n + 1])
    base = 0 if "--base0" in sys.argv else 1  # --base0: índices a partir de 0
    print(soma, i + base, j + base)
    return 0


def main():
    if "--simples" in sys.argv:
        return modo_simples()
    print("=== ETAPA 1 - SUBARRANJO DE SOMA MÁXIMA ===")
    try:
        v = ler_variacoes(ler_n())
    except EOFError:
        print("\nA entrada terminou antes de todos os dados serem lidos.", file=sys.stderr)
        return 1
    resultados = [calcular_e_mostrar(v, codigo) for codigo in escolher_algoritmos()]
    if len(resultados) > 1 and len(set(resultados)) == 1:
        print("\nTodos os algoritmos chegaram ao mesmo resultado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
