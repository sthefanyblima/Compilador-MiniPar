from flask import Flask, render_template, request
from motor_compilador import compilar_codigo
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    codigo_original = ""

    if request.method == 'POST':
        codigo_original = request.form['codigo']
        
        try:
            tokens, ast_formatada, codigo_c3e, codigo_asm, erros = compilar_codigo(codigo_original)

            # Formatar tokens e C3E para exibição com quebras de linha
            tokens_formatados = "\n".join(tokens) if tokens else ""
            c3e_formatado = "\n".join(codigo_c3e) if codigo_c3e else ""
            asm_formatado = "\n".join(codigo_asm) if codigo_asm else ""

            resultados = {
                'tokens': tokens_formatados,
                'ast_formatada': ast_formatada,
                'codigo_c3e': c3e_formatado,
                'codigo_asm': asm_formatado,
                'erros': erros
            }
        except Exception as e:
            resultados = {
                'erros': f"Erro durante a compilação: {str(e)}"
            }

    # Carrega exemplos de teste
    exemplos = {}
    for i in range(1, 9):
        arquivo = f'teste{i}.mp'
        if os.path.exists(arquivo):
            with open(arquivo, 'r', encoding='utf-8') as f:
                exemplos[f'Teste {i}'] = f.read()

    return render_template('index.html', resultados=resultados, codigo_original=codigo_original, exemplos=exemplos)

if __name__ == '__main__':
    app.run(debug=True, port=5001)