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
- **Geração de Executáveis:** compila código assembly em executáveis usando GCC/Clang.  
- **Interface Web (Flask):** insira o código MiniPar em uma área de texto e visualize tokens, AST, C3E, ARM e mensagens de erro diretamente no navegador.

---

## Estrutura do Projeto

```
compiladores/
│
├── motor_compilador.py        # Núcleo do compilador (lexer, parser, analisadores e geradores)
├── app.py                     # Aplicação Flask (interface web)
├── requirements.txt            # Dependências do projeto
├── README.md                  # Este arquivo
├── relatorio_compatibilidade.md # Relatório de compatibilidade dos testes
│
├── templates/
│   └── index.html             # Interface web renderizada pelo Flask
│
├── Scripts de compilação e teste:
│   ├── compilar_testes.py     # Compila todos os arquivos de teste
│   ├── testar_execucao.py     # Testa execução dos programas
│   ├── testar_todos.py         # Testa todos os testes principais
│   ├── testar_todos_testes.py # Testa todos os testes com detalhes
│   ├── verificar_todos_testes.py # Verifica compatibilidade CPUlator
│   └── exemplo_uso.py         # Exemplo de uso do compilador
│
├── Arquivos de teste (versões finais funcionais):
│   ├── teste1_servidor.mp      # Teste 1 - Servidor/Calculadora
│   ├── teste2_threads.mp       # Teste 2 - Threads/Paralelismo
│   ├── teste3_neuronio.mp      # Teste 3 - Neurônio
│   ├── teste4_XOR.mp           # Teste 4 - XOR
│   ├── teste5_rede_neural.mp   # Teste 5 - Rede Neural
│   ├── teste6_fatorial.mp      # Teste 6 - Fatorial
│   ├── teste7_fibonacci.mp     # Teste 7 - Fibonacci
│   └── teste8_quicksort.mp     # Teste 8 - Quicksort
│
├── Exemplos:
│   └── meu_programa.mp         # Exemplo simples de código MiniPar
│
└── Tema1-Projeto1-Compilador-MiniPar-2025-1-FINAL-okok.pdf  # Especificação do projeto
```

---

## Requisitos do Sistema

- **Python 3.10+**
- Sistema operacional: Windows, Linux ou WSL2 (recomendado para ARM)
- **GCC ou Clang** (opcional, mas necessário para gerar executáveis)
- Navegador moderno (Chrome, Edge, Firefox) - apenas para interface web

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
   cd compiladores
   python app.py
   ```
   
5. Abra o navegador e acesse:
   ```
   http://127.0.0.1:5001/
   ```

---

## Como Usar

### Interface Web

1. Cole o código MiniPar na caixa de texto da página principal.  
2. Clique em **"Compilar"**.  
3. A interface exibirá:
   - **Tokens gerados**
   - **AST formatada**
   - **Código de três endereços (C3E)**
   - **Código Assembly ARMv7**
   - **Mensagens de erro** (se houver)

### Gerar Executáveis

#### Compilar um arquivo específico:

```python
from motor_compilador import compilar_programa_minipar

with open('teste1.mp', 'r', encoding='utf-8') as f:
    codigo = f.read()

resultado = compilar_programa_minipar(
    codigo,
    nome_arquivo_saida='teste1',
    gerar_asm=True,
    gerar_executavel=True
)

if resultado['sucesso']:
    print(f"Executável gerado: {resultado['arquivo_executavel']}")
else:
    print(f"Erros: {resultado['erros']}")
```

#### Compilar todos os testes:

```bash
cd compiladores/Scripts
python compilar_testes.py
```

Este script compila todos os arquivos `teste*.mp` no diretório `Testes/` e gera executáveis correspondentes.

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

- **Erro "sly não encontrado"** → execute `pip install sly`.  
- **Erro "flask não encontrado"** → execute `pip install flask`.  
- **Porta 5000 ocupada** → execute `python app.py --port=5001`.  
- **Sem página HTML** → crie a pasta `templates/` e adicione `index.html` com o layout da interface.
- **Erro ao gerar executável** → instale GCC ou Clang:
  - **Linux/WSL:** `sudo apt-get install gcc` ou `sudo apt-get install clang`
  - **Windows:** Instale MinGW-w64 ou use WSL2
  - **macOS:** `xcode-select --install` (inclui Clang)
- **Assembly gerado mas executável não compila** → verifique se você tem um cross-compiler ARM instalado, ou ajuste `target_arch` na função `compilar_executavel` para sua arquitetura.

---

## Licença

Este projeto é de uso **educacional**, destinado ao estudo de **construção de compiladores e integração web com Flask**.
