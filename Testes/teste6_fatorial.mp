programa-miniPar

SEQ:
    declare numero : inteiro
    declare fatorial : inteiro
    declare i : inteiro
    
    numero = 5
    fatorial = 1
    i = 1
    
    enquanto i <= numero faca:
        fatorial = fatorial * i
        i = i + 1
    fim_enquanto
    
    escreva("O fatorial de ", numero, " é ", fatorial)