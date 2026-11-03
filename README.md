# Dividir para Conquistar

Comparação entre algoritmos de **divisão e conquista** e de **força bruta** em dois problemas
clássicos, o subarranjo de soma máxima e o par de pontos mais próximos, com medição real dos
tempos de execução.

**Autor:** Pedro Pompeu

## Sobre o projeto

Divisão e conquista é uma técnica que quebra um problema em partes menores, resolve cada parte
e junta as respostas. Em muitos problemas ela troca uma solução O(n²), que compara tudo com tudo,
por uma O(n log n), que continua rápida mesmo com centenas de milhares de dados.

Este projeto implementa as duas abordagens para dois problemas e mede quanto tempo cada uma leva.

**Subarranjo de soma máxima.** Dada a variação diária do preço de uma ação, encontra o período
contínuo de dias com o maior ganho acumulado. Serve para achar a melhor janela de valorização
em uma série de dados, como preços, vendas ou temperaturas.

**Par de pontos mais próximos.** Dadas as coordenadas de várias estações de monitoramento,
encontra as duas mais próximas entre si, por exemplo para identificar risco de interferência
entre elas. A mesma ideia aparece em detecção de colisão, agrupamento de dados e mapas.

### Objetivo

- Implementar a força bruta e a divisão e conquista dos dois problemas, além de duas versões
  O(n) para o subarranjo de soma máxima (Kadane e uma divisão e conquista linear).
- Verificar com medições se o tempo cresce como a análise prevê: O(n²), O(n log n) e O(n).
- Descobrir até que tamanho a força bruta ainda é mais rápida e usar isso para escolher o
  limiar da divisão e conquista: abaixo dele, o problema é resolvido por força bruta.

### Principais resultados

- Com 6.400 elementos, a divisão e conquista foi cerca de **110 vezes** mais rápida que a força
  bruta no subarranjo de soma máxima e **84 vezes** no par de pontos mais próximos.
- Os tempos medidos seguem a complexidade prevista: o da força bruta quadruplica quando a
  entrada dobra, e o da divisão e conquista pouco mais que dobra.
- Para entradas muito pequenas (até cerca de 30 a 45 elementos), a força bruta vence. Por isso o par de
  pontos mais próximos usa força bruta em subproblemas de até 16 pontos.

A análise completa, com tabelas e gráficos, está em `relatorio.pdf`.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `subarranjo_maximo.py` | subarranjo de soma máxima: força bruta O(n²), divisão e conquista O(n log n), Kadane O(n) e D&C linear O(n) |
| `par_mais_proximo.py` | par de pontos mais próximos: força bruta O(n²) e divisão e conquista O(n log n) |
| `testes.py` | testes automáticos; também confere todos os casos de `casos_de_teste.txt` |
| `casos_de_teste.txt` | casos de teste com entrada, saída esperada e motivo de cada um |
| `medicoes.py` / `medicoes.csv` | script de medição dos tempos e as medições usadas no relatório |
| `relatorio.pdf` | relatório com a análise |

## Como executar

Precisa do Python 3.8 ou mais recente; só a biblioteca padrão é usada.

```
python subarranjo_maximo.py     # pede os dados, deixa escolher o algoritmo e mostra o cálculo
python par_mais_proximo.py      # idem, para o par de pontos mais próximos
python testes.py                # roda todos os testes (deve terminar com "OK")
python medicoes.py              # refaz as medições (2 a 3 minutos; substitui medicoes.csv)
```

Com `--simples`, os programas leem a entrada direto e imprimem só a resposta (útil para testes
automáticos). Com `--base0`, os índices começam em 0 em vez de 1.

```
$ echo "9  -2 1 -3 4 -1 2 1 -5 4" | python subarranjo_maximo.py --simples
6 4 7                           # soma, dia de início, dia de fim
$ echo "3  0 0  10 10  1 1" | python par_mais_proximo.py --simples
1.414214 1 3                    # distância, estação i, estação j
```

**Formato da entrada:** `n` seguido dos `n` valores (subarranjo) ou dos `n` pares `x y`
(pontos), separados por espaços ou quebras de linha.

**Desempate:** no subarranjo vence o intervalo de menor início e, depois, o de menor fim; nos
pontos, o menor par (i, j). Uma entrada inválida gera mensagem de erro (código de saída 1).

## Máquina usada nas medições

Intel Xeon @ 2,10 GHz (máquina virtual, 2 núcleos lógicos), 7,8 GB de RAM, Linux,
CPython 3.13.16, em 27/10/2026. Os algoritmos usam um único núcleo.
