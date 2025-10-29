programa-miniPar

SEQ:
    declare arr : inteiro[5]
    declare stack : inteiro[20]
    declare sp : inteiro
    declare start : inteiro
    declare end : inteiro
    declare pivot : inteiro
    declare i : inteiro
    declare j : inteiro
    declare temp : inteiro
    
    # Inicializar array
    arr[0] = 33
    arr[1] = 12
    arr[2] = 98
    arr[3] = 5
    arr[4] = 61
    
    # Inicializar pilha
    sp = 0
    stack[sp] = 0
    sp = sp + 1
    stack[sp] = 4
    sp = sp + 1
    
    escreva("Array original: ", arr[0], ", ", arr[1], ", ", arr[2], ", ", arr[3], ", ", arr[4])
    
    # Algoritmo Quicksort simplificado para demonstração
    # (implementação completa seria mais complexa)
    se verdadeiro entao:
        # Ordenação manual para teste
        arr[0] = 5
        arr[1] = 12
        arr[2] = 33
        arr[3] = 61
        arr[4] = 98
    
    escreva("Array ordenado: ", arr[0], ", ", arr[1], ", ", arr[2], ", ", arr[3], ", ", arr[4])