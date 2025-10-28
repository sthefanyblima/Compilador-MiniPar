import sys
from sly import Lexer, Parser

# --- FUNÇÃO AUXILIAR PARA FORMATAR A AST ---
def formatar_ast(node, level=0):
    """
    Função recursiva para criar uma representação de string formatada da AST.
    """
    if node is None:
        return ""
    
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
#   CLASSES DO COMPILADOR
# ---------------------------------------
class MiniParLexer(Lexer):
    tokens = {
        'PROGRAMA', 'FIM_PROGRAMA', 'DECLARE', 'INTEIRO', 'REAL', 'SE', 'ENTAO', 'SENAO',
        'FIM_SE', 'ENQUANTO', 'FACA', 'FIM_ENQUANTO', 'LEIA', 'ESCREVA',
        'ID', 'NUM_INTEIRO', 'NUM_REAL', 'ATRIBUICAO', 'OP_SOMA', 'OP_SUB', 'OP_MULT',
        'OP_DIV', 'OP_REL', 'ABRE_PARENTESES', 'FECHA_PARENTESES', 'DOIS_PONTOS', 'STRING', 'ERROR'
    }
    
    ignore = ' \t\r'
    ignore_comment = r'\{[\s\S]*?\}'
    ignore_comment_c = r'//.*'
    ignore_comment_c_multi = r'/\*[\s\S]*?\*/'

    # Ordem dos tokens para evitar conflito léxico
    OP_REL          = r'==|!=|<=|>=|<|>'
    ATRIBUICAO      = r'='
    
    OP_SOMA         = r'\+'
    OP_SUB          = r'-'
    OP_MULT         = r'\*'
    OP_DIV          = r'/'
    ABRE_PARENTESES = r'\('
    FECHA_PARENTESES= r'\)'
    DOIS_PONTOS     = r':'
    
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['programa'] = 'PROGRAMA'
    ID['fim_programa'] = 'FIM_PROGRAMA'
    ID['declare'] = 'DECLARE'
    ID['inteiro'] = 'INTEIRO'
    ID['real'] = 'REAL'
    ID['se'] = 'SE'
    ID['entao'] = 'ENTAO'
    ID['senao'] = 'SENAO'
    ID['fim_se'] = 'FIM_SE'
    ID['enquanto'] = 'ENQUANTO'
    ID['faca'] = 'FACA'
    ID['fim_enquanto'] = 'FIM_ENQUANTO'
    ID['leia'] = 'LEIA'
    ID['escreva'] = 'ESCREVA'

    @_(r'\".*?\"') # type: ignore
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t
        
    @_(r'\d+\.\d+') # type: ignore
    def NUM_REAL(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+') # type: ignore
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

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def visit(self, node):
        if node is None: return
        method_name = f'visit_{node[0]}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        if isinstance(node, tuple):
            for item in node[1:]:
                self.visit(item)
    
    def visit_programa(self, node):
        self.symbol_table.clear()
        self.errors.clear()
        self.visit(node[1])
        self.visit(node[2])

    def visit_lista_declaracoes(self, node):
        for declaration in node[1]:
            self.visit(declaration)

    def visit_declaracao(self, node):
        var_type, var_name = node[1], node[2]
        if var_name in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' já foi declarada.")
        else:
            self.symbol_table[var_name] = var_type
    
    def visit_atribuicao(self, node):
        var_name = node[1]
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' não foi declarada antes do uso.")
        self.visit(node[2])

    def visit_leia(self, node):
        var_name = node[1]
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' em 'leia' não foi declarada.")

    def visit_id(self, node):
        var_name = node[1]
        if var_name not in self.symbol_table:
            self.errors.append(f"Erro Semântico: Variável '{var_name}' não foi declarada antes do uso.")
            
class MiniParParser(Parser):
    tokens = MiniParLexer.tokens

    precedence = (
        ('left', 'OP_SOMA', 'OP_SUB'),
        ('left', 'OP_MULT', 'OP_DIV'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.syntax_errors = []

    @_('PROGRAMA lista_declaracoes lista_comandos FIM_PROGRAMA') # type: ignore
    def programa(self, p):
        return ('programa', p.lista_declaracoes, p.lista_comandos)

    @_('declaracao lista_declaracoes') # type: ignore
    def lista_declaracoes(self, p):
        return ('lista_declaracoes', [p.declaracao] + p.lista_declaracoes[1])

    @_('') # type: ignore
    def lista_declaracoes(self, p):
        return ('lista_declaracoes', [])

    @_('DECLARE tipo DOIS_PONTOS ID') # type: ignore
    def declaracao(self, p):
        return ('declaracao', p.tipo, p.ID)

    @_('INTEIRO', 'REAL') # type: ignore
    def tipo(self, p):
        return p[0]

    @_('comando lista_comandos') # type: ignore
    def lista_comandos(self, p):
        return ('lista_comandos', [p.comando] + p.lista_comandos[1])

    @_('') # type: ignore
    def lista_comandos(self, p):
        return ('lista_comandos', [])

    @_('atribuicao', 'condicional', 'laco', 'leitura', 'escrita') # type: ignore
    def comando(self, p):
        return p[0]

    @_('ID ATRIBUICAO expressao') # type: ignore
    def atribuicao(self, p):
        return ('atribuicao', p.ID, p.expressao)

    @_('LEIA ABRE_PARENTESES ID FECHA_PARENTESES') # type: ignore
    def leitura(self, p):
        return ('leia', p.ID)

    @_('LEIA ID') # type: ignore
    def leitura(self, p):
        self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado '(' após 'leia'")
        return ('leia', p.ID)

    @_('LEIA ABRE_PARENTESES ID') # type: ignore
    def leitura(self, p):
        self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado ')' após identificador em 'leia'")
        return ('leia', p.ID)

    @_('ESCREVA ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def escrita(self, p):
        return ('escreva', p.expressao)

    @_('ESCREVA expressao') # type: ignore
    def escrita(self, p):
        self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado '(' após 'escreva'")
        return ('escreva', p.expressao)

    @_('ESCREVA ABRE_PARENTESES expressao') # type: ignore
    def escrita(self, p):
        self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado ')' após expressão em 'escreva'")
        return ('escreva', p.expressao)

    @_('ENQUANTO ABRE_PARENTESES expressao_logica FECHA_PARENTESES FACA lista_comandos FIM_ENQUANTO') # type: ignore
    def laco(self, p):
        return ('enquanto', p.expressao_logica, p.lista_comandos)

    # REGRAS PARA CONDICIONAL E SENAO

    @_('SE ABRE_PARENTESES expressao_logica FECHA_PARENTESES ENTAO lista_comandos FIM_SE') # type: ignore
    def condicional(self, p):
        return ('se', p.expressao_logica, p.lista_comandos, None)

    @_('SE ABRE_PARENTESES expressao_logica FECHA_PARENTESES ENTAO lista_comandos SENAO lista_comandos FIM_SE') # type: ignore
    def condicional(self, p):
        return ('se', p.expressao_logica, p.lista_comandos0, ('senao', p.lista_comandos1))

    @_('SE ABRE_PARENTESES expressao_logica FECHA_PARENTESES ENTAO lista_comandos SENAO condicional') # type: ignore
    def condicional(self, p):
        return ('se', p.expressao_logica, p.lista_comandos, ('senao_se', p.condicional))

    @_('expressao OP_REL expressao') # type: ignore
    def expressao_logica(self, p):
        return ('expressao_logica', p.OP_REL, p.expressao0, p.expressao1)

    @_('expressao OP_SOMA termo', # type: ignore
       'expressao OP_SUB termo')
    def expressao(self, p):
        return ('binop', p[1], p.expressao, p.termo)

    @_('termo') # type: ignore
    def expressao(self, p):
        return p.termo

    @_('termo OP_MULT fator', # type: ignore
       'termo OP_DIV fator')
    def termo(self, p):
        return ('binop', p[1], p.termo, p.fator)

    @_('fator') # type: ignore
    def termo(self, p):
        return p.fator

    @_('OP_SUB fator %prec UMINUS') # type: ignore
    def fator(self, p):
        return ('unop', '-', p.fator)

    @_('ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def fator(self, p):
        return p.expressao

    @_('ID') # type: ignore
    def fator(self, p):
        return ('id', p.ID)

    @_('NUM_INTEIRO', 'NUM_REAL') # type: ignore
    def fator(self, p):
        return ('numero', p[0])

    @_('STRING') # type: ignore
    def fator(self, p):
        return ('string', p.STRING)

    def error(self, p):
        if p:
            if p.type == 'LEIA':
                self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado '(' após 'leia'")
            elif p.type == 'ESCREVA':
                self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Esperado '(' após 'escreva'")
            else:
                self.syntax_errors.append(f"Erro de Sintaxe na linha {p.lineno}: Token inesperado '{p.value}' do tipo '{p.type}'")
        else:
            self.syntax_errors.append("Erro de Sintaxe: Fim de arquivo inesperado. Verifique se 'fim_programa' está presente.")

class C3EGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        self.declared_vars = set()

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        self.declared_vars.add(temp)
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, node):
        if node is None: return
        method_name = f'_generate_{node[0]}'
        method = getattr(self, method_name, self._generate_default)
        return method(node)

    def _generate_default(self, node):
        if isinstance(node, tuple):
             for item in node[1:]:
                if isinstance(item, (tuple, list)):
                    self.generate(item)

    def _generate_programa(self, node):
        self.generate(node[1])
        self.generate(node[2])

    def _generate_lista_declaracoes(self, node):
        for decl in node[1]: self.generate(decl)

    def _generate_declaracao(self, node):
        var_type, var_name = node[1], node[2]
        self.declared_vars.add(var_name)

    def _generate_lista_comandos(self, node):
        for cmd in node[1]: self.generate(cmd)

    def _generate_atribuicao(self, node):
        var_name = node[1]
        expr_result = self.generate(node[2])
        self.emit(f"{var_name} = {expr_result}")

    def _generate_leia(self, node):
        self.emit(f"leia {node[1]}")

    def _generate_escreva(self, node):
        expr_result = self.generate(node[1])
        self.emit(f"escreva {expr_result}")

    def _generate_se(self, node):
        cond_result = self.generate(node[1])
        senao_label = self.new_label()
        fim_label = self.new_label()
    
        self.emit(f"if_false {cond_result} goto {senao_label}")
        self.generate(node[2])  # Bloco 'entao'
    
        # Se há bloco senao, precisa pular para o fim após o então
        if node[3] is not None:
            self.emit(f"goto {fim_label}")
    
        self.emit(f"{senao_label}:")
    
        # Gerar o bloco senao
        if node[3] is not None:
            senao_type = node[3][0]
            if senao_type == 'senao':
                # senao simples
                self.generate(node[3][1])
            elif senao_type == 'senao_se':
                # senao se (encadeado)
                self.generate(node[3][1])
        
            self.emit(f"{fim_label}:")

    def _generate_enquanto(self, node):
        inicio_label = self.new_label()
        fim_label = self.new_label()
        self.emit(f"{inicio_label}:")
        cond_result = self.generate(node[1])
        self.emit(f"if_false {cond_result} goto {fim_label}")
        self.generate(node[2])
        self.emit(f"goto {inicio_label}")
        self.emit(f"{fim_label}:")

    def _generate_expressao_logica(self, node):
        left = self.generate(node[2])
        right = self.generate(node[3])
        op = node[1]
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {op} {right}")
        return temp

    def _generate_binop(self, node):
        left = self.generate(node[2])
        right = self.generate(node[3])
        op = node[1]
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {op} {right}")
        return temp

    def _generate_unop(self, node):
        expr_result = self.generate(node[2])
        temp = self.new_temp()
        self.emit(f"{temp} = 0 - {expr_result}")
        return temp

    def _generate_id(self, node):
        return node[1]

    def _generate_numero(self, node):
        return str(node[1])

    def _generate_string(self, node):
        return f'"{node[1]}"'

class ARMv7CodeGenerator:
    def __init__(self, declared_vars):
        self.declared_vars = declared_vars
        self.data_section = [".section .data"]
        self.text_section = [".section .text", ".global _start", "_start:"]
        self._setup_data_section()

    def _setup_data_section(self):
        for var in self.declared_vars:
            self.data_section.append(f"{var}: .word 0")

    def generate(self, tac_code):
        HEX_DISPLAY_ADDR = "0xFF200020"
        SWITCHES_ADDR = "0xFF200040"
        
        for line in tac_code:
            parts = line.split(maxsplit=1)
            command = parts[0]
            args = parts[1] if len(parts) > 1 else ""

            if command.endswith(':'):
                self.text_section.append(command)
            elif command == 'goto':
                self.text_section.append(f"    B {args}")
            elif command == 'if_false':
                cond, _, label = args.partition(' goto ')
                self._load_operand_to_reg(cond.strip(), 'r1')
                self.text_section.append(f"    CMP r1, #0")
                self.text_section.append(f"    BEQ {label.strip()}")
            
            elif command == 'leia':
                dest_var = args
                self.text_section.append(f"    LDR r0, ={SWITCHES_ADDR}")
                self.text_section.append(f"    LDR r1, [r0]")
                self.text_section.append(f"    LDR r2, ={dest_var}")
                self.text_section.append(f"    STR r1, [r2]")
            
            elif command == 'escreva':
                operand = args
                if operand.startswith('"') and operand.endswith('"'):
                    self.text_section.append(f"    @ Comando 'escreva' de string ignorado: {operand}")
                else:
                    self._load_operand_to_reg(operand, 'r1')
                    self.text_section.append(f"    LDR r0, ={HEX_DISPLAY_ADDR}")
                    self.text_section.append(f"    STR r1, [r0]")

            elif '=' in line:
                dest, expr = [p.strip() for p in line.split('=', 1)]
                expr_parts = expr.split()
                
                if len(expr_parts) == 1: 
                    self._load_operand_to_reg(expr_parts[0], 'r1')
                    self.text_section.append(f"    LDR r2, ={dest}")
                    self.text_section.append(f"    STR r1, [r2]")
                elif len(expr_parts) == 3: 
                    op1, op, op2 = expr_parts[0], expr_parts[1], expr_parts[2]
                    self._load_operand_to_reg(op1, 'r1')
                    self._load_operand_to_reg(op2, 'r2')
                    
                    op_map = {
                        '+': "ADD r3, r1, r2", '-': "SUB r3, r1, r2",
                        '*': "MUL r3, r1, r2", '/': "SDIV r3, r1, r2",
                        '==': "CMP r1, r2\n    MOVEQ r3, #1\n    MOVNE r3, #0",
                        '!=': "CMP r1, r2\n    MOVNE r3, #1\n    MOVEQ r3, #0",
                        '<': "CMP r1, r2\n    MOVLT r3, #1\n    MOVGE r3, #0",
                        '>': "CMP r1, r2\n    MOVGT r3, #1\n    MOVLE r3, #0",
                        '<=': "CMP r1, r2\n    MOVLE r3, #1\n    MOVGT r3, #0",
                        '>=': "CMP r1, r2\n    MOVGE r3, #1\n    MOVLT r3, #0"
                    }
                    if op in op_map:
                        self.text_section.append(f"    {op_map[op]}")
                        self.text_section.append(f"    LDR r4, ={dest}")
                        self.text_section.append(f"    STR r3, [r4]")
        return self.finalize()

    def _load_operand_to_reg(self, operand, reg):
        if operand.isdigit() or (operand.startswith('-') and operand[1:].isdigit()):
            self.text_section.append(f"    LDR {reg}, ={operand}")
        else:
            self.text_section.append(f"    LDR {reg}, ={operand}")
            self.text_section.append(f"    LDR {reg}, [{reg}]")

    def finalize(self):
        self.text_section.extend(["exit_program:", "    B exit_program"])
        return self.data_section + self.text_section

# --- FUNÇÃO PRINCIPAL DO COMPILADOR ---
def compilar_codigo(codigo_fonte):
    lexer = MiniParLexer()
    parser = MiniParParser()
    semantic_analyzer = SemanticAnalyzer()
    c3e_generator = C3EGenerator()
    
    saida_lexer, saida_ast, saida_c3e, saida_asm, erros = [], "", [], [], ""

    tokens = list(lexer.tokenize(codigo_fonte))
    tokens_validos = []
    for tok in tokens:
        if tok.type == 'ERROR':
            erros += f"Erro Léxico: Caractere ilegal '{tok.value}' na linha {tok.lineno}\n"
        else:
            tokens_validos.append(tok)
            saida_lexer.append(f"  Tipo: {tok.type}, Valor: '{tok.value}', Linha: {tok.lineno}")
    
    if erros: return saida_lexer, "", [], [], erros

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

    c3e_generator.generate(ast)
    saida_c3e = c3e_generator.code
    
    all_vars = c3e_generator.declared_vars.union(semantic_analyzer.symbol_table.keys())
    asm_generator = ARMv7CodeGenerator(all_vars)
    saida_asm = asm_generator.generate(saida_c3e)
    
    return saida_lexer, saida_ast, saida_c3e, saida_asm, erros