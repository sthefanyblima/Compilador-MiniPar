programa
    declare inteiro: opcao
    declare inteiro: n
    declare inteiro: resultado
    declare inteiro: fat
    declare inteiro: i
    declare inteiro: total_testes
    declare inteiro: testes_aprovados

    escreva("TESTADOR DE FATORIAL")
    escreva("\n")
    escreva("1 - Testes automaticos")
    escreva("\n")
    escreva("2 - Teste manual")
    escreva("\n")
    escreva("3 - Sair")
    escreva("\n")
    escreva("Escolha: ")
    leia(opcao)

    se (opcao == 1) entao
        total_testes = 7
        testes_aprovados = 0

        { Teste 1: Numero 5 }
        n = 5
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 1: ")
        escreva(resultado)
        se (resultado == 120) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 2: Numero 0 }
        n = 0
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 2: ")
        escreva(resultado)
        se (resultado == 1) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 3: Numero -3 }
        n = -3
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 3: ")
        escreva(resultado)
        se (resultado == -1) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 4: Numero 1 }
        n = 1
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 4: ")
        escreva(resultado)
        se (resultado == 1) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 5: Numero 6 }
        n = 6
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 5: ")
        escreva(resultado)
        se (resultado == 720) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 6: Numero 3 }
        n = 3
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 6: ")
        escreva(resultado)
        se (resultado == 6) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        { Teste 7: Numero 12 }
        n = 12
        se (n < 0) entao
            resultado = -1
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            resultado = fat
        fim_se
        escreva("Teste 7: ")
        escreva(resultado)
        se (resultado == 479001600) entao
            escreva(" APROVADO")
            testes_aprovados = testes_aprovados + 1
        senao
            escreva(" REPROVADO")
        fim_se
        escreva("\n")

        escreva("Total: ")
        escreva(testes_aprovados)
        escreva("/")
        escreva(total_testes)
        escreva(" aprovados")
        escreva("\n")

    senao se (opcao == 2) entao
        escreva("Digite numero: ")
        leia(n)

        se (n < 0) entao
            escreva(-1)
        senao
            fat = 1
            i = 1
            enquanto (i <= n) faca
                fat = fat * i
                i = i + 1
            fim_enquanto
            escreva(fat)
        fim_se
        escreva("\n")

    senao
        escreva("Fim")
        escreva("\n")
    fim_se

fim_programa