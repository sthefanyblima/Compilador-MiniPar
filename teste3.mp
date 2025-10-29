programa-miniPar

SEQ:
    declare input_val : real
    declare output_desire : real
    declare input_weight : real
    declare learning_rate : real
    declare error : real
    declare iteration : inteiro
    declare bias : real
    declare bias_weight : real
    declare sum_val : real
    declare output : real
    
    def activation(sum : real) : inteiro:
        se sum >= 0 entao:
            return 1
        senao:
            return 0
    
    input_val = 1.0
    output_desire = 0.0
    input_weight = 0.5
    learning_rate = 0.01
    error = 1000.0
    iteration = 0
    bias = 1.0
    bias_weight = 0.5
    
    escreva("Entrada: ", input_val, " Desejado: ", output_desire)
    
    enquanto error != 0 faca:
        iteration = iteration + 1
        escreva("### Iteração: ", iteration)
        escreva("Peso: ", input_weight)
        
        sum_val = (input_val * input_weight) + (bias * bias_weight)
        output = activation(sum_val)
        escreva("Saída: ", output)
        
        error = output_desire - output
        escreva("Erro: ", error)
        
        se error != 0 entao:
            input_weight = input_weight + (learning_rate * input_val * error)
            escreva("Peso do bias: ", bias_weight)
            bias_weight = bias_weight + (learning_rate * bias * error)
    
    escreva("Parabéns!!! A Rede de um Neurônio Aprendeu")
    escreva("Valor desejado: ", output_desire)