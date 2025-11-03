#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Léxico do compilador MiniPar
"""

from sly import Lexer


class MiniParLexer(Lexer):
    tokens = {
        'PROGRAMA', 'FIM_PROGRAMA', 'DECLARE', 'INTEIRO', 'REAL', 'STRING_TYPE', 'BOOL', 'C_CHANNEL',
        'SE', 'ENTAO', 'SENAO', 'FIM_SE', 'ENQUANTO', 'FACA', 'FIM_ENQUANTO', 
        'LEIA', 'ESCREVA', 'SEQ', 'PAR', 'SEND', 'RECEIVE', 'DEF', 'RETURN', 'PARA', 'EM',
        'ID', 'NUM_INTEIRO', 'NUM_REAL', 'STRING', 'BOOLEAN',
        'ATRIBUICAO', 'OP_SOMA', 'OP_SUB', 'OP_MULT', 'OP_DIV', 'OP_REL',
        'ABRE_PARENTESES', 'FECHA_PARENTESES', 'ABRE_CHAVES', 'FECHA_CHAVES',
        'ABRE_COLCHETE', 'FECHA_COLCHETE', 'DOIS_PONTOS', 'VIRGULA', 'PONTO'
    }
    
    ignore = ' \t\r'
    ignore_comment = r'\#.*'
    
    OP_REL = r'==|!=|<=|>=|<|>'
    ATRIBUICAO = r'='
    OP_SOMA = r'\+'
    OP_SUB = r'-'
    OP_MULT = r'\*'
    OP_DIV = r'/'
    ABRE_PARENTESES = r'\('
    FECHA_PARENTESES = r'\)'
    ABRE_CHAVES = r'\{'
    FECHA_CHAVES = r'\}'
    ABRE_COLCHETE = r'\['
    FECHA_COLCHETE = r'\]'
    DOIS_PONTOS = r':'
    VIRGULA = r','
    PONTO = r'\.'
    
    # Adicionar estas regras para aceitar PAR: e SEQ: como tokens
    @_(r'PAR\s*:')  # type: ignore
    def PAR_COLON(self, t):
        t.type = 'PAR'
        return t
    
    @_(r'SEQ\s*:')  # type: ignore  
    def SEQ_COLON(self, t):
        t.type = 'SEQ'
        return t
    
    # Regras específicas para booleanos ANTES da regra ID geral
    @_(r'verdadeiro\b')  # type: ignore
    def BOOLEAN_VERDADEIRO(self, t):
        t.type = 'BOOLEAN'
        t.value = True
        return t

    @_(r'falso\b')  # type: ignore  
    def BOOLEAN_FALSO(self, t):
        t.type = 'BOOLEAN'
        t.value = False
        return t
    
    ID = r'[a-zA-Z_][a-zA-Z0-9_\-]*'
    
    ID['program-minipar'] = 'PROGRAMA' 
    ID['programa-miniPar'] = 'PROGRAMA'
    ID['programa_minipar'] = 'PROGRAMA'
    ID['fim_programa'] = 'FIM_PROGRAMA'
    ID['declare'] = 'DECLARE'
    ID['inteiro'] = 'INTEIRO'
    ID['real'] = 'REAL'
    ID['string'] = 'STRING_TYPE'
    ID['bool'] = 'BOOL'
    ID['true'] = 'BOOLEAN'  
    ID['false'] = 'BOOLEAN'
    ID['True'] = 'BOOLEAN'
    ID['False'] = 'BOOLEAN'
    ID['c_channel'] = 'C_CHANNEL'
    ID['seq'] = 'SEQ'
    ID['SEQ'] = 'SEQ'
    ID['par'] = 'PAR'
    ID['se'] = 'SE'
    ID['entao'] = 'ENTAO'
    ID['senao'] = 'SENAO'
    ID['fim_se'] = 'FIM_SE'
    ID['enquanto'] = 'ENQUANTO'
    ID['faca'] = 'FACA'
    ID['fim_enquanto'] = 'FIM_ENQUANTO'
    ID['leia'] = 'LEIA'
    ID['escreva'] = 'ESCREVA'
    ID['send'] = 'SEND'
    ID['receive'] = 'RECEIVE'
    ID['def'] = 'DEF'
    ID['return'] = 'RETURN'
    ID['para'] = 'PARA'
    ID['em'] = 'EM'
    ID['True'] = 'BOOLEAN'
    ID['False'] = 'BOOLEAN'
    ID['faca'] = 'FACA'
    ID['FACA'] = 'FACA'

    @_(r'\".*?\"') # type: ignore
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t
        
    @_(r'-?\d+\.\d+') # type: ignore
    def NUM_REAL(self, t):
        t.value = float(t.value)
        return t

    @_(r'-?\d+') # type: ignore
    def NUM_INTEIRO(self, t):
        t.value = int(t.value)
        return t    

    @_(r'\n+') # type: ignore
    def ignore_newline(self, t):
        self.lineno += len(t.value)
        
    def error(self, t):
        t.type = 'ERROR'
        t.value = t.value[0]
        self.index += 1
        return t

