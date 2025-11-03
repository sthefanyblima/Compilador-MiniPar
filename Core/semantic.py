#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisador Semântico do compilador MiniPar
"""

# --- ANALISADOR SEMÂNTICO ---
class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.channel_table = {}
        self.function_table = {}
        self.current_function_type = None
        self.errors = []
        self.array_dims = {}  # Armazenar dimensões dos arrays
        self.declared_vars = set() 
        
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
