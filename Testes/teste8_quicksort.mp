programa-miniPar

SEQ:
    declare arr : inteiro[5]
    declare stack : inteiro[20]
    declare sp : inteiro
    declare start : inteiro
    declare end_val : inteiro
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
    
    escreva("Array original: ", arr[0], ", ", arr[1], ", ", arr[2], ", ", arr[3], ", ", arr[4])
    
    # Inicializar pilha: empilhar primeiro intervalo (0, 4)
    sp = 0
    stack[sp] = 0
    sp = sp + 1
    stack[sp] = 4
    sp = sp + 1
    
    # Loop principal: enquanto a pilha não estiver vazia
    enquanto sp >= 2 faca:
        # Desempilhar: remover último par (LIFO - Last In First Out)
        sp = sp - 1
        end_val = stack[sp]
        sp = sp - 1
        start = stack[sp]
        
        # Particionar apenas se start < end_val
        se start < end_val entao:
            # Particionamento: usar último elemento como pivô
            pivot = arr[end_val]
            i = start - 1
            
            # Loop interno: particionar elementos do start até end_val-1
            j = start
            enquanto j < end_val faca:
                se arr[j] <= pivot entao:
                    i = i + 1
                    temp = arr[i]
                    arr[i] = arr[j]
                    arr[j] = temp
                j = j + 1
            fim_enquanto
            
            # Colocar pivô na posição final correta
            i = i + 1
            temp = arr[i]
            arr[i] = arr[end_val]
            arr[end_val] = temp
            
            # pivot_index agora é i
            
            # Empilhar subarrays para processar
            # LIFO: empilhar direita primeiro, depois esquerda (processa esquerda primeiro)
            
            # Subarray da direita (i+1, end_val) - só se houver 2+ elementos
            se i + 1 < end_val entao:
                stack[sp] = i + 1
                sp = sp + 1
                stack[sp] = end_val
                sp = sp + 1
            
            # Subarray da esquerda (start, i-1) - só se houver 2+ elementos
            # IMPORTANTE: start < i - 1 garante que há pelo menos 2 elementos no subarray
            # Se start = 0 e i = 1, então start < i - 1 = 0 < 0 = False (correto, não há intervalo)
            # Se start = 0 e i = 2, então start < i - 1 = 0 < 1 = True (correto, há intervalo [0, 1])
            se start < i - 1 entao:
                stack[sp] = start
                sp = sp + 1
                stack[sp] = i - 1
                sp = sp + 1
    fim_enquanto
    
    escreva("Array ordenado: ", arr[0], ", ", arr[1], ", ", arr[2], ", ", arr[3], ", ", arr[4])
