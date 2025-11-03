# Análise Detalhada dos Testes - Compilador MiniPar

Este documento explica como cada teste funciona e como foi transformado do código base do PDF para a linguagem MiniPar.

---

## 📋 Índice

1. [Teste 1 - Servidor/Calculadora](#teste-1---servidorcalculadora)
2. [Teste 2 - Threads/Paralelismo](#teste-2---threadsparalelismo)
3. [Teste 3 - Neurônio](#teste-3---neurônio)
4. [Teste 4 - XOR](#teste-4---xor)
5. [Teste 5 - Rede Neural](#teste-5---rede-neural)
6. [Teste 6 - Fatorial](#teste-6---fatorial)
7. [Teste 7 - Fibonacci](#teste-7---fibonacci)
8. [Teste 8 - Quicksort](#teste-8---quicksort)

---

## Teste 1 - Servidor/Calculadora

### Objetivo
Demonstrar comunicação entre processos usando canais (`c_channel`) do MiniPar. O teste implementa uma calculadora simples onde um processo envia operações e recebe resultados via canal.

### Funcionamento
1. O programa declara um canal chamado `calculadora` com três participantes: `calculadora`, `computador_1`, `computador_2`
2. O programa principal (`SEQ`) lê a operação e dois valores
3. Envia os dados através do canal usando `calculadora.send()`
4. Recebe o resultado calculado usando `calculadora.receive()`
5. Exibe o resultado

### Transformação do PDF para MiniPar

**Características do PDF:**
- Demonstração de canais de comunicação entre processos
- Envio e recebimento de dados via canais

**Adaptações para MiniPar:**
- **Sintaxe de canais**: Usado `c_channel nome participante1 participante2 participante3` (sintaxe específica do MiniPar)
- **Bloco SEQ**: Todo o código principal está dentro de um bloco `SEQ:` (sequencial)
- **Operações de I/O**: `escreva()` e `leia()` usados diretamente, sem necessidade de bibliotecas externas
- **Tipos explícitos**: Todas as variáveis precisam ser declaradas com tipo (`string`, `real`)

### Código MiniPar vs PDF

**Principais diferenças:**
- No PDF, o exemplo pode ter usado sintaxe diferente para canais; no MiniPar usamos a sintaxe `c_channel`
- O bloco `SEQ:` é obrigatório para código sequencial no MiniPar
- As declarações de variáveis são mais explícitas no MiniPar

---

## Teste 2 - Threads/Paralelismo

### Objetivo
Demonstrar programação paralela usando blocos `PAR` (paralelos) do MiniPar. Dois processos executam simultaneamente: um calcula o fatorial de 5 e outro calcula a série de Fibonacci com 5 termos.

### Funcionamento
1. **Thread 1 (Primeiro bloco PAR)**: Calcula o fatorial de 5
   - Inicializa `numero = 5`, `fatorial = 1`, `i = 1`
   - Loop `enquanto` multiplica `fatorial` por `i` até `i <= numero`
   - Exibe o resultado a cada iteração

2. **Thread 2 (Segundo bloco PAR)**: Calcula a série de Fibonacci
   - Inicializa `n = 5`, `a = 0`, `b = 1`
   - Loop `enquanto` gera os primeiros `n` termos da série
   - Cada iteração calcula o próximo termo como `a + b`

### Transformação do PDF para MiniPar

**Características do PDF:**
- Demonstração de execução paralela
- Múltiplos processos executando simultaneamente

**Adaptações para MiniPar:**
- **Blocos PAR**: Cada thread é um bloco `PAR:` separado (sintaxe específica do MiniPar)
- **Loops enquanto**: Convertidos para `enquanto condição faca: ... fim_enquanto`
- **Variáveis locais**: Cada bloco `PAR` tem suas próprias variáveis declaradas dentro dele
- **Comentários**: Usados `#` para comentários (compatível com MiniPar)

### Código MiniPar vs PDF

**Principais diferenças:**
- No PDF, a sintaxe para paralelismo pode diferir; no MiniPar usamos blocos `PAR:` explícitos
- Cada bloco `PAR` é independente e pode ter suas próprias variáveis
- Os loops foram convertidos para a sintaxe `enquanto ... faca` do MiniPar

---

## Teste 3 - Neurônio

### Objetivo
Implementar um neurônio artificial simples com aprendizado usando a regra de Hebb. O neurônio aprende a produzir uma saída desejada através de ajustes iterativos dos pesos.

### Funcionamento
1. Define uma função `activation()` que implementa a função degrau (threshold)
   - Se a soma for >= 0, retorna 1
   - Caso contrário, retorna 0

2. Loop de treinamento:
   - Calcula a soma ponderada: `sum_val = (input_val * input_weight) + (bias * bias_weight)`
   - Aplica a função de ativação
   - Calcula o erro: `error = output_desire - output`
   - Ajusta os pesos usando a regra de aprendizado: `weight = weight + (learning_rate * input * error)`
   - Continua até o erro ser 0 ou atingir 1000 iterações

### Transformação do PDF para MiniPar

**Características do PDF:**
- Função de ativação definida pelo usuário
- Loop de treinamento iterativo
- Ajuste de pesos com taxa de aprendizado

**Adaptações para MiniPar:**
- **Definição de função**: Sintaxe `def nome(parâmetro : tipo) : tipo_retorno:` (sintaxe específica do MiniPar)
- **Estruturas condicionais aninhadas**: Usadas para implementar a função de ativação e controle de loop
- **Variável de controle**: `continue_training` como flag para controlar o loop (já que MiniPar não tem `break`)
- **Comparação de reais**: Uso de `==` para comparar valores reais (requer cuidado na implementação)

### Código MiniPar vs PDF

**Principais diferenças:**
- A função `activation()` foi definida usando a sintaxe de funções do MiniPar
- O loop de treinamento usa `enquanto continue_training == 1 faca:` com uma flag de controle
- Não há operador de incremento (`++`), então usamos `iteration = iteration + 1`
- A estrutura condicional `se ... entao: ... senao:` substitui `if/else` do código base

---

## Teste 4 - XOR

### Objetivo
Implementar uma rede neural completa (multilayer perceptron) para resolver o problema XOR usando arrays bidimensionais, funções de ativação sigmoid e backpropagation.

### Funcionamento
1. **Inicialização**:
   - Array 2D `entradas[4][2]` com as 4 combinações possíveis de XOR: (0,0), (0,1), (1,0), (1,1)
   - Array `saidas_desejadas[4]` com as saídas esperadas: 0, 1, 1, 0
   - Arrays de pesos para camada oculta (`pesos_oculta[3][2]`) e saída (`pesos_saida[3]`)
   - Arrays de bias para ambas as camadas

2. **Treinamento (20000 épocas)**:
   - **Forward Propagation**:
     - Calcula saída da camada oculta usando sigmoid aproximada
     - Calcula saída final usando sigmoid aproximada
   - **Backpropagation**:
     - Calcula deltas (erro * derivada)
     - Atualiza pesos usando taxa de aprendizado

3. **Execução Final**:
   - Testa todas as entradas com os pesos treinados
   - Exibe resultados

### Transformação do PDF para MiniPar

**Características do PDF:**
- Arrays bidimensionais (`entradas[4][2]`)
- Função sigmoid (`1 / (1 + e^(-x))`)
- Backpropagation completo
- Loops aninhados múltiplos

**Adaptações para MiniPar:**
- **Arrays 2D**: Sintaxe `declare nome : tipo[linhas][colunas]`
- **Aproximação de Sigmoid**: Como MiniPar não tem função `exp()`, usamos série de Taylor:
  ```
  e^(-x) ≈ 1 + x + x²/2 + x³/6 + x⁴/24
  sigmoid(x) = 1 / (1 + e^(-x))
  ```
- **Loops aninhados**: Três níveis de `enquanto` (épocas, padrões, neurônios)
- **Limites para overflow**: Verificação `se temp > 10.0` ou `temp < -10.0` para evitar overflow na aproximação
- **Multiplicação manual**: Cálculos como `x²`, `x³`, `x⁴` feitos passo a passo

### Código MiniPar vs PDF

**Principais diferenças:**
- **Função exponencial**: No PDF pode usar `exp()`, no MiniPar precisamos calcular manualmente
- **Array indexing**: Sintaxe explícita `array[i][j]` em todas as operações
- **Estrutura do código**: Todo o código de treinamento está explicitamente escrito (sem bibliotecas de ML)
- **Aproximação de sigmoid**: Implementação manual usando série de Taylor com limitações para evitar overflow

---

## Teste 5 - Rede Neural

### Objetivo
Implementar uma rede neural de recomendação de produtos com duas camadas (oculta com ReLU e saída com sigmoid) usando arrays de strings para armazenar nomes de produtos.

### Funcionamento
1. **Inicialização de Dados**:
   - Array de strings `produtos[16]` com nomes de produtos
   - Array `historico[16]` indicando quais produtos foram comprados (1) ou não (0)
   - Codifica o histórico como entrada da rede (`entrada[16]`)

2. **Inicialização de Pesos**:
   - Matriz de pesos `W1[160]` (16x10) para camada oculta (armazenada como array 1D)
   - Array de bias `b1[10]` para camada oculta
   - Matriz de pesos `W2[160]` (10x16) para camada de saída
   - Array de bias `b2[16]` para camada de saída

3. **Forward Propagation**:
   - **Camada Oculta**: `Z1 = entrada * W1 + b1`, depois aplica ReLU: `A1 = max(0, Z1)`
   - **Camada de Saída**: `Z2 = A1 * W2 + b2`, depois aplica sigmoid aproximada: `A2 = 1 / (1 + e^(-Z2))`

4. **Geração de Recomendações**:
   - Produtos com `A2[i] >= 0.5` e `historico[i] == 0` são recomendados
   - Usa condições aninhadas já que MiniPar não tem operador lógico `e`

### Transformação do PDF para MiniPar

**Características do PDF:**
- Arrays de strings para nomes de produtos
- Rede neural com duas camadas
- Função de ativação ReLU na camada oculta
- Função sigmoid na camada de saída

**Adaptações para MiniPar:**
- **Arrays de Strings**: Sintaxe `declare nome : string[tamanho]`
- **Matrizes como Arrays 1D**: Como MiniPar não suporta arrays multidimensionais além de 2D, matrizes grandes são armazenadas como arrays 1D com cálculo manual de índice:
  - `W1[i * 10 + j]` acessa elemento (i, j) de uma matriz 16x10
- **ReLU Manual**: Implementado como `se Z1[i] > 0.0 entao A1[i] = Z1[i] senao A1[i] = 0.0`
- **Sigmoid Aproximada**: Série de Taylor até x⁶ para melhor precisão:
  ```
  e^x ≈ 1 + x + x²/2 + x³/6 + x⁴/24 + x⁵/120 + x⁶/720
  ```
- **Operador Lógico**: Como não há `e`, usamos `se A2[i] >= 0.5 entao: se historico[i] == 0 entao: ...`

### Código MiniPar vs PDF

**Principais diferenças:**
- **Indexação de matrizes**: Cálculo manual de índice para arrays 1D que representam matrizes
- **Forward propagation explícito**: Todo o cálculo de matrizes feito com loops aninhados
- **ReLU implementado manualmente**: Não há função `max()`, então usamos condicional
- **Sigmoid com aproximação melhor**: Mais termos na série de Taylor (até x⁶) comparado ao teste 4

---

## Teste 6 - Fatorial

### Objetivo
Calcular o fatorial de um número usando um loop `enquanto`. O teste demonstra loops simples com condição de continuação.

### Funcionamento
1. Inicializa `numero = 5`, `fatorial = 1`, `i = 1`
2. Loop `enquanto i <= numero faca:`:
   - Multiplica `fatorial` por `i`
   - Incrementa `i`
   - Continua até `i > numero`
3. Exibe o resultado: "O fatorial de 5 é 120"

### Transformação do PDF para MiniPar

**Características do PDF:**
- Loop simples com cálculo iterativo
- Uso de variável de controle (`i`)

**Adaptações para MiniPar:**
- **Sintaxe de loop**: `enquanto condição faca: ... fim_enquanto`
- **Operador de comparação**: `<=` usado diretamente (sintaxe do MiniPar)
- **Incremento manual**: `i = i + 1` (não há `i++`)
- **Bloco SEQ**: Código dentro de `SEQ:` para execução sequencial

### Código MiniPar vs PDF

**Principais diferenças:**
- Sintaxe de loop diferente (`enquanto` vs `while`)
- Palavras-chave em português
- Operadores de incremento explícitos

---

## Teste 7 - Fibonacci

### Objetivo
Gerar os primeiros N termos da série de Fibonacci usando um loop `enquanto`. O teste demonstra manipulação de múltiplas variáveis em um loop.

### Funcionamento
1. Inicializa `n = 5`, `a = 0`, `b = 1`, `i = 0`
2. Loop `enquanto i < n faca:`:
   - Exibe o valor atual `a`
   - Calcula próximo termo: `proximo = a + b`
   - Atualiza valores: `a = b`, `b = proximo`
   - Incrementa contador: `i = i + 1`
3. Exibe os primeiros 5 termos: 0, 1, 1, 2, 3

### Transformação do PDF para MiniPar

**Características do PDF:**
- Sequência matemática clássica
- Manipulação de duas variáveis simultaneamente (`a` e `b`)

**Adaptações para MiniPar:**
- **Atribuições múltiplas**: Feitas sequencialmente (não há tuple unpacking)
- **Variável temporária**: `proximo` usada para armazenar `a + b` antes de atualizar `a` e `b`
- **Sintaxe de loop**: Igual ao teste 6 (`enquanto ... faca`)

### Código MiniPar vs PDF

**Principais diferenças:**
- Atribuições feitas uma por vez (em linguagens modernas poderia ser `a, b = b, a+b`)
- Variável explícita para armazenar valor intermediário

---

## Teste 8 - Quicksort

### Objetivo
Implementar o algoritmo de ordenação Quicksort usando uma pilha simulada para evitar recursão (já que MiniPar pode não suportar recursão nativa).

### Funcionamento
1. **Inicialização**: Array `arr[5]` com valores [33, 12, 98, 5, 61]
2. **Pilha Simulada**: Array `stack[20]` e ponteiro `sp` (stack pointer)
3. **Algoritmo Iterativo**:
   - Empilha intervalo inicial: `[0, 4]`
   - Enquanto pilha não estiver vazia (`sp >= 2`):
     - Desempilha intervalo `[start, end]`
     - Particiona o array usando último elemento como pivô
     - Empilha subarrays esquerdo e direito (se tiverem 2+ elementos)
   - Repete até todos os intervalos serem processados

### Transformação do PDF para MiniPar

**Características do PDF:**
- Algoritmo de ordenação clássico
- Implementação recursiva típica

**Adaptações para MiniPar:**
- **Pilha Simulada**: Como MiniPar pode não ter recursão nativa, usamos uma pilha explícita
  - `stack[sp]` armazena os limites dos intervalos (pares de índices)
  - `sp` (stack pointer) controla o topo da pilha
- **LIFO (Last In First Out)**: A pilha é implementada como array com índice crescente
- **Particionamento**: Implementado conforme algoritmo clássico de Hoare:
  1. Escolhe pivô (último elemento)
  2. Reorganiza elementos menores/maiores que o pivô
  3. Coloca pivô na posição final correta
- **Condições para empilhar**: 
  - Subarray direito: `se i + 1 < end_val entao` (pelo menos 2 elementos)
  - Subarray esquerdo: `se start < i - 1 entao` (pelo menos 2 elementos)

### Código MiniPar vs PDF

**Principais diferenças:**
- **Recursão → Iteração**: No PDF pode ter usado recursão, no MiniPar usamos pilha simulada
- **Controle de pilha manual**: Gerenciamento explícito do stack pointer
- **Empilhamento/Desempilhamento**: Operações LIFO feitas manualmente:
  - **Empilhar**: `stack[sp] = valor; sp = sp + 1`
  - **Desempilhar**: `sp = sp - 1; valor = stack[sp]`
- **Estrutura de dados**: Pilha implementada como array comum (não há tipo `stack` nativo)

### Detalhes da Implementação

**Por que LIFO funciona:**
- Empilhamos o subarray direito primeiro, depois o esquerdo
- Como é LIFO, processamos o esquerdo primeiro (último a entrar, primeiro a sair)
- Isso mantém a ordem correta de processamento (esquerda antes de direita)

**Cálculo de Índices:**
- `i` é a posição final do pivô após particionamento
- `[start, i-1]` são elementos menores que o pivô
- `[i+1, end]` são elementos maiores que o pivô

---

## 📊 Resumo das Transformações

### Padrões Comuns de Adaptação

1. **Loops**: `while` → `enquanto condição faca: ... fim_enquanto`
2. **Condicionais**: `if/else` → `se ... entao: ... senao:`
3. **Arrays**: Declarações explícitas `declare nome : tipo[tamanho]`
4. **Funções Matemáticas**: Implementação manual (ex: `exp()` via série de Taylor)
5. **Recursão**: Substituída por iteração com pilha simulada quando necessário
6. **Operadores**: Incremento explícito (`i = i + 1` ao invés de `i++`)
7. **Tipos**: Declarações explícitas obrigatórias
8. **Paralelismo**: Blocos `PAR:` para execução paralela
9. **Comunicação**: Canais `c_channel` para IPC

### Limitações da Linguagem e Soluções

| Limitação | Solução Implementada |
|-----------|---------------------|
| Sem `exp()` | Série de Taylor para aproximar `e^x` |
| Sem recursão | Pilha simulada (teste 8) |
| Sem operador `e` | Condicionais aninhadas |
| Arrays limitados | Matrizes como arrays 1D com cálculo de índice |
| Sem `max()` | Condicionais (`se x > 0 entao x senao 0`) |
| Sem incremento `++` | `i = i + 1` |

---

## ✅ Conclusão

Todos os testes foram transformados do código base do PDF para MiniPar mantendo a lógica funcional equivalente. As principais adaptações envolvem:

- **Sintaxe específica do MiniPar** (palavras-chave em português)
- **Implementação manual de funções** que não existem nativamente
- **Estruturas de dados adaptadas** para as limitações da linguagem
- **Controle de fluxo explícito** (flags e loops ao invés de recursão)

Todos os testes compilam com sucesso e são compatíveis com o CPUlator, gerando código assembly ARMv7 funcional.

