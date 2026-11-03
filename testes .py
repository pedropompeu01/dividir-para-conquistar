# Testes das Etapas 1 e 2
# Uso: python testes.py   (no final deve aparecer "OK")

import math
import os
import random
import subprocess
import sys
import unittest

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PASTA)

import par_mais_proximo as pm    # noqa: E402
import subarranjo_maximo as sm   # noqa: E402

VERSOES_1 = [sm.forca_bruta, sm.divisao_conquista, sm.kadane, sm.divisao_conquista_linear]
# Etapa 2: força bruta e D&C com limiares 2 e 3 (recursão até o fim) e 16 (o adotado).
VERSOES_2 = [pm.forca_bruta] + [lambda p, L=L: pm.divisao_conquista(p, L) for L in (2, 3, 16)]


# oráculo O(n^3): recalcula cada soma do zero
def oraculo_soma(v):
    melhor = None
    for i in range(len(v)):
        for j in range(i, len(v)):
            if melhor is None or sum(v[i:j + 1]) > melhor[0]:
                melhor = (sum(v[i:j + 1]), i, j)
    return melhor


# oráculo O(n^2): menor (distância², i, j)
def oraculo_par(p):
    pares = []
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            dx, dy = p[i][0] - p[j][0], p[i][1] - p[j][1]
            pares.append((dx * dx + dy * dy, i, j))
    return min(pares)


def ler_casos():
    casos = []
    with open(os.path.join(PASTA, "casos_de_teste.txt"), encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha.startswith("["):
                etapa, nome = linha[1:].split("] ")
                casos.append({"etapa": etapa, "nome": nome})
            elif linha.startswith("Entrada:"):
                casos[-1]["entrada"] = linha[len("Entrada:"):].strip()
            elif linha.startswith("Saída esperada:"):
                casos[-1]["saida"] = linha[len("Saída esperada:"):].strip()
    return casos


def rodar(programa, argumentos, entrada):
    return subprocess.run([sys.executable, os.path.join(PASTA, programa), *argumentos],
                          input=entrada, capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=60)


# conta quantos vizinhos ficam a no máximo delta em y na faixa (sem o limite de 7)
def contar_vizinhos_na_faixa(instancias=60, semente=77):
    g = random.Random(semente)
    tipos = [lambda n: [(g.random(), g.random()) for _ in range(n)],
             lambda n: [(c // 40, c % 40) for c in g.sample(range(1600), n)],
             lambda n: [(g.choice([0, 1]) + g.random() * 1e-3, g.random()) for _ in range(n)],
             lambda n: [(0, y) for y in g.sample(range(5000), n)]]
    maior = 0
    original = pm._verificar_faixa

    def espiao(faixa, melhor):
        nonlocal maior
        for a in range(len(faixa)):
            b = a + 1
            while b < len(faixa) and (faixa[b][1] - faixa[a][1]) ** 2 <= melhor[0]:
                b += 1
            maior = max(maior, b - a - 1)
        return original(faixa, melhor)

    pm._verificar_faixa = espiao
    try:
        for tipo in tipos:
            for _ in range(instancias):
                pm.divisao_conquista(tipo(g.randint(20, 400)), 3)
    finally:
        pm._verificar_faixa = original
    return maior, instancias * len(tipos)


class Etapa1(unittest.TestCase):
    def confere(self, v, esperado):
        for funcao in VERSOES_1:
            self.assertEqual(funcao(v), esperado, funcao.__name__)

    def test_so_negativos(self):
        # a resposta é o maior elemento, não 0
        self.confere([-5, -2, -8, -1, -3], (-1, 3, 3))
        self.confere([-3, -3, -3], (-3, 0, 0))

    def test_tamanho_1(self):
        # caso base da recursão
        self.confere([42], (42, 0, 0))
        self.confere([-42], (-42, 0, 0))

    def test_empates(self):
        # menor início, depois menor fim (inclusive na combinação da D&C)
        self.confere([3, -5, 3], (3, 0, 0))
        self.confere([2, -2, 2], (2, 0, 0))
        self.confere([0, 0, 5, 0, 0], (5, 0, 2))
        self.confere([4, -9, 1, 3, -9, 4], (4, 0, 0))

    def test_resposta_cruza_o_meio(self):
        self.confere([-10, 2, 3, 4, -10], (9, 1, 3))

    def test_aleatorios_contra_oraculo(self):
        # faixas pequenas de valores geram muitos empates
        g = random.Random(2026)
        for minimo, maximo in [(-1, 1), (-2, 2), (-10, 10), (-100, -1), (-1000, 1000)]:
            for _ in range(200):
                v = [g.randint(minimo, maximo) for _ in range(g.randint(1, 20))]
                self.confere(v, oraculo_soma(v))


class Etapa2(unittest.TestCase):
    def confere(self, pontos, distancia, i, j):
        for funcao in VERSOES_2:
            d, a, b = funcao(pontos)
            self.assertAlmostEqual(d, distancia, places=9)
            self.assertEqual((a, b), (i, j))

    def test_dois_e_tres_pontos(self):
        self.confere([(0, 0), (3, 4)], 5.0, 0, 1)
        self.confere([(0, 0), (10, 10), (1, 1)], math.sqrt(2), 0, 2)

    def test_pontos_coincidentes(self):
        # distância 0, tratada antes da recursão
        self.confere([(2, 2), (7, 7), (7, 7), (2, 2)], 0.0, 0, 3)

    def test_mesmo_x_e_mesmo_y(self):
        self.confere([(0, 0), (0, 10), (0, 3), (0, 7), (0, 20)], 3.0, 0, 2)
        self.confere([(0, 5), (9, 5), (4, 5), (2, 5), (15, 5)], 2.0, 0, 3)

    def test_par_cruza_a_divisao(self):
        # um ponto de cada lado: só a faixa encontra
        self.confere([(20, 0), (9, 10), (0, 20), (10, 10), (0, 0), (20, 20)], 1.0, 1, 3)

    def test_ponto_exatamente_a_delta_da_linha(self):
        # com < na faixa o ponto (7, 0) ficaria de fora e a resposta mudaria
        self.confere([(5, 0), (7, 0), (0, 10), (0, 12), (20, 30), (20, 50)], 2.0, 0, 1)

    def test_empates_em_grade(self):
        grade = [(2, 2), (0, 1), (1, 0), (2, 0), (0, 0), (1, 2), (0, 2), (2, 1), (1, 1)]
        self.confere(grade, 1.0, 0, 5)

    def test_coordenadas_especiais(self):
        # negativas, decimais e perto de 10^9
        self.confere([(-5, -5), (-1, -2), (3, 1), (-4, -4)], math.sqrt(2), 0, 3)
        self.confere([(0.5, 0.5), (1.25, 0.5), (3.0, 3.0), (0.5, 1.5)], 0.75, 0, 1)
        self.confere([(10**9, 10**9), (10**9 + 1, 10**9 + 1), (-10**9, 0)], math.sqrt(2), 0, 1)

    def test_bastam_7_vizinhos(self):
        maior, _ = contar_vizinhos_na_faixa()
        self.assertLessEqual(maior, 7)

    def test_aleatorios_contra_oraculo(self):
        # inteiros pequenos (empates e repetidos), grade, decimais e grupos
        g = random.Random(2026)
        tipos = [lambda n: [(g.randint(-5, 5), g.randint(-5, 5)) for _ in range(n)],
                 lambda n: [(2 * (c // 20), 2 * (c % 20)) for c in g.sample(range(400), n)],
                 lambda n: [(g.uniform(-99, 99), g.uniform(-99, 99)) for _ in range(n)],
                 lambda n: [(g.choice([0, 500]) + g.random(), g.choice([0, 500]) + g.random())
                            for _ in range(n)]]
        for tipo in tipos:
            for _ in range(200):
                pontos = tipo(g.randint(2, 60))
                d2, i, j = oraculo_par(pontos)
                self.confere(pontos, math.sqrt(d2), i, j)


class ArquivoDeCasos(unittest.TestCase):
    def setUp(self):
        self.casos = ler_casos()

    def numeros(self, caso):
        return [float(t) if "." in t or "e" in t else int(t) for t in caso["entrada"].split()]

    def test_saidas_conferem_com_oraculos(self):
        for caso in self.casos:
            if caso["saida"] == "ERRO":
                continue
            v = self.numeros(caso)
            if caso["etapa"] == "etapa1":
                soma, i, j = oraculo_soma(v[1:])
                esperado = f"{soma} {i + 1} {j + 1}"
            else:
                d2, i, j = oraculo_par(list(zip(v[1::2], v[2::2])))
                esperado = f"{math.sqrt(d2):.6f} {i + 1} {j + 1}"
            self.assertEqual(esperado, caso["saida"], caso["nome"])

    def test_todas_as_versoes(self):
        for caso in self.casos:
            if caso["saida"] == "ERRO":
                continue
            v = self.numeros(caso)
            if caso["etapa"] == "etapa1":
                for funcao in VERSOES_1:
                    soma, i, j = funcao(v[1:])
                    self.assertEqual(f"{soma} {i + 1} {j + 1}", caso["saida"], caso["nome"])
            else:
                for funcao in VERSOES_2:
                    d, i, j = funcao(list(zip(v[1::2], v[2::2])))
                    self.assertEqual(f"{d:.6f} {i + 1} {j + 1}", caso["saida"], caso["nome"])

    def test_programas_modo_simples(self):
        # roda cada caso no programa, como o professor rodaria
        for caso in self.casos:
            programa = "subarranjo_maximo.py" if caso["etapa"] == "etapa1" else "par_mais_proximo.py"
            r = rodar(programa, ["--simples"], caso["entrada"])
            if caso["saida"] == "ERRO":
                self.assertEqual(r.returncode, 1, caso["nome"])
                self.assertIn("Erro", r.stderr)
            else:
                self.assertEqual(r.stdout.strip(), caso["saida"], caso["nome"])


class Interface(unittest.TestCase):
    def test_etapa1(self):
        r = rodar("subarranjo_maximo.py", [], "abc\n9\n-2 1 -3 4 -1 2 1 -5 4\n5\n")
        for trecho in ["Valor inválido", "Insira as 9 variações", "deu 6", "do dia 4 ao dia 7",
                       "4 + (-1) + 2 + 1 = 6", "Tempo de execução", "mesmo resultado"]:
            self.assertIn(trecho, r.stdout)

    def test_etapa2(self):
        r = rodar("par_mais_proximo.py", [], "1\n5\n0 0\n3 4\nabc\n10 10\n4 4\n20 1\n3\n")
        for trecho in ["Valor inválido", "Estação 5", "a estação 2 (3, 4)", "a estação 4 (4, 4)",
                       "= 1.000000", "Tempo de execução", "mesmo resultado"]:
            self.assertIn(trecho, r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
