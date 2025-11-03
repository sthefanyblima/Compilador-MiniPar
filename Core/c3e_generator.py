#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Código de 3 Endereços (C3E)
"""

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
        
    def visit_declaracao_var_array(self, node):
        var_name = node[1]
        var_type = node[2].upper()
        dimensions = node[3]
        self.declared_vars.add(var_name)
        
        # Calcular tamanho total do array
        total_size = 1
        for dim in dimensions:
            total_size *= dim
        
        # Armazenar informações do array
        self.array_sizes[var_name] = {
            'dimensions': dimensions,
            'total_size': total_size,
            'type': var_type
        }
        
        return (node[0], var_name, var_type, dimensions)
        
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
        
    def visit_atribuicao_array(self, node):
        var_name = node[1]
        indices = node[2]
        expr_result = self.visit(node[3])
        
        # Processar índices
        index_results = []
        for index in indices:
            index_result = self.visit(index)
            index_results.append(index_result)
        
        # Gerar código para calcular endereço do array
        temp_addr = self.new_temp()
        self.add_code(temp_addr, "=", "ARRAY_ADDR", var_name, *index_results)
        
        # Atribuir valor ao array
        self.add_code("ARRAY_STORE", temp_addr, "=", expr_result)
        
        return (node[0], var_name, index_results, expr_result)
        
    def visit_acesso_array(self, node):
        var_name = node[1]
        indices = node[2]
        
        # Processar índices
        index_results = []
        for index in indices:
            index_result = self.visit(index)
            index_results.append(index_result)
        
        # Gerar código para calcular endereço e carregar valor
        temp_addr = self.new_temp()
        temp_value = self.new_temp()
        self.add_code(temp_addr, "=", "ARRAY_ADDR", var_name, *index_results)
        self.add_code(temp_value, "=", "ARRAY_LOAD", temp_addr)
        
        return temp_value

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
