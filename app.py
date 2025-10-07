# app.py
from flask import Flask, render_template, request
from motor_compilador import compilar_codigo

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = None
    codigo_original = ""

    if request.method == 'POST':
        codigo_original = request.form['codigo']
        
        # Chama a função do compilador, esperando 5 valores de retorno
        tokens, msg_parser, codigo_c3e, codigo_asm, erros = compilar_codigo(codigo_original)

        resultados = {
            'tokens': tokens,
            'msg_parser': msg_parser,
            'codigo_c3e': codigo_c3e,
            'codigo_asm': codigo_asm,
            'erros': erros
        }

    return render_template('index.html', resultados=resultados, codigo_original=codigo_original)

if __name__ == '__main__':
    app.run(debug=True)