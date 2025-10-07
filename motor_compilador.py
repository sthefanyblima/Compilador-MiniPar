# motor_compilador.py
import sys
from sly import Lexer, Parser

# -----------------------------------------------------------------------------
#   ANALISADOR LÉXICO (LEXER)
# -----------------------------------------------------------------------------
class MiniParLexer(Lexer):
    tokens = {
        'PROGRAMA', 'FIM_PROGRAMA', 'DECLARE', 'INTEIRO', 'REAL', 'SE', 'ENTAO', 'SENAO',
        'FIM_SE', 'ENQUANTO', 'FACA', 'FIM_ENQUANTO', 'LEIA', 'ESCREVA',
        'ID', 'NUM_INTEIRO', 'NUM_REAL', 'ATRIBUICAO', 'OP_SOMA', 'OP_SUB', 'OP_MULT',
        'OP_DIV', 'OP_REL', 'ABRE_PARENTESES', 'FECHA_PARENTESES', 'DOIS_PONTOS', 'ERROR'
    }
    ignore = ' \t\r'
    ignore_comment = r'\{.*?\}'
    ATRIBUICAO      = r'='
    OP_SOMA         = r'\+'
    OP_SUB          = r'-'
    OP_MULT         = r'\*'
    OP_DIV          = r'/'
    OP_REL          = r'==|!=|<=|>=|<|>'
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

# -----------------------------------------------------------------------------
#   GERADOR DE CÓDIGO DE TRÊS ENDEREÇOS
# -----------------------------------------------------------------------------
class CodeGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
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
        raise Exception(f"Nenhum método de geração para o nó: {node[0]}")
    def _generate_programa(self, node):
        self.generate(node[1])
        self.generate(node[2])
    def _generate_lista_declaracoes(self, node):
        pass
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
        self.generate(node[2])
        self.emit(f"goto {fim_label}")
        self.emit(f"{senao_label}:")
        if node[3]: self.generate(node[3])
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
    def _generate_id(self, node):
        return node[1]
    def _generate_numero(self, node):
        return str(node[1])

# -----------------------------------------------------------------------------
#   ANALISADOR SINTÁTICO (PARSER)
# -----------------------------------------------------------------------------
class MiniParParser(Parser):
    tokens = MiniParLexer.tokens
    precedence = (('left', 'OP_SOMA', 'OP_SUB'),('left', 'OP_MULT', 'OP_DIV'),)
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
    @_('INTEIRO') # type: ignore
    def tipo(self, p):
        return 'inteiro'
    @_('REAL') # type: ignore
    def tipo(self, p):
        return 'real'
    @_('comando lista_comandos') # type: ignore
    def lista_comandos(self, p):
        return ('lista_comandos', [p.comando] + p.lista_comandos[1])
    @_('') # type: ignore
    def lista_comandos(self, p):
        return ('lista_comandos', [])
        
    # >>>>> CORREÇÃO IMPORTANTE AQUI <<<<<
    @_('atribuicao', 'condicional', 'laco', 'leitura', 'escrita') # type: ignore
    def comando(self, p):
        return p[0]
        
    @_('ID ATRIBUICAO expressao') # type: ignore
    def atribuicao(self, p):
        return ('atribuicao', p.ID, p.expressao)
    @_('LEIA ABRE_PARENTESES ID FECHA_PARENTESES') # type: ignore
    def leitura(self, p):
        return ('leia', p.ID)
    @_('ESCREVA ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def escrita(self, p):
        return ('escreva', p.expressao)
    @_('SE ABRE_PARENTESES expressao_logica FECHA_PARENTESES ENTAO lista_comandos senao_parte FIM_SE') # type: ignore
    def condicional(self, p):
        return ('se', p.expressao_logica, p.lista_comandos, p.senao_parte)
    @_('SENAO lista_comandos') # type: ignore
    def senao_parte(self, p):
        return p.lista_comandos
    @_('') # type: ignore
    def senao_parte(self, p):
        return None
    @_('ENQUANTO ABRE_PARENTESES expressao_logica FECHA_PARENTESES FACA lista_comandos FIM_ENQUANTO') # type: ignore
    def laco(self, p):
        return ('enquanto', p.expressao_logica, p.lista_comandos)
    @_('expressao OP_REL expressao') # type: ignore
    def expressao_logica(self, p):
        return ('expressao_logica', p.OP_REL, p.expressao0, p.expressao1)
    @_('expressao OP_SOMA expressao', # type: ignore
       'expressao OP_SUB expressao',
       'expressao OP_MULT expressao',
       'expressao OP_DIV expressao')
    def expressao(self, p):
        return ('binop', p[1], p.expressao0, p.expressao1)
    @_('ABRE_PARENTESES expressao FECHA_PARENTESES') # type: ignore
    def expressao(self, p):
        return p.expressao
    @_('ID') # type: ignore
    def expressao(self, p):
        return ('id', p.ID)
    @_('NUM_INTEIRO', 'NUM_REAL') # type: ignore
    def expressao(self, p):
        return ('numero', p[0])
    def error(self, p):
        pass

# --- FUNÇÃO PRINCIPAL DO COMPILADOR ---
def compilar_codigo(codigo_fonte):
    lexer = MiniParLexer()
    parser = MiniParParser()
    generator = CodeGenerator()

    saida_lexer = []
    saida_parser = ""
    saida_gerador = []
    erros = ""

    tokens = list(lexer.tokenize(codigo_fonte))
    
    tokens_validos = []
    error_found_in_lexer = False
    for tok in tokens:
        if tok.type == 'ERROR':
            error_found_in_lexer = True
            erros += f"Erro Léxico: Caractere ilegal '{tok.value}' na linha {tok.lineno}\n"
        else:
            tokens_validos.append(tok)
            saida_lexer.append(f"  Tipo: {tok.type}, Valor: '{tok.value}', Linha: {tok.lineno}")
    
    if error_found_in_lexer:
        return saida_lexer, saida_parser, saida_gerador, erros

    ast = parser.parse(iter(tokens_validos))
    if ast:
        saida_parser = "Análise sintática concluída com sucesso. AST gerada."
    else:
        erros += "Erro de Sintaxe: Verifique a estrutura do seu código (ex: falta 'fim_se' ou ';').\n"
        return saida_lexer, saida_parser, saida_gerador, erros

    generator.generate(ast)
    saida_gerador = generator.code
    
    return saida_lexer, saida_parser, saida_gerador, erros