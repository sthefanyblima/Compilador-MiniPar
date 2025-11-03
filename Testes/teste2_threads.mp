programa-miniPar

PAR:
    # Thread 1 - Cálculo do Fatorial
    declare numero : inteiro
    declare fatorial : inteiro
    declare i : inteiro
    
    numero = 5
    fatorial = 1
    i = 1
    
    enquanto i <= numero faca:
        fatorial = fatorial * i
        escreva("Fatorial de ", numero, " é ", fatorial)
        i = i + 1
    fim_enquanto

PAR:
    # Thread 2 - Série de Fibonacci
    declare n : inteiro
    declare a : inteiro
    declare b : inteiro
    declare proximo : inteiro
    declare j : inteiro
    
    n = 5
    a = 0
    b = 1
    
    escreva("Série de Fibonacci com ", n, " termos:")
    j = 0
    enquanto j < n faca:
        escreva(a)
        proximo = a + b
        a = b
        b = proximo
        j = j + 1
    fim_enquanto