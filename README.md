# Compilador MiniPar

Este projeto implementa um **compilador completo para a linguagem MiniPar**, com suporte a **análise léxica, sintática, semântica**, **geração de código intermediário (C3E)** e **geração de código ARMv7**.  
Além disso, ele oferece uma **interface web interativa** construída com **Flask**, permitindo compilar e visualizar os resultados diretamente no navegador.

---

## Funcionalidades Principais

- **Análise Léxica:** feita com a biblioteca `sly`, reconhecendo palavras-chave, identificadores, operadores e literais.  
- **Análise Sintática:** parser recursivo descendente que valida a estrutura gramatical dos programas MiniPar.  
- **Análise Semântica:** detecção de erros como variáveis não declaradas ou duplicadas.  
- **Geração de Código Intermediário (C3E):** cria uma representação de três endereços para o programa.  
- **Geração de Código ARMv7:** traduz o código intermediário para instruções em Assembly ARMv7.  
- **Interface Web (Flask):** insira o código MiniPar em uma área de texto e visualize tokens, AST, C3E, ARM e mensagens de erro diretamente no navegador.

---

## Estrutura do Projeto

```
 MiniPar-Compiler/
│
├── app.py                # Aplicação Flask (interface web)
├── motor_compilador.py   # Núcleo do compilador (lexer, parser, analisadores e geradores)
├── templates/
│   └── index.html        # Interface web renderizada pelo Flask
│
├── testinho.txt          # Programa de teste em MiniPar (exemplo de entrada)
├── meu_programa.mp       # Outro exemplo de código MiniPar
├── teste.mp              # Programa adicional de teste
│
└── README.md             # Este arquivo
```

---

## Requisitos do Sistema

- **Python 3.10+**
- Sistema operacional: Windows, Linux ou WSL2 (recomendado para ARM)
- Navegador moderno (Chrome, Edge, Firefox)

---

## Dependências

Instale os pacotes necessários com:

```bash
pip install flask sly
```

> **Flask** – cria e executa a interface web.  
> **Sly** – fornece as classes `Lexer` e `Parser` usadas para construir o compilador.

---

## Como Executar o Compilador

1. **Clone ou extraia** o projeto em uma pasta local.  
2. (Opcional) Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux / WSL
   venv\Scripts\activate     # Windows
   ```
3. **Instale as dependências**:
   ```bash
   pip install flask sly
   ```
4. **Execute a aplicação Flask**:
   ```bash
   python app.py
   ```
5. Abra o navegador e acesse:
   ```
   http://127.0.0.1:5000/
   ```

---

## Como Usar

1. Cole o código MiniPar na caixa de texto da página principal.  
2. Clique em **“Compilar”**.  
3. A interface exibirá:
   - **Tokens gerados**
   - **AST formatada**
   - **Código de três endereços (C3E)**
   - **Código Assembly ARMv7**
   - **Mensagens de erro** (se houver)

---

## Exemplo de Código MiniPar

```minipar
programa
    declare inteiro: x
    declare inteiro: y
    x = 5
    y = x + 2
    escreva(y)
fim_programa
```

---

## Possíveis Problemas

- **Erro “sly não encontrado”** → execute `pip install sly`.  
- **Erro “flask não encontrado”** → execute `pip install flask`.  
- **Porta 5000 ocupada** → execute `python app.py --port=5001`.  
- **Sem página HTML** → crie a pasta `templates/` e adicione `index.html` com o layout da interface.

---

## Licença

Este projeto é de uso **educacional**, destinado ao estudo de **construção de compiladores e integração web com Flask**.
