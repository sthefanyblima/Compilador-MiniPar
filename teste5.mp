programa-miniPar

SEQ:
    declare produtos : string[16]
    declare historico : inteiro[16]
    declare recomendacoes : string[16]
    declare count : inteiro
    
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
    historico[0] = 1  # Smartphone
    historico[4] = 0  # Camisa (não comprou)
    historico[5] = 1  # Jeans
    historico[9] = 1  # Micro-ondas
    historico[12] = 1 # Ficção
    
    escreva("Produtos recomendados para você:")
    count = 0
    
    i = 0
    enquanto i < 16 faca:
        se historico[i] == 0 entao:
            recomendacoes[count] = produtos[i]
            count = count + 1
            escreva(produtos[i])
        i = i + 1