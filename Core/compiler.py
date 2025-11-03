#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Funções principais de compilação
"""

import os
import subprocess
import platform

try:
    from .lexer import MiniParLexer
    from .parser import MiniParParser
    from .semantic import SemanticAnalyzer
    from .c3e_generator import C3EGenerator
    from .armv7_generator import ARMv7CodeGenerator
    from .utils import formatar_ast
except ImportError:
    from lexer import MiniParLexer
    from parser import MiniParParser
    from semantic import SemanticAnalyzer
    from c3e_generator import C3EGenerator
    from armv7_generator import ARMv7CodeGenerator
    from utils import formatar_ast

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

        # Tentar parsing múltiplas vezes para garantir que tudo seja parseado
        # Isso ajuda com conflitos shift/reduce que podem fazer o parser parar cedo
        ast = None
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                parser.syntax_errors = []  # Limpar erros anteriores
                ast = parser.parse(iter(tokens_validos))
                # Verificar se parseou tudo - se não há erros críticos, aceitar
                if ast and len(parser.syntax_errors) == 0:
                    break
                # Se há erros mas AST foi gerada parcialmente, verificar se é suficiente
                if ast and attempt < max_attempts - 1:
                    # Tentar novamente com tokens validos
                    tokens_validos = [t for t in tokens if t.type != 'ERROR']
            except Exception:
                if attempt < max_attempts - 1:
                    tokens_validos = [t for t in tokens if t.type != 'ERROR']
                    continue
                break
        
        if parser.syntax_errors:
            # Apenas reportar erros se não tivermos uma AST válida
            if not ast:
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

# --- FUNÇÕES PARA GERAR EXECUTÁVEIS ---
def salvar_assembly(codigo_asm, nome_arquivo="output.s"):
    """Salva o código assembly gerado em um arquivo .s"""
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            if isinstance(codigo_asm, list):
                f.write('\n'.join(codigo_asm))
            else:
                f.write(str(codigo_asm))
        return True, f"Assembly salvo em {nome_arquivo}"
    except Exception as e:
        return False, f"Erro ao salvar assembly: {str(e)}"

def compilar_executavel(arquivo_asm, nome_executavel=None, target_arch="arm"):
    """
    Compila o código assembly em um executável.
    
    Args:
        arquivo_asm: Caminho para o arquivo .s
        nome_executavel: Nome do executável de saída (opcional)
        target_arch: Arquitetura alvo ("arm", "x86", "x64")
    
    Returns:
        (success, message): Tupla indicando sucesso e mensagem
    """
    import os
    import subprocess
    import platform
    
    if nome_executavel is None:
        nome_executavel = arquivo_asm.replace('.s', '.exe' if platform.system() == 'Windows' else '')
    
    # Detectar o sistema e escolher o compilador apropriado
    sistema = platform.system()
    
    # Tentar encontrar gcc ou clang
    compiladores = []
    
    if target_arch == "arm":
        # Para ARM, tentar diferentes variantes
        if sistema == "Linux" or "Linux" in platform.platform():
            compiladores = ['arm-linux-gnueabihf-gcc', 'arm-none-eabi-gcc', 'gcc']
        elif sistema == "Darwin":  # macOS
            compiladores = ['clang']
        else:  # Windows
            compiladores = ['gcc', 'arm-none-eabi-gcc']
    else:
        # Para x86/x64, usar gcc padrão
        compiladores = ['gcc', 'clang']
    
    compilador = None
    for cmd in compiladores:
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode == 0 or 'gcc' in cmd or 'clang' in cmd:
                compilador = cmd
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if compilador is None:
        # Tentar usar gcc diretamente
        compilador = 'gcc'
    
    # Montar comando de compilação
    if target_arch == "arm":
        # Para ARM, pode precisar de flags especiais
        if 'arm' in compilador:
            cmd = [compilador, '-o', nome_executavel, arquivo_asm, '-static']
        else:
            # GCC padrão - pode não funcionar para ARM sem cross-compiler
            # Neste caso, tentar compilar como x86/x64 se possível
            cmd = [compilador, '-o', nome_executavel, arquivo_asm]
    else:
        cmd = [compilador, '-o', nome_executavel, arquivo_asm]
    
    try:
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0:
            if os.path.exists(nome_executavel):
                return True, f"Executável gerado com sucesso: {nome_executavel}"
            else:
                return False, f"Compilador executou mas executável não foi criado. Erros: {result.stderr}"
        else:
            return False, f"Erro na compilação: {result.stderr or result.stdout}"
            
    except FileNotFoundError:
        return False, f"Compilador '{compilador}' não encontrado. Por favor, instale GCC ou Clang."
    except subprocess.TimeoutExpired:
        return False, "Timeout durante a compilação."
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"

def compilar_programa_minipar(codigo_fonte, nome_arquivo_saida=None, gerar_asm=True, gerar_executavel=True):
    """
    Compila um programa MiniPar e gera arquivos assembly e executável.
    
    Args:
        codigo_fonte: Código fonte em MiniPar
        nome_arquivo_saida: Nome base para os arquivos de saída (sem extensão)
        gerar_asm: Se True, salva arquivo .s
        gerar_executavel: Se True, tenta compilar executável
    
    Returns:
        Dicionário com resultados da compilação
    """
    if nome_arquivo_saida is None:
        nome_arquivo_saida = "programa_compilado"
    
    # Compilar o código
    tokens, ast, c3e, asm, erros = compilar_codigo(codigo_fonte)
    
    resultado = {
        'sucesso': len(erros) == 0,
        'erros': erros,
        'tokens': tokens,
        'ast': ast,
        'c3e': c3e,
        'asm': asm
    }
    
    if len(erros) > 0:
        return resultado
    
    # Salvar assembly
    if gerar_asm:
        arquivo_asm = f"{nome_arquivo_saida}.s"
        sucesso_asm, msg_asm = salvar_assembly(asm, arquivo_asm)
        resultado['arquivo_asm'] = arquivo_asm if sucesso_asm else None
        resultado['msg_asm'] = msg_asm
        
        if sucesso_asm and gerar_executavel:
            # Tentar compilar executável
            sucesso_exe, msg_exe = compilar_executavel(arquivo_asm, f"{nome_arquivo_saida}")
            resultado['arquivo_executavel'] = f"{nome_arquivo_saida}" if sucesso_exe else None
            resultado['msg_executavel'] = msg_exe
        else:
            resultado['arquivo_executavel'] = None
            resultado['msg_executavel'] = "Assembly não foi salvo ou geração desabilitada"
    else:
        resultado['arquivo_asm'] = None
        resultado['msg_asm'] = "Geração de assembly desabilitada"
        resultado['arquivo_executavel'] = None
        resultado['msg_executavel'] = "Geração de executável desabilitada"
    
    return resultado