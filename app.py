# app.py
from flask import Flask, render_template, request
from motor_compilador import compilar_codigo # Importa nossa função

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Dicionário para guardar os resultados da compilação
    resultados = None
    codigo_original = ""

    if request.method == 'POST':
        # Pega o código que o usuário digitou no formulário
        codigo_original = request.form['codigo']
        
        # Chama a função do nosso compilador
        tokens, msg_parser, codigo_c3e, erros = compilar_codigo(codigo_original)

        # Prepara o dicionário de resultados para enviar ao template
        resultados = {
            'tokens': tokens,
            'msg_parser': msg_parser,
            'codigo_c3e': codigo_c3e,
            'erros': erros
        }

    # Renderiza a página HTML, passando os resultados (se houver)
    return render_template('index.html', resultados=resultados, codigo_original=codigo_original)

if __name__ == '__main__':
    app.run(debug=True)