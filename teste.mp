{
  Este programa calcula o fatorial de um número lido.
  Usa laço 'enquanto' e condicional 'se'.
}
programa
    declare inteiro: n
    declare inteiro: i
    declare inteiro: fat

    leia(n)

    se (n < 0) entao
        escreva(-1) { Sinaliza erro para fatorial de negativo }
    senao
        fat = 1
        i = 1
        enquanto (i <= n) faca
            fat = fat * i
            i = i + 1
        fim_enquanto
        escreva(fat)
    fim_se

fim_programa
