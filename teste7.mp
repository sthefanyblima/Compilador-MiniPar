programa-miniPar

SEQ:
    declare n : inteiro
    declare a : inteiro
    declare b : inteiro
    declare proximo : inteiro
    declare i : inteiro
    
    n = 5
    a = 0
    b = 1
    
    escreva("Série de Fibonacci com ", n, " termos:")
    i = 0
    
    enquanto i < n faca:
        escreva(a)
        proximo = a + b
        a = b
        b = proximo
        i = i + 1