programa-miniPar
c_channel calculadora computador_1 computador_2

SEQ:
    declare operacao : string
    declare valor1 : real
    declare valor2 : real
    declare resultado : real
    
    escreva("Calculadora - Operações: +, -, *, /")
    leia(operacao)
    leia(valor1)
    leia(valor2)
    
    calculadora.send(operacao, valor1, valor2, resultado)
    escreva("Resultado: ", resultado)