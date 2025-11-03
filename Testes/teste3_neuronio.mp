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
    declare continue_training : inteiro
    
    def activation(sum : real) : inteiro:
        se sum >= 0 entao:
            return 1
        senao:
            return 0
    
    input_val = 1.0
    output_desire = 0.0
    input_weight = 0.5
    learning_rate = 0.01
    error = 1.0
    iteration = 0
    bias = 1.0
    bias_weight = 0.5
    continue_training = 1
    
    escreva("Entrada: ", input_val, " Desejado: ", output_desire)
    
    enquanto continue_training == 1 faca:
        iteration = iteration + 1
        escreva("#### Iteração: ", iteration)
        
        sum_val = (input_val * input_weight) + (bias * bias_weight)
        output = activation(sum_val)
        error = output_desire - output
        
        escreva("Peso: ", input_weight)
        escreva("Saída: ", output)
        escreva("Erro: ", error)
        escreva("Peso do bias: ", bias_weight)
        
        se error == 0.0 entao:
            continue_training = 0
        senao:
            input_weight = input_weight + (learning_rate * input_val * error)
            bias_weight = bias_weight + (learning_rate * bias * error)
        
        # Garantir que iteration sempre muda para evitar detecção de loop estagnado
        se iteration > 1000 entao:
            continue_training = 0
    fim_enquanto
    
    escreva("Parabéns! O neurônio aprendeu.")
    escreva("Valor desejado: ", output_desire)