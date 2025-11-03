#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Sintático do compilador MiniPar
Gramática refatorada para eliminar conflitos shift/reduce
"""

from sly import Parser
try:
    from .lexer import MiniParLexer
except ImportError:
    from lexer import MiniParLexer


class MiniParParser(Parser):
    tokens = MiniParLexer.tokens
    debugfile = 'parser.out'
    
    # Precedência para resolver conflitos
    # Com FIM_ENQUANTO obrigatório, o parser sabe exatamente onde termina o loop,
    # então não precisamos mais de precedência especial para ENQUANTO
    precedence = (
        ('left', 'OP_REL'),      # Operadores relacionais
        ('left', 'OP_SOMA', 'OP_SUB'),
        ('left', 'OP_MULT', 'OP_DIV'),
        ('right', 'UMINUS'),
        # Precedência para tokens de fechamento
        ('left', 'SENAO', 'FIM_ENQUANTO'),  # Tokens de fechamento têm precedência para reduzir lista_comandos
        ('left', 'SE', 'PARA'),  # Outras estruturas de controle
    )

    def __init__(self):
        self.syntax_errors = []
        self.indent_level = 0
        self.last_token = None

    def error(self, p):
        if p:
            error_message = f"Erro de Sintaxe: Token inesperado '{p.value}' (Tipo: {p.type}) na linha {p.lineno}"
            self.syntax_errors.append(error_message)
            self.last_token = p
            return None
        else:
            error_message = "Erro de Sintaxe: Fim inesperado do arquivo."
            self.syntax_errors.append(error_message)
            return None

    # Regra principal do programa
    @_('PROGRAMA lista_comandos') # type: ignore
    def programa_minipar(self, p):
        return ('programa_minipar', p.lista_comandos)

    # Blocos SEQ e PAR - usando opt_dois_pontos para reduzir conflitos
    @_('SEQ opt_dois_pontos lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_seq', p.lista_comandos)

    @_('PAR opt_dois_pontos lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_par', p.lista_comandos)
    
    # Terminal opcional para DOIS_PONTOS - ajuda a reduzir conflitos
    @_('') # type: ignore
    def opt_dois_pontos(self, p):
        pass
    
    @_('DOIS_PONTOS') # type: ignore
    def opt_dois_pontos(self, p):
        pass

    # Lista de comandos - left-recursive (padrão do SLY)
    # CORREÇÃO: Manter left-recursion mas tornar regras de comando mais específicas
    # para reduzir ambiguidade. O problema não é a recursão, mas a ambiguidade nas regras.
    @_('lista_comandos comando') # type: ignore
    def lista_comandos(self, p):
        return p.lista_comandos + [p.comando]

    @_('comando') # type: ignore
    def lista_comandos(self, p):
        return [p.comando]
    
    # Lista de comandos para loops - mesma estrutura mas com nome diferente
    # para permitir tratamento específico se necessário
    @_('lista_comandos_loop comando') # type: ignore
    def lista_comandos_loop(self, p):
        return p.lista_comandos_loop + [p.comando]

    @_('comando') # type: ignore
    def lista_comandos_loop(self, p):
        return [p.comando]
        
    # Para funções - mesma estrutura
    @_('stmts comando') # type: ignore
    def stmts(self, p):
        return p.stmts + [p.comando]
        
    @_('comando') # type: ignore
    def stmts(self, p):
        return [p.comando]

    # Comando - regras específicas sem disjunção para eliminar conflitos shift/reduce
    # ORDEM É CRÍTICA: mais específicos primeiro para resolver ambiguidades
    # Estruturas de controle primeiro (pois são prefixadas com palavras-chave únicas)
    @_('declaracao_funcao') # type: ignore
    def comando(self, p):
        return p.declaracao_funcao
        
    @_('declaracao_var') # type: ignore
    def comando(self, p):
        return p.declaracao_var
        
    @_('comando_canal') # type: ignore
    def comando(self, p):
        return p.comando_canal
        
    @_('comando_se') # type: ignore
    def comando(self, p):
        return p.comando_se
        
    @_('comando_enquanto') # type: ignore
    def comando(self, p):
        return p.comando_enquanto
        
    @_('comando_para') # type: ignore
    def comando(self, p):
        return p.comando_para
        
    @_('comando_return') # type: ignore
    def comando(self, p):
        return p.comando_return
        
    @_('comando_send') # type: ignore
    def comando(self, p):
        return p.comando_send
        
    @_('comando_receive') # type: ignore
    def comando(self, p):
        return p.comando_receive
        
    @_('comando_escreva') # type: ignore
    def comando(self, p):
        return p.comando_escreva
        
    @_('comando_leia') # type: ignore
    def comando(self, p):
        return p.comando_leia
        
    @_('atribuicao_array') # type: ignore
    def comando(self, p):
        return p.atribuicao_array
        
    @_('atribuicao') # type: ignore
    def comando(self, p):
        return p.atribuicao
        
    @_('chamada_funcao') # type: ignore
    def comando(self, p):
        return p.chamada_funcao
        
    @_('bloco_stmt') # type: ignore
    def comando(self, p):
        return p.bloco_stmt

    # DECLARAÇÃO DE VARIÁVEIS
    @_('DECLARE ID DOIS_PONTOS tipo dimensoes') # type: ignore
    def declaracao_var(self, p):
        return ('declaracao_var_array', p.ID, p.tipo, p.dimensoes)

    @_('DECLARE ID DOIS_PONTOS tipo') # type: ignore
    def declaracao_var(self, p):
        return ('declaracao_var', p.ID, p.tipo)

    @_('dimensoes ABRE_COLCHETE NUM_INTEIRO FECHA_COLCHETE') # type: ignore
    def dimensoes(self, p):
        return p.dimensoes + [p.NUM_INTEIRO]

    @_('ABRE_COLCHETE NUM_INTEIRO FECHA_COLCHETE') # type: ignore
    def dimensoes(self, p):
        return [p.NUM_INTEIRO]

    @_('INTEIRO', 'REAL', 'STRING_TYPE', 'BOOL') # type: ignore
    def tipo(self, p):
        return p[0]

    # DECLARAÇÃO DE CANAL
    @_('C_CHANNEL ID ID ID') # type: ignore
    def comando_canal(self, p):
        return ('c_channel', p.ID0, p.ID1, p.ID2)
    
    # ATRIBUIÇÃO DE ARRAY - deve vir ANTES de atribuicao simples para resolver ambiguidade
    @_('ID indices ATRIBUICAO expressao') # type: ignore
    def atribuicao_array(self, p):
        return ('atribuicao_array', p.ID, p.indices, p.expressao)

    @_('indices ABRE_COLCHETE expressao FECHA_COLCHETE') # type: ignore
    def indices(self, p):
        return p.indices + [p.expressao]

    @_('ABRE_COLCHETE expressao FECHA_COLCHETE') # type: ignore
    def indices(self, p):
        return [p.expressao]
    
    # SEND E RECEIVE
    @_('ID PONTO SEND ABRE_PARENTESES lista_expressoes FECHA_PARENTESES') # type: ignore
    def comando_send(self, p):
        return ('send', p.ID, p.lista_expressoes)

    @_('ID PONTO RECEIVE ABRE_PARENTESES lista_ids FECHA_PARENTESES') # type: ignore
    def comando_receive(self, p):
        return ('receive', p.ID, p.lista_ids)
        
    # LOOP FOR
    @_('PARA ID EM intervalo lista_comandos_loop') # type: ignore
    def comando_para(self, p):
        return ('para', p.ID, p.intervalo, p.lista_comandos_loop)

    @_('NUM_INTEIRO PONTO PONTO NUM_INTEIRO') # type: ignore
    def intervalo(self, p):
        return ('intervalo', p.NUM_INTEIRO0, p.NUM_INTEIRO1)

    # FUNÇÕES
    @_('DEF ID ABRE_PARENTESES lista_params FECHA_PARENTESES DOIS_PONTOS tipo DOIS_PONTOS stmts') # type: ignore
    def declaracao_funcao(self, p):
        return ('declaracao_funcao', p.ID, p.lista_params, p.tipo, p.stmts)
        
    @_('DEF ID ABRE_PARENTESES FECHA_PARENTESES DOIS_PONTOS tipo DOIS_PONTOS stmts') # type: ignore
    def declaracao_funcao(self, p):
        return ('declaracao_funcao', p.ID, [], p.tipo, p.stmts)
        
    @_('lista_params VIRGULA param') # type: ignore
    def lista_params(self, p):
        return p.lista_params + [p.param]

    @_('param') # type: ignore
    def lista_params(self, p):
        return [p.param]
        
    @_('ID DOIS_PONTOS tipo') # type: ignore
    def param(self, p):
        return ('param', p.ID, p.tipo)
        
    @_('RETURN expressao') # type: ignore
    def comando_return(self, p):
        return ('return', p.expressao)
        
    # ATRIBUIÇÃO SIMPLES - deve vir depois de atribuicao_array
    @_('ID ATRIBUICAO expressao') # type: ignore
    def atribuicao(self, p):
        return ('atribuicao', p.ID, p.expressao)

    # ESTRUTURAS DE CONTROLE
    @_('SE expressao ENTAO opt_dois_pontos lista_comandos_loop SENAO opt_dois_pontos lista_comandos_loop') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos_loop0, p.lista_comandos_loop1)

    @_('SE expressao ENTAO opt_dois_pontos lista_comandos_loop') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos_loop, None)

    # Comando ENQUANTO
    # SOLUÇÃO: Usar FIM_ENQUANTO como marcador explícito de fim do loop
    # Isso elimina completamente os conflitos shift/reduce porque o parser sabe exatamente
    # onde termina o bloco de comandos do loop
    @_('ENQUANTO expressao FACA opt_dois_pontos lista_comandos_loop FIM_ENQUANTO') # type: ignore
    def comando_enquanto(self, p):
        # Identificar variável de controle deste loop
        # CORREÇÃO: Verificar ambos os lados da comparação (pode ser i < epocas ou epocas > i)
        var_controle = None
        if isinstance(p.expressao, tuple) and p.expressao[0] == 'binop':
            # Verificar lado esquerdo primeiro (mais comum: i < epocas)
            if len(p.expressao) > 2 and isinstance(p.expressao[2], tuple) and p.expressao[2][0] == 'id':
                var_controle = p.expressao[2][1]
            # Verificar lado direito se não encontrou no esquerdo (caso: epocas > i)
            if not var_controle and len(p.expressao) > 3:
                if isinstance(p.expressao[3], tuple) and p.expressao[3][0] == 'id':
                    var_controle = p.expressao[3][1]
        
        # Com FIM_ENQUANTO, não é mais necessário pós-processamento complexo,
        # mas mantemos a correção para compatibilidade com código antigo
        lista_comandos_corrigida = p.lista_comandos_loop
        if var_controle and isinstance(p.lista_comandos_loop, list):
            lista_comandos_corrigida = self._corrigir_comandos_loop(list(p.lista_comandos_loop), var_controle)
        
        return ('enquanto', p.expressao, lista_comandos_corrigida)
    
    def _corrigir_comandos_loop(self, comandos, var_controle):
        """Move comandos de incremento de var_controle que estão dentro de loops aninhados
        ou após loops aninhados de volta para o nível correto (dentro deste loop, após o loop aninhado)"""
        if not isinstance(comandos, list):
            return comandos
        
        nova_lista = []
        i = 0
        
        while i < len(comandos):
            cmd = comandos[i]
            
            # Se é um loop aninhado, processar recursivamente
            if isinstance(cmd, tuple) and cmd[0] == 'enquanto':
                # Identificar variável de controle do loop aninhado
                # CORREÇÃO: Verificar ambos os lados da comparação
                cond_aninhado = cmd[1] if len(cmd) > 1 else None
                var_aninhado = None
                if isinstance(cond_aninhado, tuple) and cond_aninhado[0] == 'binop':
                    # Verificar lado esquerdo primeiro (mais comum)
                    if len(cond_aninhado) > 2 and isinstance(cond_aninhado[2], tuple) and cond_aninhado[2][0] == 'id':
                        var_aninhado = cond_aninhado[2][1]
                    # Verificar lado direito se não encontrou no esquerdo
                    if not var_aninhado and len(cond_aninhado) > 3:
                        if isinstance(cond_aninhado[3], tuple) and cond_aninhado[3][0] == 'id':
                            var_aninhado = cond_aninhado[3][1]
                
                bloco_aninhado = cmd[2] if len(cmd) > 2 else []
                
                # Se este loop aninhado usa uma variável DIFERENTE, procurar por incremento
                # de var_controle dentro ou após este loop
                incremento_encontrado = None
                
                if var_aninhado and var_aninhado != var_controle:
                    # Este é um loop aninhado com variável diferente - incremento de var_controle
                    # após este loop pertence ao loop externo
                    
                    # Primeiro, procurar dentro do bloco do loop aninhado (incluindo estruturas se/senao)
                    if isinstance(bloco_aninhado, list):
                        # Remover incrementos de var_controle do bloco aninhado
                        # CORREÇÃO: Procurar recursivamente também dentro de estruturas se/senao
                        bloco_filtrado, incrementos_encontrados = self._extrair_incrementos_recursivo(
                            bloco_aninhado, var_controle
                        )
                        bloco_aninhado = bloco_filtrado
                        if incrementos_encontrados:
                            # Pegar o primeiro incremento encontrado (deve haver apenas um)
                            incremento_encontrado = incrementos_encontrados[0]
                    
                    # Depois, procurar após o loop aninhado na lista de comandos
                    # CORREÇÃO: NÃO mover incrementos que estão no final da lista de comandos
                    # (depois de todos os outros comandos, como escreva). Apenas mover incrementos
                    # que estão imediatamente após o loop aninhado, antes de outros comandos importantes.
                    if not incremento_encontrado:
                        j = i + 1
                        # Limitar a busca: só procurar incrementos imediatamente após o loop,
                        # não no final da lista
                        encontrou_comando_importante = False
                        while j < len(comandos):
                            prox_cmd = comandos[j]
                            if isinstance(prox_cmd, tuple):
                                # Se encontrou um comando importante (escreva, se, outro loop), 
                                # parar a busca - o incremento deve ficar no final
                                if prox_cmd[0] in ('escreva', 'se', 'enquanto', 'leia'):
                                    encontrou_comando_importante = True
                                    break
                                elif prox_cmd[0] == 'atribuicao':
                                    if prox_cmd[1] == var_controle:
                                        expr = prox_cmd[2] if len(prox_cmd) > 2 else None
                                        if isinstance(expr, tuple) and expr[0] == 'binop' and expr[1] == '+':
                                            left = expr[2] if len(expr) > 2 else None
                                            if isinstance(left, tuple) and left[0] == 'id' and left[1] == var_controle:
                                                # Só mover se não há comandos importantes depois
                                                # Se há escreva depois, não mover
                                                tem_escreva_depois = any(
                                                    isinstance(comandos[k], tuple) and comandos[k][0] == 'escreva'
                                                    for k in range(j + 1, len(comandos))
                                                )
                                                if not tem_escreva_depois:
                                                    incremento_encontrado = prox_cmd
                                                    # Remover da posição atual
                                                    comandos.pop(j)
                                                    break
                            j += 1
                        
                        # Se encontrou comando importante antes de encontrar incremento,
                        # não mover incrementos que possam estar depois
                        if encontrou_comando_importante:
                            pass  # Não fazer nada, deixar incremento onde está
                
                # Processar recursivamente o bloco aninhado (pode ter mais loops dentro)
                bloco_corrigido = self._corrigir_comandos_loop(bloco_aninhado, var_controle)
                
                # Adicionar o loop aninhado corrigido
                novo_loop = (cmd[0], cmd[1], bloco_corrigido) if len(cmd) >= 3 else cmd
                nova_lista.append(novo_loop)
                
                # Se encontrou incremento (dentro ou após o loop aninhado), adicioná-lo aqui
                # Isso garante que ele fique no nível correto do loop externo
                if incremento_encontrado:
                    nova_lista.append(incremento_encontrado)
            else:
                nova_lista.append(cmd)
            
            i += 1
        
        return nova_lista
    
    def _extrair_incrementos_recursivo(self, comandos, var_controle):
        """Remove recursivamente incrementos de var_controle de uma lista de comandos,
        incluindo dentro de estruturas se/senao e loops aninhados.
        Retorna (comandos_filtrados, lista_incrementos_encontrados)"""
        if not isinstance(comandos, list):
            return comandos, []
        
        comandos_filtrados = []
        incrementos_encontrados = []
        
        for cmd in comandos:
            if isinstance(cmd, tuple):
                # Verificar se é um incremento da variável de controle
                if cmd[0] == 'atribuicao' and cmd[1] == var_controle:
                    expr = cmd[2] if len(cmd) > 2 else None
                    if isinstance(expr, tuple) and expr[0] == 'binop' and expr[1] == '+':
                        left = expr[2] if len(expr) > 2 else None
                        if isinstance(left, tuple) and left[0] == 'id' and left[1] == var_controle:
                            # Encontrou incremento - adicionar à lista e não incluir no resultado
                            incrementos_encontrados.append(cmd)
                            continue
                
                # Se é uma estrutura se/senao, processar recursivamente
                if cmd[0] == 'se':
                    # cmd é: ('se', expressao, lista_comandos_then, lista_comandos_else)
                    then_block = cmd[2] if len(cmd) > 2 else []
                    else_block = cmd[3] if len(cmd) > 3 else None
                    
                    then_filtrado, then_incrementos = self._extrair_incrementos_recursivo(then_block, var_controle)
                    incrementos_encontrados.extend(then_incrementos)
                    
                    if else_block:
                        else_filtrado, else_incrementos = self._extrair_incrementos_recursivo(else_block, var_controle)
                        incrementos_encontrados.extend(else_incrementos)
                        comandos_filtrados.append((cmd[0], cmd[1], then_filtrado, else_filtrado))
                    else:
                        comandos_filtrados.append((cmd[0], cmd[1], then_filtrado, None))
                    continue
                
                # Se é um loop, processar recursivamente mas não extrair incrementos dele
                # (cada loop cuida dos seus próprios incrementos)
                if cmd[0] == 'enquanto':
                    bloco_loop = cmd[2] if len(cmd) > 2 else []
                    bloco_corrigido, _ = self._extrair_incrementos_recursivo(bloco_loop, var_controle)
                    comandos_filtrados.append((cmd[0], cmd[1], bloco_corrigido))
                    continue
            
            comandos_filtrados.append(cmd)
        
        return comandos_filtrados, incrementos_encontrados

    # LEITURA E ESCRITA
    @_('LEIA ABRE_PARENTESES ID FECHA_PARENTESES') # type: ignore
    def comando_leia(self, p):
        return ('leia', p.ID)

    @_('ESCREVA ABRE_PARENTESES lista_expressoes FECHA_PARENTESES') # type: ignore
    def comando_escreva(self, p):
        return ('escreva', p.lista_expressoes)

    @_('lista_expressoes VIRGULA expressao') # type: ignore
    def lista_expressoes(self, p):
        return p.lista_expressoes + [p.expressao]

    @_('expressao') # type: ignore
    def lista_expressoes(self, p):
        return [p.expressao]
        
    @_('lista_ids VIRGULA ID') # type: ignore
    def lista_ids(self, p):
        return p.lista_ids + [p.ID]
        
    @_('ID') # type: ignore
    def lista_ids(self, p):
        return [p.ID]

    # EXPRESSÕES - estrutura hierárquica clara para reduzir conflitos
    @_('expressao OP_REL expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_REL, p.expressao0, p.expressao1)

    @_('expressao_aditiva') # type: ignore
    def expressao(self, p):
        return p.expressao_aditiva

    @_('expressao_aditiva OP_SOMA expressao_multiplicativa') # type: ignore
    def expressao_aditiva(self, p):
        return ('binop', p.OP_SOMA, p.expressao_aditiva, p.expressao_multiplicativa)

    @_('expressao_aditiva OP_SUB expressao_multiplicativa') # type: ignore
    def expressao_aditiva(self, p):
        return ('binop', p.OP_SUB, p.expressao_aditiva, p.expressao_multiplicativa)

    @_('expressao_multiplicativa') # type: ignore
    def expressao_aditiva(self, p):
        return p.expressao_multiplicativa

    @_('expressao_multiplicativa OP_MULT fator') # type: ignore
    def expressao_multiplicativa(self, p):
        return ('binop', p.OP_MULT, p.expressao_multiplicativa, p.fator)

    @_('expressao_multiplicativa OP_DIV fator') # type: ignore
    def expressao_multiplicativa(self, p):
        return ('binop', p.OP_DIV, p.expressao_multiplicativa, p.fator)

    @_('fator') # type: ignore
    def expressao_multiplicativa(self, p):
        return p.fator

    # FATOR - ordem é importante para resolver ambiguidades
    @_('NUM_INTEIRO') # type: ignore
    def fator(self, p):
        return ('num_inteiro', p.NUM_INTEIRO)

    @_('NUM_REAL') # type: ignore
    def fator(self, p):
        return ('num_real', p.NUM_REAL)

    @_('STRING') # type: ignore
    def fator(self, p):
        return ('string', p.STRING)

    @_('BOOLEAN') # type: ignore
    def fator(self, p):
        return ('boolean', p.BOOLEAN if isinstance(p.BOOLEAN, bool) else (p.BOOLEAN == 'True' or p.BOOLEAN is True))

    # Chamada de função - deve vir antes de ID simples para resolver ambiguidade
    @_('ID ABRE_PARENTESES lista_expressoes FECHA_PARENTESES') # type: ignore
    def chamada_funcao(self, p):
        return ('chamada_funcao', p.ID, p.lista_expressoes)

    @_('ID ABRE_PARENTESES FECHA_PARENTESES') # type: ignore
    def chamada_funcao(self, p):
        return ('chamada_funcao', p.ID, [])
    
    # Acesso a array - deve vir antes de ID simples
    @_('ID indices') # type: ignore
    def fator(self, p):
        return ('acesso_array', p.ID, p.indices)

    @_('ID') # type: ignore
    def fator(self, p):
        return ('id', p.ID)

    @_('chamada_funcao') # type: ignore
    def fator(self, p):
        return p.chamada_funcao
        
    @_('ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def fator(self, p):
        return p.expressao

    @_('OP_SUB fator %prec UMINUS') # type: ignore
    def fator(self, p):
        return ('unop', '-', p.fator)
