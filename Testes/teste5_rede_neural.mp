programa-miniPar

SEQ:
    declare produtos : string[16]
    declare historico : inteiro[16]
    
    # Arrays para a rede neural
    declare entrada : real[16]
    declare W1 : real[160]  # 16x10 pesos camada oculta
    declare b1 : real[10]   # bias camada oculta
    declare Z1 : real[10]   # saída linear camada oculta
    declare A1 : real[10]   # saída após ReLU
    declare W2 : real[160]  # 10x16 pesos camada saída
    declare b2 : real[16]   # bias camada saída
    declare Z2 : real[16]   # saída linear camada saída
    declare A2 : real[16]   # saída final (sigmoid)
    
    # Variáveis auxiliares
    declare i : inteiro
    declare j : inteiro
    declare soma : real
    declare exp_term : real
    declare sigmoid_val : real
    declare temp : real
    
    # Inicializar produtos
    produtos[0] = "Smartphone"
    produtos[1] = "Laptop"
    produtos[2] = "Tablet"
    produtos[3] = "Fones de ouvido"
    produtos[4] = "Camisa"
    produtos[5] = "Jeans"
    produtos[6] = "Jaqueta"
    produtos[7] = "Sapatos"
    produtos[8] = "Geladeira"
    produtos[9] = "Micro-ondas"
    produtos[10] = "Máquina de lavar"
    produtos[11] = "Ar condicionado"
    produtos[12] = "Ficção"
    produtos[13] = "Não-ficção"
    produtos[14] = "Ficção científica"
    produtos[15] = "Fantasia"
    
    # Histórico de compras (1 = comprou, 0 = não comprou)
    historico[0] = 1   # Smartphone (comprou)
    historico[1] = 0   # Laptop (não comprou)
    historico[2] = 0   # Tablet (não comprou)
    historico[3] = 0   # Fones de ouvido (não comprou)
    historico[4] = 0   # Camisa (não comprou)
    historico[5] = 1   # Jeans (comprou)
    historico[6] = 0   # Jaqueta (não comprou)
    historico[7] = 0   # Sapatos (não comprou)
    historico[8] = 0   # Geladeira (não comprou)
    historico[9] = 1   # Micro-ondas (comprou)
    historico[10] = 0  # Máquina de lavar (não comprou)
    historico[11] = 0  # Ar condicionado (não comprou)
    historico[12] = 1  # Ficção (comprou)
    historico[13] = 0  # Não-ficção (não comprou)
    historico[14] = 0  # Ficção científica (não comprou)
    historico[15] = 0  # Fantasia (não comprou)
    
    # Codificar histórico (entrada da rede)
    i = 0
    enquanto i < 16 faca:
        entrada[i] = historico[i]
        i = i + 1
    fim_enquanto
    
    # Inicializar pesos W1 (16x10, todos 0.5)
    i = 0
    enquanto i < 16 faca:
        j = 0
        enquanto j < 10 faca:
            W1[i * 10 + j] = 0.5
            j = j + 1
        fim_enquanto
        i = i + 1
    fim_enquanto
    
    # Inicializar bias b1 (10 elementos, todos 0.5)
    i = 0
    enquanto i < 10 faca:
        b1[i] = 0.5
        i = i + 1
    fim_enquanto
    
    # Inicializar pesos W2 (10x16, todos 0.5)
    i = 0
    enquanto i < 10 faca:
        j = 0
        enquanto j < 16 faca:
            W2[i * 16 + j] = 0.5
            j = j + 1
        fim_enquanto
        i = i + 1
    fim_enquanto
    
    # Inicializar bias b2 (16 elementos, todos 0.5)
    i = 0
    enquanto i < 16 faca:
        b2[i] = 0.5
        i = i + 1
    fim_enquanto
    
    # Forward Propagation - Camada Oculta
    # Z1 = X * W1 + b1
    j = 0
    enquanto j < 10 faca:
        soma = 0.0
        i = 0
        enquanto i < 16 faca:
            soma = soma + entrada[i] * W1[i * 10 + j]
            i = i + 1
        fim_enquanto
        Z1[j] = soma + b1[j]
        j = j + 1
    fim_enquanto
    
    # Aplicar ReLU: A1 = max(0, Z1)
    i = 0
    enquanto i < 10 faca:
        se Z1[i] > 0.0 entao:
            A1[i] = Z1[i]
        senao:
            A1[i] = 0.0
        i = i + 1
    fim_enquanto
    
    # Forward Propagation - Camada de Saída
    # Z2 = A1 * W2 + b2
    j = 0
    enquanto j < 16 faca:
        soma = 0.0
        i = 0
        enquanto i < 10 faca:
            soma = soma + A1[i] * W2[i * 16 + j]
            i = i + 1
        fim_enquanto
        Z2[j] = soma + b2[j]
        j = j + 1
    fim_enquanto
    
    # Aplicar Sigmoid: A2 = 1 / (1 + e^(-Z2))
    # Como não temos exp(), vamos usar uma aproximação similar ao teste4_XOR
    i = 0
    enquanto i < 16 faca:
        temp = -Z2[i]
        
        # Aproximação de e^x usando série de Taylor
        # Para valores muito grandes ou muito pequenos, usar limites
        se temp > 10.0 entao:
            sigmoid_val = 0.0
        senao:
            se temp < -10.0 entao:
                sigmoid_val = 1.0
            senao:
                # Calcular e^temp usando série de Taylor até x⁶
                exp_term = 1.0
                exp_term = exp_term + temp
                exp_term = exp_term + (temp * temp) / 2.0
                exp_term = exp_term + (temp * temp * temp) / 6.0
                exp_term = exp_term + (temp * temp * temp * temp) / 24.0
                exp_term = exp_term + (temp * temp * temp * temp * temp) / 120.0
                exp_term = exp_term + (temp * temp * temp * temp * temp * temp) / 720.0
                
                # Calcular sigmoid
                se exp_term <= 0.0 entao:
                    sigmoid_val = 1.0
                senao:
                    sigmoid_val = 1.0 / (1.0 + exp_term)
        
        A2[i] = sigmoid_val
        i = i + 1
    fim_enquanto
    
    # Gerar recomendações: produtos com A2[i] > 0.5 e historico[i] == 0
    # Como não temos operador 'e', usamos condições aninhadas
    escreva("Produtos recomendados para você:")
    
    i = 0
    enquanto i < 16 faca:
        se A2[i] >= 0.5 entao:
            se historico[i] == 0 entao:
                escreva(produtos[i])
        i = i + 1
    fim_enquanto
