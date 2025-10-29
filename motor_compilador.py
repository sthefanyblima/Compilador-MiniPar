import sys
import socket
import threading
import struct
from sly import Lexer, Parser
import math

# --- SISTEMA DE CANAIS E THREADS ---
class ChannelManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.channels = {}
            return cls._instance
    
    def create_channel(self, name, comp1, comp2):
        self.channels[name] = {
            'comp1': comp1,
            'comp2': comp2,
            'data': None,
            'lock': threading.Lock()
        }
    
    def send_data(self, channel_name, data):
        if channel_name in self.channels:
            with self.channels[channel_name]['lock']:
                self.channels[channel_name]['data'] = data
                return True
        return False
    
    def receive_data(self, channel_name):
        if channel_name in self.channels:
            with self.channels[channel_name]['lock']:
                data = self.channels[channel_name]['data']
                self.channels[channel_name]['data'] = None
                return data
        return None

class ThreadManager:
    def __init__(self):
        self.threads = []
        self.results = {}
        self.lock = threading.Lock()
    
    def execute_parallel(self, blocks):
        self.threads = []
        self.results = {}
        
        def run_block(block_id, block_code):
            try:
                result = f"Thread_{block_id}_completed"
                with self.lock:
                    self.results[block_id] = result
            except Exception as e:
                with self.lock:
                    self.results[block_id] = f"Error: {str(e)}"
        
        for i, block in enumerate(blocks):
            thread = threading.Thread(target=run_block, args=(i, block))
            self.threads.append(thread)
            thread.start()
        
        for thread in self.threads:
            thread.join()
        
        return self.results
# --- FIM DO SISTEMA DE CANAIS ---

# --- FUNÇÃO AUXILIAR PARA FORMATAR A AST ---
def formatar_ast(node, level=0):
    if node is None:
        return ""
    
    # Se node não for uma tupla ou lista, tratamos como valor simples
    if not isinstance(node, (tuple, list)):
        indent = '  ' * level
        return f"{indent}- {repr(node)}\n"
    
    indent = '  ' * level
    result = f"{indent}- {node[0]}\n"
    
    for item in node[1:]:
        if isinstance(item, tuple):
            result += formatar_ast(item, level + 1)
        elif isinstance(item, list):
            for sub_item in item:
                result += formatar_ast(sub_item, level + 1)
        elif item is not None:
            if node[0] == 'string':
                result += f"{'  ' * (level + 1)}- \"{item}\"\n"
            else:
                result += f"{'  ' * (level + 1)}- '{item}'\n"
            
    return result

# ---------------------------------------
#   ANALISADOR LÉXICO
# ---------------------------------------
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
    ID['verdadeiro'] = 'BOOLEAN'
    ID['falso'] = 'BOOLEAN'
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

    @_(r'verdadeiro')  # type: ignore
    def BOOLEAN(self, t):
        t.value = True
        return t

    @_(r'falso')  # type: ignore  
    def BOOLEAN(self, t):
        t.value = False
        return t    

    @_(r'\n+') # type: ignore
    def ignore_newline(self, t):
        self.lineno += len(t.value)
        
    def error(self, t):
        t.type = 'ERROR'
        t.value = t.value[0]
        self.index += 1
        return t

# ---------------------------------------
#   ANALISADOR SINTÁTICO
# ---------------------------------------
class MiniParParser(Parser):
    tokens = MiniParLexer.tokens

    precedence = (
        ('left', 'OP_SOMA', 'OP_SUB'),
        ('left', 'OP_MULT', 'OP_DIV'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.syntax_errors = []
        self.indent_level = 0

    def error(self, p):
        if p:
            error_message = f"Erro de Sintaxe: Token inesperado '{p.value}' (Tipo: {p.type}) na linha {p.lineno}"
            self.syntax_errors.append(error_message)
        else:
            error_message = "Erro de Sintaxe: Fim inesperado do arquivo."
            self.syntax_errors.append(error_message)

    # Regra principal do programa
    @_('PROGRAMA lista_comandos') # type: ignore
    def programa_minipar(self, p):
        return ('programa_minipar', p.lista_comandos)

    # Blocos SEQ e PAR - aceitando ambas as sintaxes
    @_('PAR DOIS_PONTOS lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_par', p.lista_comandos)

    @_('SEQ DOIS_PONTOS lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_seq', p.lista_comandos)
    
    # Regras alternativas para aceitar PAR: e SEQ: como uma unidade
    @_('PAR lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_par', p.lista_comandos)

    @_('SEQ lista_comandos') # type: ignore
    def bloco_stmt(self, p):
        return ('bloco_seq', p.lista_comandos)
        
    @_('lista_comandos comando') # type: ignore
    def lista_comandos(self, p):
        return p.lista_comandos + [p.comando]

    @_('comando') # type: ignore
    def lista_comandos(self, p):
        return [p.comando]
        
    @_('comando') # type: ignore
    def stmts(self, p):
        return [p.comando]
        
    @_('stmts comando') # type: ignore
    def stmts(self, p):
        return p.stmts + [p.comando]

    @_('declaracao_var', 'comando_canal', 'atribuicao', 'comando_se', 'comando_enquanto', 
       'comando_leia', 'comando_escreva', 'comando_send', 'comando_receive', 'bloco_stmt',
       'comando_para', 'chamada_funcao', 'comando_return', 'declaracao_funcao', 'atribuicao_array') # type: ignore
    def comando(self, p):
        return p[0]
        
    # DECLARAÇÃO DE VARIÁVEIS - Adicionar suporte a arrays
    @_('DECLARE ID DOIS_PONTOS tipo') # type: ignore
    def declaracao_var(self, p):
        return ('declaracao_var', p.ID, p.tipo)

    @_('DECLARE ID DOIS_PONTOS tipo dimensoes') # type: ignore
    def declaracao_var(self, p):
        return ('declaracao_var_array', p.ID, p.tipo, p.dimensoes)

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
    
    # ATRIBUIÇÃO DE ARRAY
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
    @_('PARA ID EM intervalo lista_comandos') # type: ignore
    def comando_para(self, p):
        return ('para', p.ID, p.intervalo, p.lista_comandos)

    @_('NUM_INTEIRO PONTO PONTO NUM_INTEIRO') # type: ignore
    def intervalo(self, p):
        return ('intervalo', p.NUM_INTEIRO0, p.NUM_INTEIRO1)

    # FUNÇÕES - CORRIGIDO: aceitando DOIS_PONTOS após parâmetros
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
        
    # ATRIBUIÇÃO
    @_('ID ATRIBUICAO expressao') # type: ignore
    def atribuicao(self, p):
        return ('atribuicao', p.ID, p.expressao)

    # ESTRUTURAS DE CONTROLE - CORREÇÃO: aceitando DOIS_PONTOS após condições
    @_('SE expressao ENTAO DOIS_PONTOS lista_comandos') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos, None)

    @_('SE expressao ENTAO DOIS_PONTOS lista_comandos SENAO DOIS_PONTOS lista_comandos') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos0, p.lista_comandos1)

    # Regras alternativas sem DOIS_PONTOS
    @_('SE expressao ENTAO lista_comandos') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos, None)

    @_('SE expressao ENTAO lista_comandos SENAO lista_comandos') # type: ignore
    def comando_se(self, p):
        return ('se', p.expressao, p.lista_comandos0, p.lista_comandos1)

    # Comando ENQUANTO - aceitando ambas as sintaxes
    @_('ENQUANTO expressao FACA DOIS_PONTOS lista_comandos') # type: ignore
    def comando_enquanto(self, p):
        return ('enquanto', p.expressao, p.lista_comandos)

    @_('ENQUANTO expressao FACA lista_comandos') # type: ignore
    def comando_enquanto(self, p):
        return ('enquanto', p.expressao, p.lista_comandos)

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

    # EXPRESSÕES - Adicionar acesso a arrays
    @_('expressao OP_SOMA expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_SOMA, p.expressao0, p.expressao1)

    @_('expressao OP_SUB expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_SUB, p.expressao0, p.expressao1)

    @_('expressao OP_MULT expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_MULT, p.expressao0, p.expressao1)

    @_('expressao OP_DIV expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_DIV, p.expressao0, p.expressao1)

    @_('expressao OP_REL expressao') # type: ignore
    def expressao(self, p):
        return ('binop', p.OP_REL, p.expressao0, p.expressao1)

    @_('termo') # type: ignore
    def expressao(self, p):
        return p.termo

    @_('termo OP_MULT fator') # type: ignore
    def termo(self, p):
        return ('binop', p.OP_MULT, p.termo, p.fator)

    @_('termo OP_DIV fator') # type: ignore
    def termo(self, p):
        return ('binop', p.OP_DIV, p.termo, p.fator)

    @_('fator') # type: ignore
    def termo(self, p):
        return p.fator

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
        return ('boolean', p.BOOLEAN == 'True')

    @_('ID') # type: ignore
    def fator(self, p):
        return ('id', p.ID)

    @_('ID indices') # type: ignore
    def fator(self, p):
        return ('acesso_array', p.ID, p.indices)

    @_('ID ABRE_PARENTESES lista_expressoes FECHA_PARENTESES') # type: ignore
    def chamada_funcao(self, p):
        return ('chamada_funcao', p.ID, p.lista_expressoes)

    @_('ID ABRE_PARENTESES FECHA_PARENTESES') # type: ignore
    def chamada_funcao(self, p):
        return ('chamada_funcao', p.ID, [])
        
    @_('chamada_funcao') # type: ignore
    def fator(self, p):
        return p.chamada_funcao
        
    @_('ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def fator(self, p):
        return p.expressao

    @_('OP_SUB fator %prec UMINUS') # type: ignore
    def fator(self, p):
        return ('unop', '-', p.fator)
    

# --- ANALISADOR SEMÂNTICO ---
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.channel_table = {}
        self.function_table = {}
        self.current_function_type = None
        self.errors = []
        self.array_dims = {}  # Armazenar dimensões dos arrays
        self.declared_vars = set()  # ADICIONE ESTA LINHA
        
    def visit(self, node):
        if node is None:
            return None
        
        method_name = f'visit_{node[0]}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node):
        node_type = node[0]
        results = []
        for child in node[1:]:
            if isinstance(child, tuple):
                results.append(self.visit(child))
            elif isinstance(child, list):
                list_results = []
                for item in child:
                    if isinstance(item, tuple):
                        list_results.append(self.visit(item))
                    else:
                        list_results.append(item)
                results.append(list_results)
            else:
                results.append(child)
        
        return (node_type,) + tuple(results)

    def visit_programa_minipar(self, node):
        for cmd in node[1]:
            self.visit(cmd)
        return node

    def visit_bloco_seq(self, node):
        for cmd in node[1]:
            self.visit(cmd)
        return node

    def visit_bloco_par(self, node):
        for cmd in node[1]:
            self.visit(cmd)
        return node

    def visit_declaracao_var(self, node):
        var_name = node[1]
        var_type = node[2]
        normalized_type = self.normalize_type(var_type)
        if var_name in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' já declarada.")
        else:
            self.symbol_table[var_name] = normalized_type
        return (node[0], var_name, normalized_type)

    def visit_declaracao_var_array(self, node):
        var_name = node[1]
        var_type = node[2]
        dimensions = node[3]
        normalized_type = self.normalize_type(var_type)
        if var_name in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' já declarada.")
        else:
            self.symbol_table[var_name] = normalized_type
            self.array_dims[var_name] = dimensions
        return (node[0], var_name, normalized_type, dimensions)

    def visit_atribuicao_array(self, node):
        var_name = node[1]
        indices = node[2]
        expr_node = node[3]
        
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' não foi declarada.")
            return ('atribuicao_array', var_name, indices, self.visit(expr_node), 'error')
            
        var_type = self.symbol_table[var_name]
        expr_type_node = self.visit(expr_node)
        expr_type = self.get_type(expr_type_node)

        # Verificar índices
        for index in indices:
            index_type = self.get_type(index)
            if index_type != 'INTEIRO' and index_type != 'error':
                self.errors.append(f"Erro Semântico: Índice de array deve ser INTEIRO, mas é '{index_type}'.")

        if var_type != expr_type and expr_type != 'error':
            if var_type == 'REAL' and expr_type == 'INTEIRO':
                return ('atribuicao_array', var_name, indices, expr_type_node, 'REAL')
            self.errors.append(f"Erro Semântico: Tipos incompatíveis. Não é possível atribuir '{expr_type}' à variável '{var_name}' (tipo '{var_type}').")
            return ('atribuicao_array', var_name, indices, expr_type_node, 'error')
            
        return ('atribuicao_array', var_name, indices, expr_type_node, var_type)

    def visit_acesso_array(self, node):
        var_name = node[1]
        indices = node[2]
        
        # Verificar se a variável existe na tabela de símbolos
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' não foi declarada.")
            return ('acesso_array', var_name, indices, 'error')
        
        # Processar índices
        index_results = []
        for index in indices:
            index_type_node = self.visit(index)
            index_type = self.get_type(index_type_node)
            if index_type != 'INTEIRO' and index_type != 'error':
                self.errors.append(f"Erro Semântico: Índice de array deve ser INTEIRO, mas é '{index_type}'.")
            index_results.append(index_type_node)
        
        var_type = self.symbol_table[var_name]
        return ('acesso_array', var_name, index_results, var_type)
        
    def visit_c_channel(self, node):
        channel_name = node[1]
        comp1 = node[2]
        comp2 = node[3]
        if channel_name in self.channel_table:
            self.errors.append(f"Erro Semântico: Canal '{channel_name}' já declarado.")
        else:
            self.channel_table[channel_name] = (comp1, comp2)
        return node
        
    def visit_declaracao_funcao(self, node):
        func_name = node[1]
        params = node[2]
        func_type = node[3]
        body = node[4]
        
        if func_name in self.function_table:
            self.errors.append(f"Erro Semântico: Função '{func_name}' já declarada.")
            return node
            
        param_types = []
        param_names = set()
        
        old_table = self.symbol_table.copy()
        self.symbol_table[func_name] = 'function'
        
        for param in params:
            p_name = param[1]
            p_type = param[2]
            normalized_p_type = self.normalize_type(p_type)
            if p_name in param_names:
                self.errors.append(f"Erro Semântico: Parâmetro '{p_name}' duplicado na função '{func_name}'.")
            param_names.add(p_name)
            param_types.append(normalized_p_type)
            self.symbol_table[p_name] = normalized_p_type
            
        normalized_func_type = self.normalize_type(func_type)
        self.function_table[func_name] = {'type': normalized_func_type, 'params': param_types}
        
        self.current_function_type = normalized_func_type
        for stmt in body:
            self.visit(stmt)
        self.current_function_type = None
        self.symbol_table = old_table
        
        return node
        
    def visit_return(self, node):
        if self.current_function_type is None:
            self.errors.append("Erro Semântico: Comando 'return' encontrado fora de uma função.")
            return ('return', self.visit(node[1]), 'error')
            
        return_type = self.visit(node[1])
        
        if return_type[0] == 'id':
            var_name = return_type[1]
            if var_name not in self.symbol_table:
                self.errors.append(f"Erro Semântico: Variável '{var_name}' não declarada.")
                expr_type = 'error'
            else:
                expr_type = self.symbol_table[var_name]
        elif return_type[0] == 'chamada_funcao':
            func_name = return_type[1]
            if func_name not in self.function_table:
                self.errors.append(f"Erro Semântico: Função '{func_name}' não declarada.")
                expr_type = 'error'
            else:
                expr_type = self.function_table[func_name]['type']
        else:
             expr_type = self.get_type(return_type)
             
        # Comparar tipos normalizados
        if expr_type != self.current_function_type and expr_type != 'error':
            self.errors.append(f"Erro Semântico: Tipo de retorno da função ({expr_type}) não é compatível com o tipo esperado ({self.current_function_type}).")
            
        return ('return', return_type, expr_type)

    def visit_atribuicao(self, node):
        var_name = node[1]
        expr_node = node[2]
        
        # Se a variável não foi declarada, declarar implicitamente como INTEIRO
        if var_name not in self.symbol_table:
            self.symbol_table[var_name] = 'INTEIRO'
                
        var_type = self.symbol_table[var_name]
        expr_type_node = self.visit(expr_node)
        expr_type = self.get_type(expr_type_node)

        # Comparar tipos normalizados
        if var_type != expr_type and expr_type != 'error':
            if var_type == 'REAL' and expr_type == 'INTEIRO':
                return ('atribuicao', var_name, expr_type_node, 'REAL')
            self.errors.append(f"Erro Semântico: Tipos incompatíveis. Não é possível atribuir '{expr_type}' à variável '{var_name}' (tipo '{var_type}').")
            return ('atribuicao', var_name, expr_type_node, 'error')
            
        return ('atribuicao', var_name, expr_type_node, var_type)
        
    def visit_send(self, node):
        channel_name = node[1]
        if channel_name not in self.channel_table:
            self.errors.append(f"Erro Semântico: Canal '{channel_name}' não declarado.")
        
        for expr in node[2]:
            self.visit(expr) 
        return node
        
    def visit_receive(self, node):
        channel_name = node[1]
        if channel_name not in self.channel_table:
            self.errors.append(f"Erro Semântico: Canal '{channel_name}' não declarado.")
            
        for var_name in node[2]:
            if var_name not in self.symbol_table:
                self.errors.append(f"Erro Semântico: Variável '{var_name}' não declarada (em 'receive').")
        return node
        
    def visit_leia(self, node):
        var_name = node[1]
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' não declarada (em 'leia').")
        return node
        
    def visit_escreva(self, node):
        for expr in node[1]:
            self.visit(expr)
        return node

    def visit_se(self, node):
        cond_node = node[1]
        bloco_then = node[2]
        bloco_else = node[3]

        cond_type_node = self.visit(cond_node)
        cond_type = self.get_type(cond_type_node)

        if cond_type != 'BOOL' and cond_type != 'error':
            self.errors.append(f"Erro Semântico: A condição do 'SE' deve ser 'BOOL', mas é '{cond_type}'.")

        for cmd in bloco_then:
            self.visit(cmd)
        if bloco_else:
            for cmd in bloco_else:
                self.visit(cmd)
            
        return ('se', cond_type_node, bloco_then, bloco_else)

    def visit_enquanto(self, node):
        cond_node = node[1]
        bloco_faca = node[2]

        cond_type_node = self.visit(cond_node)
        cond_type = self.get_type(cond_type_node)

        if cond_type != 'BOOL' and cond_type != 'error':
            self.errors.append(f"Erro Semântico: A condição do 'ENQUANTO' deve ser 'BOOL', mas é '{cond_type}'.")

        for cmd in bloco_faca:
            self.visit(cmd)
        return ('enquanto', cond_type_node, bloco_faca)
        
    def visit_para(self, node):
        var_name = node[1]
        intervalo = node[2]
        bloco = node[3]
        
        old_table = self.symbol_table.copy()
        if var_name in self.symbol_table:
             self.errors.append(f"Erro Semântico: Variável de loop '{var_name}' já declarada no escopo.")
        self.symbol_table[var_name] = 'INTEIRO'
        
        for cmd in bloco:
            self.visit(cmd)
        self.symbol_table = old_table
        
        if self.get_type(intervalo[1]) != 'INTEIRO' or self.get_type(intervalo[2]) != 'INTEIRO':
             self.errors.append(f"Erro Semântico: Limites do loop 'PARA' devem ser 'INTEIRO'.")
             
        return node

    def visit_binop(self, node):
        op = node[1]
        left_node = self.visit(node[2])
        right_node = self.visit(node[3])

        left_type = self.get_type(left_node)
        right_type = self.get_type(right_node)  # Corrigido: era right_node_type

        if left_type == 'error' or right_type == 'error':
            return (node[0], op, left_node, right_node, 'error')

        # Operações aritméticas
        if op in ('+', '-', '*', '/'):
            if left_type in ('INTEIRO', 'REAL') and right_type in ('INTEIRO', 'REAL'):
                # Se qualquer operando for REAL, o resultado é REAL
                if left_type == 'REAL' or right_type == 'REAL' or op == '/':
                    return (node[0], op, left_node, right_node, 'REAL')
                else:
                    return (node[0], op, left_node, right_node, 'INTEIRO')
            else:
                self.errors.append(f"Erro Semântico: Operação '{op}' entre tipos incompatíveis: '{left_type}' e '{right_type}'.")
                return (node[0], op, left_node, right_node, 'error')

        # Operações relacionais
        if op in ('==', '!=', '<', '>', '<=', '>='):
            if left_type in ('INTEIRO', 'REAL') and right_type in ('INTEIRO', 'REAL'):
                return (node[0], op, left_node, right_node, 'BOOL')
            else:
                self.errors.append(f"Erro Semântico: Operação relacional '{op}' entre tipos incompatíveis: '{left_type}' e '{right_type}'.")
                return (node[0], op, left_node, right_node, 'error')

        return (node[0], op, left_node, right_node, 'error')

    def visit_unop(self, node):
        op = node[1]
        expr_node = self.visit(node[2])
        expr_type = self.get_type(expr_node)

        if op == '-':
            if expr_type not in ('INTEIRO', 'REAL'):
                self.errors.append(f"Erro Semântico: Operador '-' unário aplicado a tipo incompatível: '{expr_type}'.")
                return (node[0], op, expr_node, 'error')
            return (node[0], op, expr_node, expr_type)
            
        return (node[0], op, expr_node, 'error')

    def visit_chamada_funcao(self, node):
        func_name = node[1]
        args = node[2]
        
        if func_name not in self.function_table:
            self.errors.append(f"Erro Semântico: Função '{func_name}' não foi declarada.")
            return (node[0], func_name, args, 'error')
            
        func_info = self.function_table[func_name]
        expected_params = func_info['params']
        
        if len(args) != len(expected_params):
            self.errors.append(f"Erro Semântico: Função '{func_name}' espera {len(expected_params)} argumentos, mas recebeu {len(args)}.")
            return (node[0], func_name, args, func_info['type']) 
            
        for i, arg_node in enumerate(args):
            arg_type_node = self.visit(arg_node)
            arg_type = self.get_type(arg_type_node)
            expected_type = expected_params[i]
            
            # Comparar tipos normalizados
            if arg_type != expected_type and arg_type != 'error':
                if expected_type == 'REAL' and arg_type == 'INTEIRO':
                    pass  # Conversão implícita de INTEIRO para REAL permitida
                else:
                    self.errors.append(f"Erro Semântico: Argumento {i+1} da função '{func_name}': esperava '{expected_type}', mas recebeu '{arg_type}'.")
        
        return (node[0], func_name, args, func_info['type'])

    def normalize_type(self, type_str):
        """Normaliza tipos para maiúsculas internamente"""
        if isinstance(type_str, str):
            upper_type = type_str.upper()
            # Mapeia tanto 'string' quanto 'STRING_TYPE' para 'STRING_TYPE'
            if upper_type in ['INTEIRO', 'REAL', 'STRING_TYPE', 'BOOL', 'STRING']:
                if upper_type == 'STRING':
                    return 'STRING_TYPE'
                return upper_type
        return type_str

    def get_type(self, node):
        if not isinstance(node, tuple):
            return 'error'
            
        node_type = node[0]
        
        if node_type == 'num_inteiro': return 'INTEIRO'
        if node_type == 'num_real': return 'REAL'
        if node_type == 'string': return 'STRING_TYPE'
        if node_type == 'boolean': return 'BOOL'
        
        if node_type == 'id':
            var_name = node[1]
            if var_name not in self.symbol_table:
                # Para variáveis não declaradas, assumir INTEIRO
                self.symbol_table[var_name] = 'INTEIRO'
                # self.errors.append(f"Aviso: Variável '{var_name}' não declarada, assumindo tipo INTEIRO.")
                return 'INTEIRO'
            return self.symbol_table[var_name]
            
        if len(node) > 1 and node[-1] in ('INTEIRO', 'REAL', 'STRING_TYPE', 'BOOL', 'error'):
            return node[-1]
            
        if node_type == 'chamada_funcao':
            func_name = node[1]
            if func_name not in self.function_table:
                self.errors.append(f"Erro Semântico: Função '{func_name}' não foi declarada (em get_type).")
                return 'error'
            return self.function_table[func_name]['type']

        if node_type in ('binop', 'unop', 'atribuicao'):
            if node[-1] in ('INTEIRO', 'REAL', 'BOOL', 'error'):
                return node[-1]

        return 'error'
    
    
# --- GERADOR DE CÓDIGO DE 3 ENDEREÇOS (C3E) ---
class C3EGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        self.declared_vars = set()
        self.function_code = {}
        self.current_function = None
        self.array_sizes = {} 

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"
        
    def add_code(self, *args):
        line = " ".join(map(str, args))
        if self.current_function:
            self.function_code[self.current_function].append(line)
        else:
            self.code.append(line)

    def generate(self, node):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        self.declared_vars = set()
        self.function_code = {}
        self.current_function = None
        self.array_sizes = {}
        self.visit(node)
        return self.code
        
    def visit(self, node):
        if node is None:
            return
        
        method_name = f'visit_{node[0]}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            return self.generic_visit(node)

    def generic_visit(self, node):
        for child in node[1:]:
            if isinstance(child, tuple):
                self.visit(child)
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, tuple):
                        self.visit(item)
                        
    def visit_programa_minipar(self, node):
        self.add_code("START_PROGRAM")
        
        for no_filho in node[1]:
            self.visit(no_filho)
            
        self.add_code("END_PROGRAM")

    def visit_bloco_seq(self, node):
        for cmd in node[1]:
            self.visit(cmd)
            
    def visit_bloco_par(self, node):
        self.add_code("PARALLEL_START")
        for cmd in node[1]:
            self.visit(cmd)
        self.add_code("PARALLEL_END")

    def visit_declaracao_var(self, node):
        var_name = node[1]
        var_type = node[2].upper()  # Normalizar para maiúsculas
        self.declared_vars.add(var_name)
        return (node[0], var_name, var_type)
        
    def visit_c_channel(self, node):
        channel_name = node[1]
        self.declared_vars.add(channel_name)
        self.add_code("CHANNEL_DEF", channel_name, node[2], node[3])
        
    def visit_declaracao_funcao(self, node):
        func_name = node[1]
        params = node[2]
        
        self.current_function = func_name
        self.function_code[func_name] = []
        
        self.add_code(f"FUNC_BEGIN {func_name}")
        for p_name, p_type in [(p[1], p[2]) for p in params]:
            self.add_code(f"PARAM {p_name}")
            self.declared_vars.add(p_name) 
            
        for stmt in node[4]:
            self.visit(stmt)
            
        self.add_code(f"FUNC_END {func_name}")
        self.current_function = None
        
    def visit_return(self, node):
        expr_result = self.visit(node[1])
        self.add_code("RETURN", expr_result)
        
    def visit_atribuicao(self, node):
        var_name = node[1]
        expr_result = self.visit(node[2])
        
        # Adicionar a variável ao conjunto de variáveis declaradas se não existir
        if var_name not in self.declared_vars:
            self.declared_vars.add(var_name)
        
        self.add_code(var_name, "=", expr_result)

    def visit_send(self, node):
        channel_name = node[1]
        results = []
        for expr in node[2]:
            results.append(self.visit(expr))
        
        for r in results:
            self.add_code("SEND_PARAM", r)
        self.add_code("SEND", channel_name, len(results))

    def visit_receive(self, node):
        channel_name = node[1]
        var_list = node[2]
        
        self.add_code("RECEIVE", channel_name, len(var_list))
        for i, var_name in enumerate(var_list):
            temp_result = self.new_temp()
            self.add_code("GET_RECV_PARAM", temp_result, i)
            self.add_code(var_name, "=", temp_result)
            
    def visit_leia(self, node):
        var_name = node[1]
        self.add_code("READ", var_name)
        
    def visit_escreva(self, node):
        expr_results = [self.visit(expr) for expr in node[1]]
        for result in expr_results:
            self.add_code("WRITE", result)
            
    def visit_se(self, node):
        cond_expr = node[1]
        bloco_then = node[2]
        bloco_else = node[3]
        
        cond_result = self.visit(cond_expr)
        
        label_then = self.new_label()
        label_else = self.new_label()
        label_end = self.new_label()
        
        self.add_code("IF_GOTO", cond_result, label_then)
        if bloco_else:
            self.add_code("GOTO", label_else)
        else:
            self.add_code("GOTO", label_end) 
            
        self.add_code("LABEL", label_then)
        for cmd in bloco_then:
            self.visit(cmd)
        self.add_code("GOTO", label_end)
            
        if bloco_else:
            self.add_code("LABEL", label_else)
            for cmd in bloco_else:
                self.visit(cmd)
                
        self.add_code("LABEL", label_end)

    def visit_enquanto(self, node):
        cond_expr = node[1]
        bloco_faca = node[2]
        
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()
        
        self.add_code("LABEL", label_start)
        cond_result = self.visit(cond_expr)
        
        self.add_code("IF_GOTO", cond_result, label_body)
        self.add_code("GOTO", label_end)
        
        self.add_code("LABEL", label_body)
        for cmd in bloco_faca:
            self.visit(cmd)
            
        self.add_code("GOTO", label_start)
        self.add_code("LABEL", label_end)
        
    def visit_para(self, node):
        var_name = node[1]
        intervalo = node[2]
        bloco = node[3]
        
        start_val = self.visit(intervalo[1])
        end_val = self.visit(intervalo[2])
        
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()

        self.add_code(var_name, "=", start_val)
        self.add_code("LABEL", label_start)
        
        temp_cond = self.new_temp()
        self.add_code(temp_cond, "=", var_name, "<=", end_val)
        
        self.add_code("IF_GOTO", temp_cond, label_body)
        self.add_code("GOTO", label_end)
        
        self.add_code("LABEL", label_body)
        for cmd in bloco:
            self.visit(cmd)
            
        self.add_code(var_name, "=", var_name, "+", 1)
        self.add_code("GOTO", label_start) 
        
        self.add_code("LABEL", label_end)
        
    def visit_binop(self, node):
        op = node[1]
        left_result = self.visit(node[2])
        right_result = self.visit(node[3])
        
        temp = self.new_temp()
        self.add_code(temp, "=", left_result, op, right_result)
        return temp

    def visit_unop(self, node):
        op = node[1]
        expr_result = self.visit(node[2])
        
        temp = self.new_temp()
        if op == '-':
             self.add_code(temp, "=", 0, "-", expr_result)
        
        return temp
        
    def visit_chamada_funcao(self, node):
        func_name = node[1]
        args = node[2]
        
        arg_results = []
        for arg in args:
            arg_results.append(self.visit(arg))
            
        for arg_r in arg_results:
            self.add_code("PUSH_PARAM", arg_r)
            
        temp_return = self.new_temp()
        self.add_code(temp_return, "=", "CALL", func_name, len(args))
        return temp_return

    def visit_num_inteiro(self, node):
        return node[1]
        
    def visit_num_real(self, node):
        return node[1]
        
    def visit_string(self, node):
        label = self.new_label()
        self.add_code("STRING_DEF", label, f'"{node[1]}"')
        return label
        
    def visit_boolean(self, node):
        return 1 if node[1] else 0
        
    def visit_id(self, node):
        var_name = node[1]
        
        # Adicionar a variável ao conjunto de variáveis declaradas se não existir
        if var_name not in self.declared_vars:
            self.declared_vars.add(var_name)
        
        return node[1]

# --- GERADOR DE CÓDIGO ASSEMBLY (ARMv7) ---
class ARMv7CodeGenerator:
    def __init__(self, declared_vars, function_code, array_sizes):
        self.asm_code = []
        self.data_section = []
        self.text_section = []
        self.declared_vars = declared_vars
        self.function_code = function_code
        self.array_sizes = array_sizes
        self.string_literals = {}
        self.float_literals = {}
        self.var_locations = {} 
        self.float_reg_map = {}
        self.next_stack_offset = -4
        self.next_float_reg = 0
        self.param_reg_count = 0

    def generate(self, c3e_code):
        # Inicializações...
        for var in self.declared_vars:
            if var not in self.var_locations:
                self.var_locations[var] = f"[fp, #{self.next_stack_offset}]"
                self.next_stack_offset -= 4
                
        self.add_string_literal("printf_int_format", "%d\\n")
        self.add_string_literal("printf_float_format", "%f\\n") 
        self.add_string_literal("printf_str_format", "%s\\n")
        self.add_string_literal("scanf_format", "%d")
        self.add_string_literal("newline", "\\n")

        # Adicionar funções utilitárias primeiro
        self.text_section.append("\n@ Funções utilitárias")
        self.text_section.append("int_to_string:")
        self.text_section.append("    push {r4-r7, lr}")
        self.text_section.append("    mov r4, r1")  # buffer
        self.text_section.append("    mov r5, #0")  # contador
        self.text_section.append("    mov r6, r0")  # número
        self.text_section.append("    cmp r6, #0")
        self.text_section.append("    bge itos_loop")
        self.text_section.append("    mvn r6, r6")  # negativo
        self.text_section.append("    add r6, r6, #1")
        self.text_section.append("itos_loop:")
        self.text_section.append("    mov r0, r6")
        self.text_section.append("    mov r1, #10")
        self.text_section.append("    bl divide")
        self.text_section.append("    add r0, r0, #48")  # converter para ASCII
        self.text_section.append("    strb r0, [r4, r5]")
        self.text_section.append("    add r5, r5, #1")
        self.text_section.append("    cmp r6, #0")
        self.text_section.append("    bne itos_loop")
        self.text_section.append("    mov r0, r5")  # retornar tamanho
        self.text_section.append("    pop {r4-r7, pc}")
        
        self.text_section.append("string_to_int:")
        self.text_section.append("    push {r4-r6, lr}")
        self.text_section.append("    mov r4, r0")  # tamanho
        self.text_section.append("    mov r5, r1")  # buffer
        self.text_section.append("    mov r6, #0")  # resultado
        self.text_section.append("    mov r2, #0")  # índice
        self.text_section.append("stoi_loop:")
        self.text_section.append("    ldrb r0, [r5, r2]")
        self.text_section.append("    sub r0, r0, #48")
        self.text_section.append("    mov r1, #10")
        self.text_section.append("    mul r6, r6, r1")
        self.text_section.append("    add r6, r6, r0")
        self.text_section.append("    add r2, r2, #1")
        self.text_section.append("    cmp r2, r4")
        self.text_section.append("    blt stoi_loop")
        self.text_section.append("    mov r0, r6")
        self.text_section.append("    pop {r4-r6, pc}")
        
        self.text_section.append("divide:")
        self.text_section.append("    mov r2, #0")
        self.text_section.append("divide_loop:")
        self.text_section.append("    cmp r0, r1")
        self.text_section.append("    blt divide_done")
        self.text_section.append("    sub r0, r0, r1")
        self.text_section.append("    add r2, r2, #1")
        self.text_section.append("    b divide_loop")
        self.text_section.append("divide_done:")
        self.text_section.append("    mov r0, r2")  # quociente em r0
        self.text_section.append("    mov r1, r0")  # resto em r1 (não usado)
        self.text_section.append("    bx lr")

        # Código principal
        self.text_section.append("\n.global main")
        self.text_section.append("main:")
        self.text_section.append("    push {fp, lr}")
        self.text_section.append("    mov fp, sp")
        stack_size = len(self.var_locations) * 4
        if stack_size > 0:
            self.text_section.append(f"    sub sp, sp, #{stack_size}")
        
        self.process_c3e_block(c3e_code)
        
        self.text_section.append("    mov r0, #0")
        if stack_size > 0:
            self.text_section.append(f"    add sp, sp, #{stack_size}")
        self.text_section.append("    pop {fp, pc}")
        
        for func_name, func_c3e in self.function_code.items():
            self.text_section.append(f"\n{func_name}:")
            self.text_section.append("    push {fp, lr}")
            self.text_section.append("    mov fp, sp")
            self.process_c3e_block(func_c3e)
            self.text_section.append("    pop {fp, pc}")

        self.asm_code.append(".data")
        self.asm_code.extend(self.data_section)
        self.asm_code.append("\n.text")
        self.asm_code.extend(self.text_section)
        
        return self.asm_code

    def process_c3e_block(self, c3e_block):
        self.param_reg_count = 0
        
        for line in c3e_block:
            parts = line.split()
            if not parts:
                continue
            
            cmd = parts[0]
            
            if cmd == "STRING_DEF":
                self.add_string_literal(parts[1], " ".join(parts[2:]).strip('"'))
                
            elif cmd == "START_PROGRAM" or cmd == "END_PROGRAM" or cmd == "FUNC_BEGIN" or cmd == "PARAM":
                continue
                
            elif cmd == "FUNC_END":
                self.text_section.append(f"    @ FUNC_END {parts[1]}")
                
            elif cmd == "RETURN":
                if len(parts) > 1:
                    self.load_to_reg(parts[1], "r0")
                self.text_section.append("    mov sp, fp")
                self.text_section.append("    pop {fp, pc}  @ Return")
                
            elif cmd == "LABEL":
                self.text_section.append(f"{parts[1]}:")
                
            elif cmd == "GOTO":
                self.text_section.append(f"    b {parts[1]}")
                
            elif cmd == "IF_GOTO": 
                self.load_to_reg(parts[1], "r0")
                self.text_section.append("    cmp r0, #1")
                self.text_section.append(f"    beq {parts[2]}")
                
            elif cmd == "WRITE":
                self.write_value(parts[1])
                
            elif cmd == "READ":
                self.read_value(parts[1])
                
            elif cmd == "PUSH_PARAM":
                reg = f"r{self.param_reg_count}"
                if self.param_reg_count < 4:
                    self.load_to_reg(parts[1], reg)
                else:
                    self.load_to_reg(parts[1], "r4")
                    self.text_section.append("    push {r4}")
                self.param_reg_count += 1
                
            elif cmd == "CALL":
                func_name = parts[1]
                num_params = int(parts[2])
                self.text_section.append(f"    bl {func_name}")
                if num_params > 4:
                    self.text_section.append(f"    add sp, sp, #{(num_params - 4) * 4}")
                self.param_reg_count = 0
                
            elif len(parts) == 3 and parts[1] == "=":
                dest = parts[0]
                src = parts[2]
                
                if src == "CALL":
                    self.store_from_reg(dest, "r0") 
                else:
                    self.load_to_reg(src, "r0")
                    self.store_from_reg(dest, "r0")
                    
            elif len(parts) == 5 and parts[1] == "=":
                dest = parts[0]
                op1 = parts[2]
                op = parts[3]
                op2 = parts[4]
                
                self.load_to_reg(op1, "r0")
                self.load_to_reg(op2, "r1")
                
                if op == "+": self.text_section.append("    add r0, r0, r1")
                elif op == "-": self.text_section.append("    sub r0, r0, r1")
                elif op == "*": self.text_section.append("    mul r0, r0, r1")
                elif op == "/": self.text_section.append("    sdiv r0, r0, r1")
                
                elif op in ('==', '!=', '<', '>', '<=', '>='):
                    self.text_section.append("    cmp r0, r1")
                    self.text_section.append("    mov r0, #0")
                    if op == "==": self.text_section.append("    moveq r0, #1")
                    elif op == "!=": self.text_section.append("    movne r0, #1")
                    elif op == "<": self.text_section.append("    movlt r0, #1")
                    elif op == ">": self.text_section.append("    movgt r0, #1")
                    elif op == "<=": self.text_section.append("    movle r0, #1")
                    elif op == ">=": self.text_section.append("    movge r0, #1")
                        
                self.store_from_reg(dest, "r0")
                
            else:
                self.text_section.append(f"    @ C3E não implementado: {line}")
                
    def get_var_location(self, var):
        if var not in self.var_locations:
            self.var_locations[var] = f"[fp, #{self.next_stack_offset}]"
            self.next_stack_offset -= 4
        return self.var_locations[var]

    def load_to_reg(self, src, reg):
        if src.replace('.', '', 1).isdigit() or (src.startswith('-') and src[1:].replace('.', '', 1).isdigit()):
            if "." in src:
                float_label = self.add_float_literal(src)
                self.text_section.append(f"    ldr {reg}, ={float_label}")
                self.text_section.append(f"    vldr s0, [{reg}]") 
            else:
                self.text_section.append(f"    mov {reg}, #{src}")
        elif src in self.var_locations:
            location = self.get_var_location(src)
            self.text_section.append(f"    ldr {reg}, {location}")
        elif src in self.string_literals:
            self.text_section.append(f"    ldr {reg}, ={src}")
            
    def store_from_reg(self, dest, reg):
        location = self.get_var_location(dest)
        self.text_section.append(f"    str {reg}, {location}")
        
    def write_value(self, src):
        if src in self.string_literals:
            # Syscall para escrever string
            self.load_to_reg(src, "r1")
            self.text_section.append("    mov r0, #1")  # stdout
            self.text_section.append("    mov r2, #13")  # tamanho da string (ajustar conforme necessário)
            self.text_section.append("    mov r7, #4")   # syscall write
            self.text_section.append("    svc #0")
        else:
            # Para números, converter para string primeiro (implementação simplificada)
            self.load_to_reg(src, "r0")
            # Converter número para string (implementação básica)
            self.text_section.append("    add r1, fp, #-64")  # buffer temporário
            self.text_section.append("    bl int_to_string")
            self.text_section.append("    mov r2, r0")  # tamanho
            self.text_section.append("    mov r0, #1")  # stdout
            self.text_section.append("    mov r7, #4")   # syscall write
            self.text_section.append("    svc #0")

    def read_value(self, dest):
        # Syscall para ler número
        location = self.get_var_location(dest)
        self.text_section.append("    sub r1, fp, #64")  # buffer temporário
        self.text_section.append("    mov r2, #16")      # tamanho do buffer
        self.text_section.append("    mov r0, #0")       # stdin
        self.text_section.append("    mov r7, #3")       # syscall read
        self.text_section.append("    svc #0")
        self.text_section.append("    bl string_to_int")
        self.store_from_reg(dest, "r0")

    def add_string_literal(self, label, text):
        if label not in self.string_literals:
            self.string_literals[label] = text
            self.data_section.append(f"{label}: .asciz \"{text}\"")
        return label
        
    def add_float_literal(self, value):
        label = f"float_{value.replace('.', '_').replace('-', 'n')}"
        if label not in self.float_literals:
            self.float_literals[label] = value
            self.data_section.append(f"{label}: .float {value}")
        return label

# --- FUNÇÃO PRINCIPAL DE COMPILAÇÃO ---
def compilar_codigo(codigo_fonte):
    lexer = MiniParLexer()
    parser = MiniParParser()
    semantic_analyzer = SemanticAnalyzer()
    c3e_generator = C3EGenerator()
    
    erros = ""
    saida_lexer = []
    
    try:
        tokens = list(lexer.tokenize(codigo_fonte))
        tokens_validos = []
        for tok in tokens:
            saida_lexer.append(f"Tipo: {tok.type}, Valor: '{tok.value}', Linha: {tok.lineno}")
            if tok.type == 'ERROR':
                erros += f"Erro Léxico: Caractere inesperado '{tok.value}' na linha {tok.lineno}\n"
            else:
                tokens_validos.append(tok)
        
        if erros: 
            return saida_lexer, "", [], [], erros

        ast = parser.parse(iter(tokens_validos))
        
        if parser.syntax_errors:
            erros += "\n".join(parser.syntax_errors)
            return saida_lexer, "Erro na Análise Sintática.", [], [], erros
        
        if not ast:
            erros += "Erro de Sintaxe: Falha desconhecida. Verifique a estrutura geral."
            return saida_lexer, "Erro na Análise Sintática.", [], [], erros
        
        saida_ast = formatar_ast(ast)
        
        semantic_analyzer.visit(ast)
        if semantic_analyzer.errors:
            erros += "\n".join(semantic_analyzer.errors)
            return saida_lexer, saida_ast, [], [], erros

        saida_c3e = c3e_generator.generate(ast)
        
        all_vars = (c3e_generator.declared_vars | 
                   set(semantic_analyzer.symbol_table.keys()) |
                   set(semantic_analyzer.channel_table.keys()))
        
        asm_generator = ARMv7CodeGenerator(all_vars, c3e_generator.function_code, c3e_generator.array_sizes)
        saida_asm = asm_generator.generate(saida_c3e)
        
        return saida_lexer, saida_ast, saida_c3e, saida_asm, erros

    except Exception as e:
        erros += f"Erro inesperado no compilador: {str(e)}\n"
        import traceback
        erros += traceback.format_exc()
        return saida_lexer, (saida_ast if 'saida_ast' in locals() else ""), \
               (saida_c3e if 'saida_c3e' in locals() else []), \
               (saida_asm if 'saida_asm' in locals() else []), \
               erros