from flask import Flask, render_template, request
from motor_compilador import compilar_codigo

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    codigo_original = ""

    if request.method == 'POST':
        codigo_original = request.form['codigo']
        
        tokens, ast_formatada, codigo_c3e, codigo_asm, erros = compilar_codigo(codigo_original)

        resultados = {
            'tokens': tokens,
            'ast_formatada': ast_formatada, # Passa a AST para o template
            'codigo_c3e': codigo_c3e,
            'codigo_asm': codigo_asm,
            'erros': erros
        }

    return render_template('index.html', resultados=resultados, codigo_original=codigo_original)

if __name__ == '__main__':
    app.run(debug=True)