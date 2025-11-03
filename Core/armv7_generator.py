#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Código Assembly ARMv7
"""

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
        self.next_stack_offset = 0  # Começar do topo da pilha (depois do sub sp)
        self.next_float_reg = 0
        self.param_reg_count = 0
        self.div_counter = 0  # Contador para labels únicos de divisão

    def generate(self, c3e_code):
        # Inicializações...
        # Primeiro calcular tamanho total necessário
        total_stack_size = 0
        for var in self.declared_vars:
            if var not in self.var_locations:
                if var in self.array_sizes:
                    array_size = self.array_sizes[var]['total_size'] * 4
                    total_stack_size += array_size
                else:
                    total_stack_size += 4
        
        # Agora alocar variáveis começando do topo da pilha (após sub sp)
        # fp aponta para antes do sub sp, então usamos offsets negativos
        current_offset = -total_stack_size
        for var in self.declared_vars:
            if var not in self.var_locations:
                if var in self.array_sizes:
                    # Array - alocar espaço na pilha
                    array_size = self.array_sizes[var]['total_size'] * 4
                    self.var_locations[var] = f"[fp, #{current_offset}]"
                    current_offset += array_size
                else:
                    # Variável simples
                    self.var_locations[var] = f"[fp, #{current_offset}]"
                    current_offset += 4
                
        # Strings de I/O removidas - CPUlator não precisa de formatos printf
        # Manter apenas strings literais do programa

        # Funções utilitárias removidas - usando printf/scanf da libc

        # Código principal - formato compatível com CPUlator (sem libc)
        self.text_section.append("\n.global _start")
        self.text_section.append("_start:")
        # Inicializar frame pointer
        self.text_section.append("    mov fp, sp")
        # Calcular tamanho total da pilha (incluindo arrays)
        stack_size = 0
        for var in self.var_locations:
            if var in self.array_sizes:
                array_size = self.array_sizes[var]['total_size'] * 4
                stack_size += array_size
            else:
                stack_size += 4
        
        if stack_size > 0:
            self.text_section.append(f"    sub sp, sp, #{stack_size}")
        
        self.process_c3e_block(c3e_code)
        
        # Terminar com loop infinito (compatível com CPUlator)
        if stack_size > 0:
            self.text_section.append(f"    add sp, sp, #{stack_size}")
        self.text_section.append("END:")
        self.text_section.append("    B .")  # Loop infinito - compatível com CPUlator
        
        for func_name, func_c3e in self.function_code.items():
            self.text_section.append(f"\n{func_name}:")
            self.text_section.append("    push {fp, lr}")
            self.text_section.append("    mov fp, sp")
            self.process_c3e_block(func_c3e)
            self.text_section.append("    pop {fp, pc}")

        # Organizar código: seção .text primeiro (para melhor controle de literal pool)
        codigo_final = []
        codigo_final.append(".text")
        codigo_final.extend(self.text_section)
        codigo_final.append("")
        codigo_final.append(".ltorg")  # Literal pool final
        codigo_final.append("")
        codigo_final.append(".data")
        codigo_final.extend(self.data_section)
        
        return codigo_final

    def process_c3e_block(self, c3e_block):
        self.param_reg_count = 0
        instruction_count = 0
        
        for line in c3e_block:
            # Inserir .ltorg a cada 25 instruções para manter literais dentro de 4KB
            if instruction_count > 0 and instruction_count % 25 == 0:
                self.text_section.append("    .ltorg")
            instruction_count += 1
            
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
                
            elif "ARRAY_ADDR" in parts:
                # Formato: dest = ARRAY_ADDR array_name index1 index2 ...
                if len(parts) >= 4 and parts[1] == "=" and parts[2] == "ARRAY_ADDR":
                    self.process_array_address(parts)
                elif cmd == "ARRAY_ADDR":
                    # Formato alternativo
                    self.process_array_address(parts)
                
            elif cmd == "ARRAY_STORE":
                self.process_array_store(parts)
                
            elif cmd == "ARRAY_LOAD":
                self.process_array_load(parts)
                
            elif len(parts) == 3 and parts[1] == "=":
                dest = parts[0]
                src = parts[2]
                
                if src == "CALL":
                    self.store_from_reg(dest, "r0")
                elif src == "ARRAY_LOAD":
                    # Formato: dest = ARRAY_LOAD addr_temp (não é o formato correto, deve ter 4 partes)
                    self.text_section.append(f"    @ Erro: ARRAY_LOAD sem endereço")
                else:
                    self.load_to_reg(src, "r0")
                    self.store_from_reg(dest, "r0")
            
            elif len(parts) == 4 and parts[1] == "=" and parts[2] == "ARRAY_LOAD":
                # Formato: dest = ARRAY_LOAD addr_temp
                dest = parts[0]
                addr_temp = parts[3]
                self.process_array_load([dest, "=", "ARRAY_LOAD", addr_temp])
                    
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
                elif op == "/":
                    # Divisão não suportada diretamente em ARM mode - usar algoritmo de divisão
                    # Gerar labels únicos para esta divisão
                    div_id = self.div_counter
                    self.div_counter += 1
                    
                    # Salvar registradores
                    self.text_section.append("    push {r2, r3, lr}")
                    # r0 = dividendo, r1 = divisor
                    # Verificar divisão por zero
                    self.text_section.append(f"    cmp r1, #0")
                    self.text_section.append(f"    beq div_zero_{div_id}")
                    # Inicializar quociente = 0
                    self.text_section.append(f"    mov r2, #0")
                    # Verificar sinais
                    self.text_section.append(f"    mov r3, #0")
                    # Se dividendo < 0, inverter sinal
                    self.text_section.append(f"    cmp r0, #0")
                    self.text_section.append(f"    rsblt r0, r0, #0")
                    self.text_section.append(f"    addlt r3, r3, #1")
                    # Se divisor < 0, inverter sinal
                    self.text_section.append(f"    cmp r1, #0")
                    self.text_section.append(f"    rsblt r1, r1, #0")
                    self.text_section.append(f"    eorlt r3, r3, #1")
                    # Loop de divisão: subtrair divisor do dividendo até ser menor
                    self.text_section.append(f"div_loop_{div_id}:")
                    self.text_section.append(f"    cmp r0, r1")
                    self.text_section.append(f"    blt div_done_{div_id}")
                    self.text_section.append(f"    sub r0, r0, r1")
                    self.text_section.append(f"    add r2, r2, #1")
                    self.text_section.append(f"    b div_loop_{div_id}")
                    self.text_section.append(f"div_done_{div_id}:")
                    # Restaurar sinal se necessário
                    self.text_section.append(f"    cmp r3, #0")
                    self.text_section.append(f"    beq div_pos_{div_id}")
                    self.text_section.append(f"    rsb r2, r2, #0")
                    self.text_section.append(f"div_pos_{div_id}:")
                    self.text_section.append(f"    mov r0, r2")
                    self.text_section.append(f"    pop {{r2, r3, lr}}")
                    self.text_section.append(f"    b div_exit_{div_id}")
                    self.text_section.append(f"div_zero_{div_id}:")
                    self.text_section.append(f"    mov r0, #0")
                    self.text_section.append(f"    pop {{r2, r3, lr}}")
                    self.text_section.append(f"div_exit_{div_id}:")
                
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
                
            elif cmd.startswith("ARRAY_"):
                # Processar comandos de array
                if cmd == "ARRAY_ADDR":
                    self.process_array_address(parts)
                elif cmd == "ARRAY_STORE":
                    self.process_array_store(parts)
                elif cmd == "ARRAY_LOAD":
                    self.process_array_load(parts)
                else:
                    self.text_section.append(f"    @ C3E não implementado: {line}")
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
                # Carregar valor float diretamente usando PC-relative
                # O assembler criará automaticamente uma entrada no literal pool
                self.text_section.append(f"    ldr {reg}, ={float_label}")
                # Nota: .ltorg será inserido periodicamente pelo gerador 
            else:
                self.text_section.append(f"    mov {reg}, #{src}")
        elif src in self.var_locations:
            location = self.get_var_location(src)
            # Se é um array, o location é o endereço base - carregar o endereço (não o valor)
            if src in self.array_sizes:
                # Array: calcular endereço base (adicionar fp ao offset)
                # Extrair offset da string [fp, #-128] ou [fp, #128]
                if '#-' in location:
                    offset_str = location.split('#-')[1].split(']')[0]
                    offset = int(offset_str)
                    # Usar sub para offset negativo
                    self.text_section.append(f"    sub {reg}, fp, #{offset}")
                elif '#' in location:
                    offset_str = location.split('#')[1].split(']')[0]
                    offset = int(offset_str)
                    self.text_section.append(f"    add {reg}, fp, #{offset}")
                else:
                    # Fallback - usar diretamente
                    self.text_section.append(f"    mov {reg}, fp")
            else:
                # Variável simples: carregar valor
                self.text_section.append(f"    ldr {reg}, {location}")
        elif src in self.string_literals:
            self.text_section.append(f"    ldr {reg}, ={src}")
        else:
            # Temporário - tentar carregar da localização (será criada se não existir)
            location = self.get_var_location(src)
            self.text_section.append(f"    ldr {reg}, {location}")
            
    def store_from_reg(self, dest, reg):
        location = self.get_var_location(dest)
        self.text_section.append(f"    str {reg}, {location}")
        
    def write_value(self, src):
        # Para compatibilidade com CPUlator, não fazer I/O (comentar ao invés de executar)
        # O CPUlator não tem libc, então removemos as chamadas printf
        # Os valores são apenas carregados mas não impressos
        self.text_section.append(f"    @ WRITE {src} - I/O removido para compatibilidade CPUlator")
        
        # Carregar o valor em um registrador (pode ser útil para debug)
        if src in self.string_literals:
            self.load_to_reg(src, "r0")
        elif src.replace('.', '', 1).isdigit() or (src.startswith('-') and src[1:].replace('.', '', 1).isdigit()):
            self.load_to_reg(src, "r0")
        else:
            self.load_to_reg(src, "r0")

    def read_value(self, dest):
        # Para compatibilidade com CPUlator, não fazer I/O
        # Inicializar variável com zero
        self.text_section.append(f"    @ READ {dest} - I/O removido, inicializando com 0")
        location = self.get_var_location(dest)
        self.text_section.append("    mov r0, #0")
        self.text_section.append(f"    str r0, {location}")
        
    def get_stack_offset_for_var(self, var):
        """Retorna o offset da variável na pilha"""
        if var in self.var_locations:
            # Extrair offset da string [fp, #-XX]
            loc_str = self.var_locations[var]
            if '#-' in loc_str:
                offset_str = loc_str.split('#-')[1].split(']')[0]
                return -int(offset_str)
        # Se não encontrado, criar novo
        offset = abs(self.next_stack_offset)
        self.var_locations[var] = f"[fp, #-{offset}]"
        self.next_stack_offset -= 4
        return -offset

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
        
    def process_array_address(self, parts):
        """Processa cálculo de endereço de array: temp = ARRAY_ADDR var index1 index2 ..."""
        if len(parts) < 4:
            return
            
        temp_dest = parts[0]
        # O formato pode ser: "t1 = ARRAY_ADDR arr 0" ou "ARRAY_ADDR arr 0"
        if parts[1] == "=" and parts[2] == "ARRAY_ADDR":
            # Formato: t1 = ARRAY_ADDR arr 0
            array_name = parts[3]
            indices = parts[4:]
        else:
            # Formato alternativo: ARRAY_ADDR arr 0
            array_name = parts[1]
            indices = parts[2:]
        
        if array_name not in self.array_sizes:
            self.text_section.append(f"    @ Erro: Array '{array_name}' não encontrado")
            return
            
        array_info = self.array_sizes[array_name]
        dimensions = array_info['dimensions']
        
        # Calcular endereço base do array
        self.load_to_reg(array_name, "r0")  # Endereço base
        
        if len(indices) == 1:
            # Array unidimensional
            self.load_to_reg(indices[0], "r1")
            self.text_section.append("    lsl r1, r1, #2")  # Multiplicar por 4 (tamanho de int)
            self.text_section.append("    add r0, r0, r1")
        else:
            # Array multidimensional
            # Para arrays 2D: offset = (i * cols + j) * 4
            # Para arrays 3D: offset = ((i * cols + j) * depth + k) * 4
            self.load_to_reg(indices[0], "r1")  # Primeiro índice
            
            # Multiplicar por dimensões subsequentes
            for i in range(1, len(dimensions)):
                self.text_section.append(f"    mov r2, #{dimensions[i]}")
                self.text_section.append("    mul r1, r1, r2")
                self.load_to_reg(indices[i], "r2")
                self.text_section.append("    add r1, r1, r2")
            
            # Multiplicar por 4 (tamanho do elemento)
            self.text_section.append("    lsl r1, r1, #2")
            self.text_section.append("    add r0, r0, r1")
        
        # Armazenar endereço calculado
        self.store_from_reg(temp_dest, "r0")
        
    def process_array_store(self, parts):
        """Processa armazenamento em array: ARRAY_STORE addr = value"""
        if len(parts) < 4:
            return
            
        addr_temp = parts[1]
        value = parts[3]
        
        # Carregar endereço e valor
        self.load_to_reg(addr_temp, "r0")
        self.load_to_reg(value, "r1")
        
        # Armazenar valor no endereço
        self.text_section.append("    str r1, [r0]")
        
    def process_array_load(self, parts):
        """Processa carregamento de array: temp = ARRAY_LOAD addr"""
        if len(parts) < 3:
            return
            
        temp_dest = parts[0]
        addr_temp = parts[2]
        
        # Carregar endereço
        self.load_to_reg(addr_temp, "r0")
        
        # Carregar valor do endereço
        self.text_section.append("    ldr r1, [r0]")
        
        # Armazenar valor
        self.store_from_reg(temp_dest, "r1")

# --- INTERPRETADOR PARA EXECUÇÃO DOS PROGRAMAS ---
