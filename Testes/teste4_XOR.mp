programa-miniPar

SEQ:
    # Declarações de arrays para armazenar pesos, bias e dados
    declare entradas : real[4][2]
    declare saidas_desejadas : real[4]
    declare pesos_oculta : real[3][2]
    declare bias_oculta : real[3]
    declare pesos_saida : real[3]
    declare bias_saida : real
    declare saidas_ocultas : real[3]
    declare saida_final : real
    declare taxa_aprendizado : real
    declare epocas : inteiro
    declare i : inteiro
    declare j : inteiro
    declare k : inteiro
    declare soma : real
    declare erro : real
    declare delta_saida : real
    declare delta_oculto : real
    declare x_neg : real
    declare exp_approx : real
    declare temp : real
    declare x2 : real
    declare x3 : real
    declare x4 : real
    declare x5 : real
    declare x6 : real
    
    # Inicializar dados XOR
    entradas[0][0] = 0.0
    entradas[0][1] = 0.0
    entradas[1][0] = 0.0
    entradas[1][1] = 1.0
    entradas[2][0] = 1.0
    entradas[2][1] = 0.0
    entradas[3][0] = 1.0
    entradas[3][1] = 1.0
    
    saidas_desejadas[0] = 0.0
    saidas_desejadas[1] = 1.0
    saidas_desejadas[2] = 1.0
    saidas_desejadas[3] = 0.0
    
    # Inicializar pesos aleatórios (valores pré-definidos para reprodutibilidade)
    pesos_oculta[0][0] = 0.5
    pesos_oculta[0][1] = 0.3
    bias_oculta[0] = 0.2
    pesos_oculta[1][0] = 0.4
    pesos_oculta[1][1] = 0.6
    bias_oculta[1] = 0.1
    pesos_oculta[2][0] = 0.7
    pesos_oculta[2][1] = 0.2
    bias_oculta[2] = 0.4
    pesos_saida[0] = 0.3
    pesos_saida[1] = 0.5
    pesos_saida[2] = 0.4
    bias_saida = 0.2
    taxa_aprendizado = 0.2
    epocas = 20000
    
    # Treinamento simplificado - ESTRUTURA REORGANIZADA para parser
    i = 0
    enquanto i < epocas faca:
        j = 0
        enquanto j < 4 faca:
            k = 0
            enquanto k < 3 faca:
                soma = (entradas[j][0] * pesos_oculta[k][0]) + (entradas[j][1] * pesos_oculta[k][1]) + bias_oculta[k]
                temp = soma
                se temp > 10.0 entao:
                    saidas_ocultas[k] = 0.9999
                senao:
                    se temp < -10.0 entao:
                        saidas_ocultas[k] = 0.0001
                    senao:
                        x_neg = 0.0 - temp
                        x2 = x_neg * x_neg
                        x3 = x2 * x_neg
                        x4 = x3 * x_neg
                        exp_approx = 1.0 + x_neg + x2 / 2.0 + x3 / 6.0 + x4 / 24.0
                        se exp_approx <= 0.0 entao:
                            saidas_ocultas[k] = 0.9999
                        senao:
                            se exp_approx > 0.0001 entao:
                                saidas_ocultas[k] = 1.0 / (1.0 + exp_approx)
                            senao:
                                saidas_ocultas[k] = 0.9999
                k = k + 1
            fim_enquanto
            soma = (saidas_ocultas[0] * pesos_saida[0]) + (saidas_ocultas[1] * pesos_saida[1]) + (saidas_ocultas[2] * pesos_saida[2]) + bias_saida
            temp = soma
            se temp > 10.0 entao:
                saida_final = 0.9999
            senao:
                se temp < -10.0 entao:
                    saida_final = 0.0001
                senao:
                    x_neg = 0.0 - temp
                    x2 = x_neg * x_neg
                    x3 = x2 * x_neg
                    x4 = x3 * x_neg
                    exp_approx = 1.0 + x_neg + x2 / 2.0 + x3 / 6.0 + x4 / 24.0
                    se exp_approx <= 0.0 entao:
                        saida_final = 0.9999
                    senao:
                        se exp_approx > 0.0001 entao:
                            saida_final = 1.0 / (1.0 + exp_approx)
                        senao:
                            saida_final = 0.9999
            erro = saidas_desejadas[j] - saida_final
            delta_saida = erro * (saida_final * (1.0 - saida_final))
            pesos_saida[0] = pesos_saida[0] + (saidas_ocultas[0] * delta_saida * taxa_aprendizado)
            pesos_saida[1] = pesos_saida[1] + (saidas_ocultas[1] * delta_saida * taxa_aprendizado)
            pesos_saida[2] = pesos_saida[2] + (saidas_ocultas[2] * delta_saida * taxa_aprendizado)
            bias_saida = bias_saida + (delta_saida * taxa_aprendizado)
            k = 0
            enquanto k < 3 faca:
                delta_oculto = delta_saida * pesos_saida[k] * (saidas_ocultas[k] * (1.0 - saidas_ocultas[k]))
                pesos_oculta[k][0] = pesos_oculta[k][0] + (entradas[j][0] * delta_oculto * taxa_aprendizado)
                pesos_oculta[k][1] = pesos_oculta[k][1] + (entradas[j][1] * delta_oculto * taxa_aprendizado)
                bias_oculta[k] = bias_oculta[k] + (delta_oculto * taxa_aprendizado)
                k = k + 1
            fim_enquanto
            j = j + 1
        fim_enquanto
        i = i + 1
    fim_enquanto
    
    escreva("Execução:")
    j = 0
    enquanto j < 4 faca:
        k = 0
        enquanto k < 3 faca:
            soma = (entradas[j][0] * pesos_oculta[k][0]) + (entradas[j][1] * pesos_oculta[k][1]) + bias_oculta[k]
            temp = soma
            se temp > 10.0 entao:
                saidas_ocultas[k] = 0.9999
            senao:
                se temp < -10.0 entao:
                    saidas_ocultas[k] = 0.0001
                senao:
                    x_neg = 0.0 - temp
                    x2 = x_neg * x_neg
                    x3 = x2 * x_neg
                    x4 = x3 * x_neg
                    exp_approx = 1.0 + x_neg + x2 / 2.0 + x3 / 6.0 + x4 / 24.0
                    se exp_approx <= 0.0 entao:
                        saidas_ocultas[k] = 0.9999
                    senao:
                        se exp_approx > 0.0001 entao:
                            saidas_ocultas[k] = 1.0 / (1.0 + exp_approx)
                        senao:
                            saidas_ocultas[k] = 0.9999
            k = k + 1
        fim_enquanto
        soma = (saidas_ocultas[0] * pesos_saida[0]) + (saidas_ocultas[1] * pesos_saida[1]) + (saidas_ocultas[2] * pesos_saida[2]) + bias_saida
        temp = soma
        se temp > 10.0 entao:
            saida_final = 0.9999
        senao:
            se temp < -10.0 entao:
                saida_final = 0.0001
            senao:
                x_neg = 0.0 - temp
                x2 = x_neg * x_neg
                x3 = x2 * x_neg
                x4 = x3 * x_neg
                exp_approx = 1.0 + x_neg + x2 / 2.0 + x3 / 6.0 + x4 / 24.0
                se exp_approx <= 0.0 entao:
                    saida_final = 0.9999
                senao:
                    se exp_approx > 0.0001 entao:
                        saida_final = 1.0 / (1.0 + exp_approx)
                    senao:
                        saida_final = 0.9999
        escreva("Input: [", entradas[j][0], ", ", entradas[j][1], "], Predicted Output: ", saida_final)
        j = j + 1
    fim_enquanto
