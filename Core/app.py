from flask import Flask, render_template, request, jsonify
import os
import sys

# Ajustar path para importar motor_compilador do mesmo diretório
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor_compilador import (MiniParLexer, MiniParParser, SemanticAnalyzer, 
                              C3EGenerator, formatar_ast, ARMv7CodeGenerator, 
                              MiniParInterpreter)

# Ajustar template_folder para apontar para o diretório templates no diretório pai
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(base_dir, 'templates')
app = Flask(__name__, template_folder=template_dir)

def compilar_codigo_completo(codigo_fonte):
    """Compila código e retorna todos os resultados incluindo AST"""
    lexer = MiniParLexer()
    parser = MiniParParser()
    semantic_analyzer = SemanticAnalyzer()
    c3e_generator = C3EGenerator()
    
    erros = ""
    saida_lexer = []
    ast = None
    
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
            return None, None, None, None, None, erros
        
        # Tentar parsing múltiplas vezes para garantir que tudo seja parseado
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
                return None, None, None, None, None, erros
        
        if not ast:
            erros += "Erro de Sintaxe: Falha desconhecida. Verifique a estrutura geral."
            return None, None, None, None, None, erros
        
        saida_ast = formatar_ast(ast)
        
        semantic_analyzer.visit(ast)
        if semantic_analyzer.errors:
            erros += "\n".join(semantic_analyzer.errors)
            return ast, saida_lexer, saida_ast, None, None, erros
        
        saida_c3e = c3e_generator.generate(ast)
        
        all_vars = (c3e_generator.declared_vars | 
                   set(semantic_analyzer.symbol_table.keys()) |
                   set(semantic_analyzer.channel_table.keys()))
        
        asm_generator = ARMv7CodeGenerator(all_vars, c3e_generator.function_code, c3e_generator.array_sizes)
        saida_asm = asm_generator.generate(saida_c3e)
        
        return ast, saida_lexer, saida_ast, saida_c3e, saida_asm, erros
        
    except Exception as e:
        import traceback
        erros += f"Erro inesperado no compilador: {str(e)}\n"
        erros += traceback.format_exc()
        return ast, (saida_lexer if 'saida_lexer' in locals() else []), \
               (saida_ast if 'saida_ast' in locals() else ""), \
               (saida_c3e if 'saida_c3e' in locals() else []), \
               (saida_asm if 'saida_asm' in locals() else []), \
               erros

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    codigo_original = ""

    if request.method == 'POST':
        codigo_original = request.form.get('codigo', '')
        
        try:
            ast, tokens, ast_formatada, codigo_c3e, codigo_asm, erros = compilar_codigo_completo(codigo_original)

            # Formatar tokens e C3E para exibição com quebras de linha
            tokens_formatados = "\n".join(tokens) if tokens else ""
            c3e_formatado = "\n".join(codigo_c3e) if codigo_c3e else ""
            asm_formatado = "\n".join(codigo_asm) if codigo_asm else ""

            resultados = {
                'tokens': tokens_formatados,
                'ast_formatada': ast_formatada,
                'codigo_c3e': c3e_formatado,
                'codigo_asm': asm_formatado,
                'erros': erros,
                'ast': ast  # Manter AST para execução
            }
        except Exception as e:
            resultados = {
                'erros': f"Erro durante a compilação: {str(e)}"
            }

    # Carrega exemplos de teste
    exemplos = {}
    import glob
    testes_dir = os.path.join(base_dir, 'Testes')
    for i in range(1, 9):
        # Primeiro tenta o arquivo básico
        arquivo = os.path.join(testes_dir, f'teste{i}.mp')
        if not os.path.exists(arquivo):
            # Se não existe, procura arquivos com sub-nomes
            padrao = os.path.join(testes_dir, f'teste{i}_*.mp')
            arquivos_encontrados = glob.glob(padrao)
            if arquivos_encontrados:
                arquivo = arquivos_encontrados[0]
        
        if os.path.exists(arquivo):
            # Extrai descrição do nome do arquivo (apenas o nome, sem caminho)
            nome_arquivo = os.path.basename(arquivo)  # Pega apenas o nome do arquivo
            nome_base = nome_arquivo.replace('.mp', '').replace('teste', '')
            descricao = ''
            if '_' in nome_base:
                partes = nome_base.split('_', 1)
                if len(partes) > 1:
                    descricao = partes[1].replace('_', ' ').title()
            
            nome_exibicao = f'Teste {i}'
            if descricao:
                nome_exibicao = f'Teste {i} - {descricao}'
            
            with open(arquivo, 'r', encoding='utf-8') as f:
                exemplos[nome_exibicao] = f.read()

    return render_template('index.html', resultados=resultados, codigo_original=codigo_original, exemplos=exemplos)

@app.route('/executar', methods=['POST'])
def executar():
    """Executa um programa MiniPar com entrada fornecida"""
    try:
        dados = request.get_json()
        codigo = dados.get('codigo', '')
        entrada = dados.get('entrada', '')
        
        # Compilar código
        ast, _, _, _, _, erros = compilar_codigo_completo(codigo)
        
        if erros:
            return jsonify({
                'sucesso': False,
                'saida': '',
                'erros': erros
            })
        
        if not ast:
            return jsonify({
                'sucesso': False,
                'saida': '',
                'erros': 'Erro: AST não gerada'
            })
        
        # Executar programa
        interpreter = MiniParInterpreter()
        saida = interpreter.execute(ast, entrada)
        
        return jsonify({
            'sucesso': True,
            'saida': saida,
            'erros': ''
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'sucesso': False,
            'saida': '',
            'erros': f"Erro na execução: {str(e)}\n{traceback.format_exc()}"
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001)